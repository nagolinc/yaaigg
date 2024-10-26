from flask import Flask, request, jsonify

from comfy import generate_comfy

app = Flask(__name__)

# In-memory data store
game_state = {"counters": {}, "inventory": {}}


# Endpoint to get the value of a counter
@app.route("/get_counter", methods=["GET"])
def get_counter():
    counter_name = request.args.get("name")
    value = game_state["counters"].get(counter_name, 0)        
    return jsonify({"name": counter_name,"value": value})


# Endpoint to set the value of a counter
@app.route("/set_counter", methods=["POST"])
def set_counter():
    data = request.json
    counter_name = data.get("name")
    value = data.get("value")
    game_state["counters"][counter_name] = value
    return jsonify(
        {"success": True, 
         "name": counter_name,
         "value": game_state["counters"][counter_name]}
    )
    
#increment counter
@app.route("/increment_counter", methods=["POST"])
def increment_counter():
    data = request.json
    counter_name = data.get("name")
    value = data.get("value",1)
    old_value = game_state["counters"].get(counter_name, 0)
    game_state["counters"][counter_name] = old_value + value
    return jsonify(
        {"success": True, 
         "name": counter_name,
         "value": game_state["counters"][counter_name]}
    )
    
    
#decrement counter
@app.route("/decrement_counter", methods=["POST"])
def decrement_counter():
    data = request.json
    counter_name = data.get("name")
    value = data.get("value",1)
    old_value = game_state["counters"].get(counter_name, 0)
    game_state["counters"][counter_name] = old_value - value
    return jsonify(
        {"success": True, 
         "name": counter_name,
         "value": game_state["counters"][counter_name]}
    )


# Endpoint to check if an item is in the inventory
@app.route("/inventory_has", methods=["GET"])
def inventory_has():
    item_name = request.args.get("item")
    has_item = game_state["inventory"].get(item_name, 0) > 0
    return jsonify(
        {"has_item": has_item, 
         "name": item_name,
         "value": game_state["inventory"].get(item_name, 0)}
    )


# Endpoint to add an item to the inventory
@app.route("/inventory_add", methods=["POST"])
def inventory_add():
    data = request.json
    item_name = data.get("item")
    quantity = data.get("quantity", 1)
    game_state["inventory"][item_name] = (
        game_state["inventory"].get(item_name, 0) + quantity
    )
    return jsonify({"success": True, 
                    "name": item_name,
                    "value": game_state["inventory"][item_name]})


# Endpoint to remove an item from the inventory
@app.route("/inventory_remove", methods=["POST"])
def inventory_remove():
    data = request.json
    item_name = data.get("item")
    quantity = data.get("quantity", 1)
    if game_state["inventory"].get(item_name, 0) >= quantity:
        game_state["inventory"][item_name] -= quantity
        if game_state["inventory"][item_name] <= 0:
            del game_state["inventory"][item_name]
        return jsonify({"success": True})
    else:
        return (
            jsonify(
                {
                    "error": "Not enough items",
                    "name": item_name,
                    "value": game_state["inventory"].get(item_name, 0),
                }
            ),
            400,
        )
        
        
images={}
        
#endpoint to get an image with an object name
@app.route("/get_image", methods=["GET","POST"])
def get_image():
    object_name = request.values.get("object")
    
    # Check if the object name is provided
    if not object_name:
        print('object name is required')
        return jsonify({"error": "Object name is required"}), 400
    
    
    if object_name in images:
        return jsonify({"image": images[object_name]})
    
    #generate image
    prompt = f"Generate a 3d computer graphics image of {object_name}, solid white background"
    image_filename = generate_comfy(prompt,width=512,height=512)
    
    #add a / to the beginning of the image filename
    image_filename = "/"+image_filename
    
    images[object_name] = image_filename
    return jsonify({"image": image_filename})
        
#/get_player_image (just returns /static/player.png)
@app.route("/get_player_image", methods=["GET"])
def get_player_image():
    return jsonify({"image": "/static/player.png"})

if __name__ == "__main__":
    app.run(debug=True)
