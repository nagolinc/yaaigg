import os
import google.generativeai as genai
import json
import fal_client

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

from google.generativeai.types import HarmCategory, HarmBlockThreshold


def describeReward(keywords,system_prompt_file="items_system_prompt.txt"):
    # Create the model
    generation_config = {
      "temperature": 1,
      "top_p": 0.95,
      "top_k": 64,
      "max_output_tokens": 8192,
      "response_mime_type": "application/json",
    }

    with open(system_prompt_file) as f:
        system_prompt=f.read()

    model = genai.GenerativeModel(
      model_name="gemini-1.5-flash",
      generation_config=generation_config,
      system_instruction=system_prompt,
      safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory. HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
    )

    chat_session = model.start_chat(
      history=[]
    )

    response = chat_session.send_message(",".join(keywords))

    return response.text


from datetime import datetime
import re
import requests
def generateImage(prompt):


    '''
    response is  formatted like
    {'images': [{'url': 'https://fal.media/files/elephant/zJ4leUdxnMxOzOL6kE_8S.png', 'width': 1024, 'height': 768, 'content_type': 'image/jpeg'}], 'timings': {'inference': 0.36287203000392765}, 'seed': 3171017014, 'has_nsfw_concepts': [False], 'prompt': 'Extreme close-up of a single tiger eye, direct frontal view. Detailed iris and pupil. Sharp focus on eye texture and color. Natural lighting to capture authentic eye shine and depth. The word "FLUX" is painted over it in big, white brush strokes with visible texture.'}
    '''

    handler = fal_client.submit(
        "fal-ai/flux/schnell",
        arguments={
            "prompt": prompt,
            "enable_safety_checker": False
        },
    )

    result = handler.get()
    #print(result)

    #pareses the json response
    url = result["images"][0]["url"]

    #make folder if not exist
    os.makedirs("static/samples", exist_ok=True)

    #turn the cpation into a filename by removing character othern than a-z0-9
    # and prepending datetime
    filename = datetime.now().strftime("%Y%m%d%H%M%S") +"-"+ re.sub(r"[^A-Za-z0-9]", "_", prompt.lower())[:100] + ".png"
    #fecth and save to ./static/samples folder
    with open(f"./static/samples/{filename}", "wb") as f:
        f.write(requests.get(url).content)
    return "/static/samples/"+filename
import random
def randomKeywords(filenames=["words/elements.txt","words/animals.txt","words/items.txt"],starRating=1):
    keywords=[]
    for filename in filenames:
        with open(filename) as f:
            these_keywords=f.read().splitlines()
            keywords.append(random.choice(these_keywords))
    keywords.append(str(starRating)+"star")
    return keywords

from PIL import Image
import json
import random

def getRandomItem(starRating):
    keywords = randomKeywords(starRating=starRating)
    reward = json.loads(describeReward(keywords))
    caption = reward["caption"]
    filename = generateImage(caption)
    reward["filename"] = filename

    # Generate thumbnail
    thumbnail_filename = generateThumbnail("."+filename)
    #remove leading "." from thumbnail_filename
    thumbnail_filename=thumbnail_filename[1:]
    reward["thumbnail_filename"] = thumbnail_filename

    return reward

def generateThumbnail(filename):
    with Image.open(filename) as img:
        img.thumbnail((100, 100))  # Resize to 100x100 or smaller, maintaining aspect ratio
        thumbnail_filename = filename.replace('.png', '_thumbnail.png')  # Adjust extension as needed
        img.save(thumbnail_filename)
    return thumbnail_filename


def generateNPC(starRating):
    keyword_files=["words/genders.txt","words/elements.txt","words/races.txt","words/classes.txt"]
    keywords = randomKeywords(filenames=keyword_files,starRating=starRating)
    print(keywords)
    npc = json.loads(describeReward(keywords,system_prompt_file="npc_system_prompt.txt"))
    caption = npc["caption"]
    filename = generateImage(caption)
    npc["filename"] = filename

    # Generate thumbnail
    thumbnail_filename = generateThumbnail("."+filename)
    #remove leading "." from thumbnail_filename
    thumbnail_filename=thumbnail_filename[1:]
    npc["thumbnail_filename"] = thumbnail_filename

    return npc


def generateBuilding(starRating):
    keyword_files=["words/elements.txt","words/races.txt","words/buildings.txt"]
    keywords = randomKeywords(filenames=keyword_files,starRating=starRating)
    building = json.loads(describeReward(keywords,system_prompt_file="building_system_prompt.txt"))
    caption = building["caption"]
    filename = generateImage(caption)
    building["filename"] = filename

    # Generate thumbnail
    thumbnail_filename = generateThumbnail("."+filename)
    #remove leading "." from thumbnail_filename
    thumbnail_filename=thumbnail_filename[1:]
    building["thumbnail_filename"] = thumbnail_filename

    return building


def generateQuest(starRating):
    keyword_files=["words/questlines.txt","words/monsters.txt","words/settings.txt"]
    keywords = randomKeywords(filenames=keyword_files,starRating=starRating)
    quest = json.loads(describeReward(keywords,system_prompt_file="quest_system_prompt.txt"))
    caption = quest["caption"]
    filename = generateImage(caption)
    quest["filename"] = filename

    # Generate thumbnail
    thumbnail_filename = generateThumbnail("."+filename)
    #remove leading "." from thumbnail_filename
    thumbnail_filename=thumbnail_filename[1:]
    quest["thumbnail_filename"] = thumbnail_filename

    return quest

if __name__ == "__main__":
    for i in range(1,6):
        print(generateNPC(i))
        #print(generateQuest(i))