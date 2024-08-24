from flask import Flask, render_template, jsonify, request, make_response, send_from_directory
from generationFunction import getRandomItem, generateNPC, generateBuilding, generateQuest, setupKeywordMapping
import random
import threading
import queue
import json
app = Flask(__name__)




# Global data and queue setup
user_data = {
    "currency": 10,  # Initial currency
    "items": [],  # Collected items
    "npcs": [],  # Collected NPCs
    "buildings": []  # Collected buildings
}


def levelMultiplier(level=None):
    if level is None:
        level=user_data.get("level",1)
    return level*(level+1)/2


def saveUserData(filename="user_data.json"):
    with open(filename, "w") as f:
        json.dump(user_data, f)

def loadUserData(filename="user_data.json"):
    global user_data
    try:
        with open(filename) as f:
            user_data = json.load(f)
            if "currency" not in user_data:
                user_data["currency"] = 10
            if "items" not in user_data:
                user_data["items"] = []
            if "npcs" not in user_data:
                user_data["npcs"] = []
            if "buildings" not in user_data:
                user_data["buildings"] = []

    except FileNotFoundError:
        pass

def generator_single(generation_function, star_rating, cost_multiplier=1,level=None):
    
    if level is None:
        level=user_data.get("level",1)
    
    item = generation_function(star_rating,level=level)
    item["star_rating"] = star_rating
    values = [1, 5, 10, 25, 50]
    values = [value * cost_multiplier for value in values]
    item["reward_value"] = values[star_rating - 1]*levelMultiplier(level)
    
    return item

import time

def worker(queues, generators, cost_multiplier=1):
    
    
    print("worker started")
    
    while True:
        for destination_queue, generation_function in zip(queues, generators):
            
            
            queue_sizes=[queue.qsize() for queue in queues]
            
            #if not all full
            if not all([queue.full() for queue in queues]):
                print("\n\nQUEUE SIZES",queue_sizes)
            else:
                #sleep
                #print("\n\nALL QUEUES FULL, sleeping\n\n")
                time.sleep(0.25)
            
            if not destination_queue.full():
                print(destination_queue.qsize())
                stars = [1, 2, 3, 4, 5]
                weights = [50, 25, 15, 7, 3]
                star_rating = random.choices(stars, weights=weights, k=1)[0]
            
                #print("\n\n\nENTERING LOCK ZONE\n\n\n")
                item = generator_single(generation_function, star_rating, cost_multiplier)
                print(f"Generated item: {item}")
                destination_queue.put(item)
                #print("\n\n\nEXITING LOCK ZONE\n\n\n")



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/items')
def items():
    return render_template('items.html')

@app.route('/earn_currency', methods=['POST'])
def earn_currency(base_earn=1):
    
    earn_amount=base_earn*levelMultiplier()
    
    user_data["currency"] += earn_amount  # Increment currency
    saveUserData()
    return jsonify({"currency": user_data["currency"]})

@app.route('/sell_reward', methods=['POST'])
def sell_reward():
    value = request.json['value']
    id=request.json['id']
    user_data["currency"] += int(value)
    #remove item from user_data
    user_data["items"]=[item for item in user_data["items"] if item["id"]!=id]
    saveUserData()
    return jsonify({"currency": user_data["currency"]})

@app.route('/open_box', methods=['POST'])
def open_box(base_cost=5):
    
    cost=base_cost*levelMultiplier()
    
    if user_data["currency"] < cost:
        return jsonify({"error": f"Not enough currency, cost {cost}"}), 400
    if item_queue.empty():
        return jsonify({"error": "No items available, please wait."}), 503
    user_data["currency"] -= cost
    item = item_queue.get()
    user_data["items"].append(item)
    saveUserData()
    return jsonify({"item": item, "currency": user_data["currency"]})

@app.route('/hire_npc', methods=['POST'])
def hire_npc(base_cost=10):
    cost=base_cost*levelMultiplier()
    if user_data["currency"] <cost:
        return jsonify({"error": f"Not enough currency, cost {cost}"}), 400
    if npc_queue.empty():
        return jsonify({"error": "No NPCs available, please wait."}), 503
    user_data["currency"] -= cost
    npc = npc_queue.get()
    user_data["npcs"].append(npc)
    saveUserData()
    return jsonify({"npc": npc, "currency": user_data["currency"]})

@app.route('/sell_npc', methods=['POST'])
def sell_npc():
    value = request.json['value']
    id=request.json['id']
    user_data["currency"] += int(value)
    #remove npc from user_data
    user_data["npcs"]=[npc for npc in user_data["npcs"] if npc["id"]!=id]
    saveUserData()
    return jsonify({"currency": user_data["currency"]})


@app.route('/npc')
def npcs():
    return render_template('npc.html')

@app.route('/build_building', methods=['POST'])
def build_building(base_cost=20):
    cost=base_cost*levelMultiplier()
    if user_data["currency"] < cost:
        return jsonify({"error": f"Not enough currency, cost {cost}"}), 400
    if building_queue.empty():
        return jsonify({"error": "No buildings available, please wait."}), 503
    user_data["currency"] -= cost
    building = building_queue.get()
    user_data["buildings"].append(building)
    saveUserData()
    return jsonify({"building": building, "currency": user_data["currency"]})




@app.route('/sell_building', methods=['POST'])
def sell_building():
    value = request.json['value']
    id=request.json['id']
    user_data["currency"] += int(value)
    #remove building from user_data
    user_data["buildings"]=[building for building in user_data["buildings"] if building["id"]!=id]
    #set npc.location  to 'None' if building is sold
    for npc in user_data["npcs"]:
        if "location" in npc and npc["location"]==id:
            npc["location"]="None"
    saveUserData()
    return jsonify({"currency": user_data["currency"]})

@app.route('/building')
def buildings():
    return render_template('building.html')

from math import exp,log

def teamBonus(values):
    return exp(sum([log(value) for value in values])/3)


storedQuest=None

@app.route('/random_quest', methods=['GET','POST'])
def random_quest():
    global storedQuest
    if storedQuest is None:
        if quest_queue.empty():
            return jsonify({"error": "No quests available, please wait."}), 503
        quest = quest_queue.get()
        storedQuest=quest
    else:
        quest=storedQuest   
    return jsonify({"quest": quest})

@app.route('/quest')
def quests():
    return render_template('quest.html')

#/character_management
@app.route('/character_management')
def character_management():
    return render_template('character_management.html')


BASE_QUEST_CHALLENGE_MULTIPLIER=8
LEVEL_UP_THRESHOLD=20

# Define the custom sigmoid function
# should start at 0, reach 0.5 at 1 and 1 at infinity
def custom_sigmoid(x):
    return 2*(1 / (1 + exp(-x)) - 0.5)


#endpoint to get experience, level and experience to next level
@app.route('/get_level_data')
def get_level_data():
    level=user_data.get("level",1)
    exp=user_data.get("experience",0)
    expNextLevel=LEVEL_UP_THRESHOLD*levelMultiplier(level)
    return jsonify({"level":level,"experience":exp,"experienceNextLevel":expNextLevel})




def predictQuestOutcome(quest,npcs):
    quest_star_rating=quest.get("star_rating",1)
    quest_reward_value=quest.get("reward_value",1)
    quest_level=quest.get("level",1)
    
    quest_challenge=quest_star_rating*BASE_QUEST_CHALLENGE_MULTIPLIER*levelMultiplier(quest_level)
    
    #compute power level of all npcs
    power_levels=[compute_power_level(npc.get("id")) for npc in npcs]
    team_power=teamBonus(power_levels)+sum(power_levels)
    
    #let's make this a sigmoid function
    p_success=custom_sigmoid(team_power/quest_challenge)
    
    #timeout should have min 5 seconds max 30 and decrease with p_success
    timeout=5+25*(1-p_success)
    
    print("debug, team power=",team_power," quest_challenge=",quest_challenge,
          "ratio=",team_power/quest_challenge,
          "p_success",p_success,
          "timeout",timeout)
    
    return p_success,timeout


#endpoint to show p_success
@app.route('/predict_quest_outcome', methods=['POST'])
def predict_quest_outcome():
    data = request.json
    npcs = data.get('npcs', [])
    quest=data.get('quest',{})
    
    p_success,timeout=predictQuestOutcome(quest,npcs)
    
    return jsonify({"p_success":p_success,
                    "timeout":timeout})


#endpoint to complete quest
@app.route('/complete_quest', methods=['POST'])
def complete_quest():
    # Here you can process the quest data sent from the frontend
    # For example, you can extract NPC IDs or other parameters
    data = request.json
    npcs = data.get('npcs', [])
    quest=data.get('quest',{})
    
    quest_star_rating=quest.get("star_rating",1)
    quest_level=quest.get("level",1)
    
    p_success,timeout=predictQuestOutcome(quest,npcs)
    
    r=random.random()
    
    print("ROLLING DICE, r=",r," p_success=",p_success,r<p_success)
    
    if r>p_success:
        #failure
        return jsonify({
            "status": "failure",
            "message": "Quest failed",
            "timeout": 5,  # Timeout in seconds
            "level_up":False
        })
    
    global storedQuest
    
    storedQuest=None
    
    possible_rewards=["currency"]
    #add rewards if queues are not empty
    if item_queue.qsize()>0:
        possible_rewards.append("item")
    if npc_queue.qsize()>0:
        possible_rewards.append("npc")
    if building_queue.qsize()>0:
        possible_rewards.append("building")
    
    rewardMessage=""
    
    star_bonus=[1,2,3,4,5]
    expAmount=star_bonus[quest_star_rating-1]*levelMultiplier(quest_level)
    #add to user_data
    user_data["experience"]=user_data.get("experience",0)+expAmount
    
    rewardMessage+=f"<p>Received <b>{expAmount}<b> experience</p>"
    
    
    level_up=False
    
    if user_data["experience"]>=LEVEL_UP_THRESHOLD*levelMultiplier():
        user_data["level"]=user_data.get("level",1)+1
        user_data["experience"]=0
        rewardMessage+=f"<p>leveled up to level <b>{user_data['level']}</b><p>"
        level_up=True
    
    
    reward=random.choice(possible_rewards)
    
    # Ensure weights list is at least as long as the queue size + 1 (to include 0)
    weights = [1, 2, 2, 1, 0.5]
    queue_size = item_queue.qsize()
    if queue_size + 1 > len(weights):
        weights.extend([0.1] * (queue_size + 1 - len(weights)))  # Extend weights if needed
    
    # Slice weights to match the queue size + 1
    weights = weights[:queue_size + 1]
    
    # Create a list of items based on the queue size + 1 (to include 0)
    l = list(range(0, queue_size + 1))
    
    # Select a random item based on the weights
    num_items = random.choices(l, weights=weights)[0]
    
    def escape_single_quotes(text):
        return text.replace("'", "&#39;")
    
    for _ in range(num_items):
        item = item_queue.get()
        user_data["items"].append(item)
        rewardMessage += f"<p>Received item: <b>{item['name']}</b> <img onclick='showModal(\"{item['filename']}\", \"{escape_single_quotes(item['name'])}\")' src='{item['thumbnail_filename']}' width='50px'></p>"
        
    NPC_PROB=0.5
    #if reward=="npc":
    if not npc_queue.empty() and random.random()<NPC_PROB:
        npc = npc_queue.get()
        user_data["npcs"].append(npc)
        rewardMessage += f"<p>Received npc: <b>{npc['name']}</b> <img onclick='showModal(\"{npc['filename']}\", \"{escape_single_quotes(npc['name'])}\")' src='{npc['thumbnail_filename']}' width='50px'></p>"
        
    BUILDING_PROB=0.5
    #elif reward=="building":
    #check if building queue is nonempty
    if not building_queue.empty() and random.random()<BUILDING_PROB:
        building = building_queue.get()
        user_data["buildings"].append(building)
        rewardMessage += f"<p>Received building: <b>{building['name']}</b> <img onclick='showModal(\"{building['filename']}\", \"{escape_single_quotes(building['name'])}\")' src='{building['thumbnail_filename']}' width='50px'></p>"
        
    if True: #always give currency
        currency_amount=int(random.choice([10,25,50,100,250])*levelMultiplier())
        user_data["currency"] += currency_amount
        rewardMessage+=f"<p>Received <b>{currency_amount}</b> currency</p>"
        
        
    #check if npcs can level up (if quest level > npc level)
    level_up_odds=[0.2,0.3,0.4,0.5,1.0]
    for npc in npcs:
        if npc.get("level",1)<quest_level:
            p_level_up=level_up_odds[quest_star_rating-1]
            if random.random()<p_level_up:
                #find npc in user_data
                for user_data_npc in user_data["npcs"]:
                    if user_data_npc["id"]==npc["id"]:
                        user_data_npc["level"]=user_data_npc.get("level",1)+1
                        rewardMessage += f"<p><b>{npc['name']}</b> leveled up to <b>{user_data_npc['level']}</b></p>"
                        break



    saveUserData()
    # Since this is a mock endpoint, we will not use the input data
    # and simply return a success message and a timeout
    return jsonify({
        "status": "success",
        "message": "Quest completed successfully!"+rewardMessage,
        "timeout": 5,  # Timeout in seconds
        "level_up":level_up
    })



import os

@app.route('/static/samples/<path:filename>')
def custom_static(filename):
    response = make_response(send_from_directory(os.path.join(app.root_path, 'static/samples'), filename))
    response.headers['Cache-Control'] = 'public, max-age=31536000'  # Cache for 1 year
    return response




@app.route('/get_user_data')
def get_user_data():
    #recompute power levels
    for npc in user_data["npcs"]:
        npc["power_level"]=compute_power_level(npc["id"])
    
    return jsonify(user_data)


@app.route('/ready')
def ready():
    queue_type = request.args.get('type')
    if queue_type == 'item':
        is_nonempty = not item_queue.empty()
    elif queue_type == 'npc':
        is_nonempty = not npc_queue.empty()
    elif queue_type == 'building':
        is_nonempty = not building_queue.empty()
    elif queue_type == 'quest':
        is_nonempty = not quest_queue.empty()
    else:
        return jsonify({"error": "Invalid type"}), 400

    return jsonify({"nonempty": is_nonempty})




#/equip endpoint, given a item and an npc, set item.equppied=npc.name if npc is none, set item.equipped=None
@app.route('/equip', methods=['POST'])
def equip():
    item_id = request.json['item']
    npc_id = request.json['npc']
    
    #find npc with id in user_data
    npc_name=None
    for npc in user_data["npcs"]:
        if npc["id"]==npc_id:
            npc_name=npc["name"]
    
    
    if npc_id == "None":
        npc_id = None
    for item in user_data["items"]:
        if item["id"] == item_id:
            item["equipped"] = npc_id
            item["equipped_name"]=npc_name
    saveUserData()
    return jsonify({"status": "success"})



def canMoveNPCToBuilding(npcId, buildingId):
    #check if npc.element==building.element || npc.race==building.race
    
    #find npc
    npc=None
    for npc in user_data["npcs"]:
        if npc["id"]==npcId:
            break
    #find building
    building=None
    for building in user_data["buildings"]:
        if building["id"]==buildingId:
            break
    
    #check element
    if npc["element"]==building["element"]:
        pass
    elif npc["race"]==building["race"]:
        pass
    else:
        return False
    
    MAX_POP=building.get("max_population",3)
    #check if building is full
    current_pop = 0
    for npc in user_data["npcs"]:
        if "location" in npc and npc["location"] == buildingId:
            current_pop += 1
            
    if current_pop>=MAX_POP:
        return False
    
    return True


#/availablebuildings endpoint, given a npc, return a list of buildings that npc can move to
@app.route('/availablebuildings', methods=['POST'])
def availablebuildings():
    npc_id = request.json['npc']
    available_buildings = []
    for building in user_data["buildings"]:
        if canMoveNPCToBuilding(npc_id, building["id"]):
            available_buildings.append({"name":building["name"],"id":building["id"]})
    return jsonify({"available_buildings": available_buildings})


#/move_to_building endpoint, given a npc and a building, set npc.location=building.id if building is none, set npc.location=None
@app.route('/move_to_building', methods=['POST'])
def move_to_building():
    npc_id = request.json['npc']
    building_id = request.json['building']
    
    #find building with id in user_data
    user_building=None
    for building in user_data["buildings"]:
        if building["id"]==building_id:
            user_building=building
            break
        
    
    if user_building is None:
        building_name="None"
    else:
        building_name=user_building.get("name","None")
    
    
    if building_id == "None":
        building_id = None
    for npc in user_data["npcs"]:
        if npc["id"] == npc_id:
            npc["location"] = building_id
            npc["location_name"]=building_name
    saveUserData()
    return jsonify({"status": "success"})


def compute_power_level(npc_id):
    #find npc with id npc_id in user_data
    npc=None
    for _npc in user_data["npcs"]:
        if _npc["id"] == npc_id:
            npc=_npc
            break
        
    assert npc is not None, f"NPC with id {npc_id} not found"
    
    #level is 1 if not present
    npc_level = npc.get("level", 1)
    star_rating = npc.get("star_rating", 1)
    base_power_level = levelMultiplier(npc_level) * star_rating
    
    power_level=base_power_level
    
    for item in user_data["items"]:
        if "equipped" in item and item["equipped"] == npc_id:
            item_level = item.get("level", 1)
            item_star_rating = item.get("star_rating", 1)
            item_power_level = levelMultiplier(item_level) * item_star_rating
            power_level += item_power_level
            
    if npc.get("location","None") != "None":
        for building in user_data["buildings"]:
            if building["id"] == npc["location"]:
                building_level = building.get("level", 1)
                building_star_rating = building.get("star_rating", 1)
                
                bonus = [0.1, 0.25, 0.5, 0.75, 1.0]
                
                #this guarantees that the multiplier is 1 when npc_level=building_level
                adjustment_factor = (building_level+npc_level)/(2*npc_level)
                
                power_level = power_level * (1+bonus[building_star_rating-1]*adjustment_factor)
                break
            
    #round to nearest integer
    power_level=int(power_level+0.5)
            
    return power_level


@app.route('/power_level', methods=['POST'])
def power_level():
    npc_id = request.json['npc']
    power_level = compute_power_level(npc_id)
    return jsonify({"power_level": power_level})
    



import argparse


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Start the web server')
    
    #--saveData (default = user_data.json)
    parser.add_argument('--saveData', default='user_data.json', help='Save user data to this file')
    
    #--numThreads (default = 4)
    parser.add_argument('--numThreads', default=4, type=int, help='Number of threads to start for each generator')
    
    #--queueSize (default = 4)
    parser.add_argument('--queueSize', default=4, type=int, help='Size of the queue for each generator')
    
    #--keyword_mapping (default keyword_mapping.yaml)
    parser.add_argument('--keyword_mapping', default='keyword_mapping.yaml', help='Keyword mapping file')
    
    args = parser.parse_args()
    
    setupKeywordMapping(args.keyword_mapping)
    
    
    loadUserData(args.saveData)

    item_queue = queue.Queue(maxsize=args.queueSize)  # Adjust size based on expected load
    npc_queue = queue.Queue(maxsize=args.queueSize)  # Adjust size based on expected load
    building_queue = queue.Queue(maxsize=args.queueSize)  # Adjust size based on expected load
    quest_queue = queue.Queue(maxsize=args.queueSize)  # Adjust size based on expected load
    
    queues = [item_queue, npc_queue, building_queue, quest_queue]
    generators = [getRandomItem, generateNPC, generateBuilding, generateQuest]
    
    #worker_thread = threading.Thread(target=worker, args=(queues, generators))
    #worker_thread.start()
    #worker_thread.join()
    
    # Create and start multiple worker threads
    print("STARTING",args.numThreads,"WORKER THREADS")
    worker_threads = []
    for _ in range(args.numThreads):
        worker_thread = threading.Thread(target=worker, args=(queues, generators))
        worker_thread.start()
        worker_threads.append(worker_thread)

    
    

    #start_generators(args.numThreads,getRandomItem,item_queue,1)
    #start_generators(args.numThreads,generateNPC,npc_queue,2)
    #start_generators(args.numThreads,generateBuilding,building_queue,5)
    #start_generators(args.numThreads,generateQuest,quest_queue,10)
    
    app.run(debug=True, use_reloader=False)
