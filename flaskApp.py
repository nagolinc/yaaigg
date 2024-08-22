from flask import Flask, render_template, jsonify, request
from generationFunction import getRandomItem, generateNPC, generateBuilding, generateQuest
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

def saveUserData():
    with open("user_data.json", "w") as f:
        json.dump(user_data, f)

def loadUserData():
    global user_data
    try:
        with open("user_data.json") as f:
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

def generator(generation_function,destination_queue,cost_multiplier=1):
    while True:
        #print queue size
        
        if destination_queue.full():
            continue  # Wait if the queue is full
        print(destination_queue.qsize())
        stars = [1, 2, 3, 4, 5]
        weights = [50, 25, 15, 7, 3]
        star_rating = random.choices(stars, weights=weights, k=1)[0]
        item = generation_function(star_rating)

        #add star rating and reward to item
        item["star_rating"]=star_rating
        values=[1,5,10,25,50]
        #multiply reward value by cost_multiplier
        values=[value*cost_multiplier for value in values]
        item["reward_value"]=values[star_rating-1]

        print(f"Generated item: {item}")
        destination_queue.put(item)

def start_generators(count,generation_function,destination_queue,cost_multiplier=1):
    for _ in range(count):
        t = threading.Thread(target=generator,args=(generation_function,destination_queue,cost_multiplier))
        t.daemon = True
        t.start()





@app.route('/')
def index():
    return render_template('index.html')

@app.route('/items')
def items():
    return render_template('items.html')

@app.route('/earn_currency', methods=['POST'])
def earn_currency():
    user_data["currency"] += 1  # Increment currency
    saveUserData()
    return jsonify({"currency": user_data["currency"]})

@app.route('/sell_reward', methods=['POST'])
def sell_reward():
    value = request.json['value']
    name=request.json['name']
    user_data["currency"] += int(value)
    #remove item from user_data
    user_data["items"]=[item for item in user_data["items"] if item["name"]!=name]
    saveUserData()
    return jsonify({"currency": user_data["currency"]})

@app.route('/open_box', methods=['POST'])
def open_box():
    if user_data["currency"] < 5:
        return jsonify({"error": "Not enough currency, cost 5"}), 400
    if item_queue.empty():
        return jsonify({"error": "No items available, please wait."}), 503
    user_data["currency"] -= 5
    item = item_queue.get()
    user_data["items"].append(item)
    saveUserData()
    return jsonify({"item": item, "currency": user_data["currency"]})

@app.route('/hire_npc', methods=['POST'])
def hire_npc(cost=10):
    if user_data["currency"] < cost:
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
    name=request.json['name']
    user_data["currency"] += int(value)
    #remove npc from user_data
    user_data["npcs"]=[npc for npc in user_data["npcs"] if npc["name"]!=name]
    saveUserData()
    return jsonify({"currency": user_data["currency"]})


@app.route('/npc')
def npcs():
    return render_template('npc.html')

@app.route('/build_building', methods=['POST'])
def build_building(cost=20):
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
    name=request.json['name']
    user_data["currency"] += int(value)
    #remove building from user_data
    user_data["buildings"]=[building for building in user_data["buildings"] if building["name"]!=name]
    saveUserData()
    return jsonify({"currency": user_data["currency"]})

@app.route('/building')
def buildings():
    return render_template('building.html')


@app.route('/random_quest', methods=['GET','POST'])
def random_quest():
    if quest_queue.empty():
        return jsonify({"error": "No quests available, please wait."}), 503
    quest = quest_queue.get()
    return jsonify({"quest": quest})

@app.route('/quest')
def quests():
    return render_template('quest.html')


@app.route('/complete_quest', methods=['POST'])
def complete_quest():
    # Here you can process the quest data sent from the frontend
    # For example, you can extract NPC IDs or other parameters
    # data = request.json
    # npc_ids = data.get('npcs', [])

    # Since this is a mock endpoint, we will not use the input data
    # and simply return a success message and a timeout
    return jsonify({
        "status": "success",
        "message": "Quest completed successfully!",
        "timeout": 5  # Timeout in seconds
    })

@app.route('/get_user_data')
def get_user_data():
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


if __name__ == '__main__':
    loadUserData()

    item_queue = queue.Queue(maxsize=4)  # Adjust size based on expected load
    npc_queue = queue.Queue(maxsize=4)  # Adjust size based on expected load
    building_queue = queue.Queue(maxsize=4)  # Adjust size based on expected load
    quest_queue = queue.Queue(maxsize=2)  # Adjust size based on expected load

    start_generators(5,getRandomItem,item_queue,1)
    start_generators(5,generateNPC,npc_queue,2)
    start_generators(5,generateBuilding,building_queue,5)
    start_generators(5,generateQuest,quest_queue,10)
    
    app.run(debug=True)
