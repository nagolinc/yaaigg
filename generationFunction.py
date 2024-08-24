import os
import google.generativeai as genai
import json
import fal_client

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

from google.generativeai.types import HarmCategory, HarmBlockThreshold

from comfy import generate_comfy

# create a lock
import threading

gemini_lock = threading.Lock()


def describeReward(keywords, system_prompt_file="items_system_prompt.txt",nTries=3):

    if textGenerator == "openAI":
        for i in range(nTries):
            output = describeReward_openAI(keywords, system_prompt_file=system_prompt_file)
            
            try:
                #validate output is json and has 'caption' and 'name' keys
                output_dict=json.loads(output)
                assert 'caption' in output_dict
                assert 'name' in output_dict
                return output
            except:
                print("retrying openAI",output)
        
        print("failed to generate with openAI",output)
        #return a default response
        return json.dumps({"caption":"A mysterious item","name":"Mystery Item"})
        
        
    elif textGenerator == "gemini":
        return describeReward_gemini(keywords, system_prompt_file=system_prompt_file)


from openai import OpenAI


def describeReward_openAI(keywords, system_prompt_file="items_system_prompt.txt"):
    client = OpenAI()

    with open(system_prompt_file) as f:
        system_prompt = f.read()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "text", "text": ",".join(keywords)}]},
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json_object"},
    )
    
    #print("response",response)
    
    output_text=response.choices[0].message.content
    return output_text


def describeReward_gemini(keywords, system_prompt_file="items_system_prompt.txt"):
    with gemini_lock:
        # Create the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json",
        }

        with open(system_prompt_file) as f:
            system_prompt = f.read()

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction=system_prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
        )

        chat_session = model.start_chat(history=[])

        response = chat_session.send_message(",".join(keywords))

        return response.text


from datetime import datetime
import re
import requests

imageGenerator = "comfy"
comfy_yaml = "comfy.yaml"
textGenerator = "openAI"


def generateImage(prompt, suffix=""):

    if imageGenerator == "comfy":
        print("generating comfy image with prompt", prompt)
        filename = generate_comfy(prompt+suffix, yaml_file=comfy_yaml, width=512, height=512)
        print("generated image, filename", filename)
        # prepent with / if not already there
        if filename[0] != "/":
            filename = "/" + filename

        return filename

    elif imageGenerator == "fal":
        return generateImage_fal(prompt)


def generateImage_fal(prompt):
    """
    response is  formatted like
    {'images': [{'url': 'https://fal.media/files/elephant/zJ4leUdxnMxOzOL6kE_8S.png', 'width': 1024, 'height': 768, 'content_type': 'image/jpeg'}], 'timings': {'inference': 0.36287203000392765}, 'seed': 3171017014, 'has_nsfw_concepts': [False], 'prompt': 'Extreme close-up of a single tiger eye, direct frontal view. Detailed iris and pupil. Sharp focus on eye texture and color. Natural lighting to capture authentic eye shine and depth. The word "FLUX" is painted over it in big, white brush strokes with visible texture.'}
    """

    handler = fal_client.submit(
        "fal-ai/flux/schnell",
        arguments={"prompt": prompt, "enable_safety_checker": False},
    )

    result = handler.get()
    # print(result)

    # pareses the json response
    url = result["images"][0]["url"]

    # make folder if not exist
    os.makedirs("static/samples", exist_ok=True)

    # turn the cpation into a filename by removing character othern than a-z0-9
    # and prepending datetime
    filename = (
        datetime.now().strftime("%Y%m%d%H%M%S")
        + "-"
        + re.sub(r"[^A-Za-z0-9]", "_", prompt.lower())[:100]
        + ".png"
    )
    # fecth and save to ./static/samples folder
    with open(f"./static/samples/{filename}", "wb") as f:
        f.write(requests.get(url).content)
    return "/static/samples/" + filename


import random


def randomKeywords(
    filenames=["words/elements.txt", "words/animals.txt", "words/items.txt"],
    starRating=1,
    level=1,
    falloff=0.8
):
    keywords = []
    
    
    #weights should look like 4*[1], 0.5, 0.25, .. only reversed
    weights=[1,1,1,1]+[falloff**i for i in range(level-1)]
    weights=weights[::-1]
    
    for filename in filenames:
        with open(filename) as f:
            these_keywords = f.read().splitlines()[:level+3]
            
            trimmed_weights=weights[:len(these_keywords)]
            
            #print("DEBUG",weights,these_keywords,len(these_keywords),len(weights))
            
            #weighted random
            keyword = random.choices(these_keywords, weights=trimmed_weights)[0]
            keywords.append(keyword)
    keywords.append(str(starRating) + "star")
    return keywords


from PIL import Image
import json
import random




def generateThumbnail(filename):
    with Image.open(filename) as img:
        img.thumbnail(
            (100, 100)
        )  # Resize to 100x100 or smaller, maintaining aspect ratio
        thumbnail_filename = filename.replace(
            ".png", "_thumbnail.png"
        )  # Adjust extension as needed
        img.save(thumbnail_filename)
    return thumbnail_filename



keyword_mapping={}


import yaml

def setupKeywordMapping(yaml_file):
    global keyword_mapping
    with open(yaml_file) as f:
        keyword_mapping = yaml.safe_load(open(yaml_file).read())
        
        
#datetime-random 64 bits, bas64 encoded    
def generateId():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")+str(random.getrandbits(64)).encode('utf-8').hex()[:16]


def getRandomItem(starRating,level=1):
    #filenames=["words/elements.txt", "words/animals.txt", "words/items.txt","words/classes.txt"]
    filenames=[keyword_mapping['elements'],keyword_mapping['animals'],keyword_mapping['items'],keyword_mapping['classes']]
    keywords = randomKeywords(filenames,starRating=starRating,level=level)
    print("here0")
    reward = json.loads(describeReward(keywords))
    print("here1", reward)
    caption = reward["caption"]
    filename = generateImage(caption,suffix=keyword_mapping['prompt_suffix'])
    reward["filename"] = filename
    
    reward['id']=generateId()
    
    
    reward['level']=level
    reward['starRating']=starRating
    reward['element']=keywords[0]
    reward['animal']=keywords[1]
    reward['itemType']=keywords[2]
    reward['class']=keywords[3]

    # Generate thumbnail
    thumbnail_filename = generateThumbnail("." + filename)
    # remove leading "." from thumbnail_filename
    thumbnail_filename = thumbnail_filename[1:]
    reward["thumbnail_filename"] = thumbnail_filename

    return reward




def generateNPC(starRating,level=1):
    #keyword_files = [
    #    "words/genders.txt",
    #    "words/elements.txt",
    #    "words/races.txt",
    #    "words/classes.txt",
    #]
    keyword_files=[keyword_mapping['genders'],keyword_mapping['elements'],keyword_mapping['races'],keyword_mapping['classes']]
    keywords = randomKeywords(filenames=keyword_files, starRating=starRating,level=level)
    print(keywords)
    npc = json.loads(
        describeReward(keywords, system_prompt_file="npc_system_prompt.txt")
    )
    caption = npc["caption"]
    filename = generateImage(caption,suffix=keyword_mapping['prompt_suffix'])
    npc["filename"] = filename
    
    npc['id']=generateId()
    
    npc['level']=level
    npc['starRating']=starRating
    npc['gender']=keywords[0]
    npc['element']=keywords[1]
    npc['race']=keywords[2]
    npc['class']=keywords[3]

    # Generate thumbnail
    thumbnail_filename = generateThumbnail("." + filename)
    # remove leading "." from thumbnail_filename
    thumbnail_filename = thumbnail_filename[1:]
    npc["thumbnail_filename"] = thumbnail_filename

    return npc


def generateBuilding(starRating,level=1):
    #keyword_files = ["words/elements.txt", "words/races.txt", "words/buildings.txt"]
    keyword_files=[keyword_mapping['elements'],keyword_mapping['races'],keyword_mapping['buildings']]
    keywords = randomKeywords(filenames=keyword_files, starRating=starRating,level=level)
    building = json.loads(
        describeReward(keywords, system_prompt_file="building_system_prompt.txt")
    )
    caption = building["caption"]
    filename = generateImage(caption,suffix=keyword_mapping['prompt_suffix'])
    building["filename"] = filename
    
    building['id']=generateId()
    
    
    building['level']=level
    building['starRating']=starRating
    building['element']=keywords[0]
    building['race']=keywords[1]
    building['buildingType']=keywords[2]

    # Generate thumbnail
    thumbnail_filename = generateThumbnail("." + filename)
    # remove leading "." from thumbnail_filename
    thumbnail_filename = thumbnail_filename[1:]
    building["thumbnail_filename"] = thumbnail_filename

    return building


def generateQuest(starRating,level=1):
    #keyword_files = ["words/questlines.txt", "words/monsters.txt", "words/settings.txt"]
    keyword_files=[keyword_mapping['questlines'],keyword_mapping['monsters'],keyword_mapping['settings']]
    keywords = randomKeywords(filenames=keyword_files, starRating=starRating,level=level)
    
    
    #_requirement=["words/classes.txt","words/races.txt","words/elements.txt"]
    _requirement=[keyword_mapping['classes'],keyword_mapping['races'],keyword_mapping['elements']]
    requirement=randomKeywords(_requirement,level=level)
    
    if random.random()>0.33:
        #quest['required_class']=requirement[0]
        requirement_name='required_class'
        requirement_value=requirement[0]
        keywords.append("required class: "+requirement[0])
    elif random.random()>0.5:
        #quest['required_race']=requirement[1]
        requirement_name="required_race"
        requirement_value=requirement[1]
        keywords.append("required race: "+requirement[1])
    else:
        #quest['required_element']=requirement[2]
        requirement_name="required_element"
        requirement_value=requirement[2]
        keywords.append("required element: "+requirement[2])
    
    quest = json.loads(
        describeReward(keywords, system_prompt_file="quest_system_prompt.txt")
    )
    
    quest[requirement_name]=requirement_value
    
    caption = quest["caption"]
    filename = generateImage(caption,suffix=keyword_mapping['prompt_suffix'])
    quest["filename"] = filename
    
    quest['level']=level
    
    quest['id']=generateId()
    
    # Generate thumbnail
    thumbnail_filename = generateThumbnail("." + filename)
    # remove leading "." from thumbnail_filename
    thumbnail_filename = thumbnail_filename[1:]
    quest["thumbnail_filename"] = thumbnail_filename

    return quest




if __name__ == "__main__":
    setupKeywordMapping("keyword_mapping.yaml")
    for i in range(1, 6):
        print(generateNPC(i))
        # print(generateQuest(i))
