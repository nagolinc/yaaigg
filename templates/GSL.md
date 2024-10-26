Game Systems Library is a DSL for designing simple games.

All games take place on a gird of cells and are composed of objects, actors, counters, and events.
All games are "turn" based, where each turn the player can move, interact with objects, and trigger events.

Any time the player clicks on an object or moves the player, a turn passes.
Players can also intentionally end their turn by clicking on a "end turn" button or by pressing "space".

GSL is designed to be simple and easy to use, and is suitable for creating simple games like puzzles, platformers, and adventure games.

Games implemented in GSL can be compiled to a variety of platforms, including HTML5, PyGame Android, and iOS.


Here is a very simple game implemented in GSL:

```
minigame "Gold Coin Chest" {
    layout "game_map" {
        size 8x6

        object "chest" type "clickable" 
            position 4x3
            size 1x1
    }

    counter "gold_coins" start GLOBAL

    event "player_clicks_chest" {
        condition "clicked" object "chest"
        action "increment" counter "gold_coins" by 1
        action "game_end" message "You found a gold coin!"
    }
}
```

Notice that when a counter is set to GLOBAL, it can be accessed from other minigames.

This means that the player can collect gold coins in one minigame and spend them in another minigame.

At the heart of GSL are the following concepts:

==Counters==
Counters are used to keep track of the state of the game. They can be used to store the score, the number of lives, the number of enemies, etc.

Each counter has a name and a value.
counters can be incremented, decremented, or set to a specific value.
for example:
`action "increment" counter "gold_coins" by 1`
counters can also be used as conditions in events, for example:
`condition "counter" counter "gold_coins" equals 10`

It is important to understand that counters are global and can be accessed from different minigames.

For example, in one game, a player can collect gold coins, and in another game, the player can spend the gold coins to buy items.

==inventory==

Inventory referers to the objects that the player has collected. The inventory can be used to store objects that the player has collected, and can be used to trigger events.

The game system can check if objects are in the invetory, remove items for the inventory, and add items to the inventory.
The player can have more than one of an object in the inventory.

Here is an example of adding to the inventory:
`action "add" object "apple" to inventory`

Here is an example of removing from the inventory:
`action "remove" object "apple" from inventory`

Here is an example of checking if an object is in the inventory:
`condition "inventory" object "apple" in inventory`

Like counters, the inventory is global and can be accessed from different minigames.

==Buttons==

Buttons are drawn outside of the game map and always have a label. They can be clicked by the player to trigger events.

For example, here is a simple button that ends the game when clicked:
```
button "end_turn" label "End Turn"

event "player_clicks_end_turn" {
    condition "clicked" button "end_turn"
    action "game_end" message "You ended your turn!"
}
```

There is always a "end turn" button that the player can click to end their turn.
There is also always a special "restart game" button that the player can click to restart the game.

==Objects==
Objects are the entities that the player interacts with in the game. They can be clickable and can be blocking or non-blocking.

Objects must have a position and a size.

Objects can also have additional properties, which can be numbers or boolean values.

For example, here is a simple clickable object:
```
object "chest" type "clickable" 
    position 4x3
    size 1x1
```

Position can also be randomized. For example, here is a simple object that is placed in a random position:
```
object "chest" type "clickable" 
    position random
    size 1x1
```

When position is random, the object will be placed in a random position on the map (that is not occupied by another object).

Objects can also have a count, indicating that there is more than one of the object.

Importantly, if the count>1, then position must be random (otherwise the objects would overlap).

For example, here is a simple object that has a count of 5:
```
object "apple" type "clickable" 
    position random
    size 1x1
    count 5
```


==Actors==

Actors are just like obects, but in addition to a position and size they also have a direction and a speed.
the direction can be one of "up", "down", "left".
The speed can be a number (usually 1 or 0) and is measured in units per frame.

For example, here is a simple ghost actor that moves left or right until it hits an obstacle:
```

object "ghost" type "actor" 
    position 4x3
    size 1x1 
    direction "left"
    speed 1

//if the ghost is moving left, and it hits a wall, change its direction to right
event "ghost hits wall" {
    condition "collides" object "ghost" with BLOCKING
    condition property "direction" object "ghost" equals "left"
    action "change_direction" object "ghost" to "right"
}
//if the ghost is moving right, and it hits a wall, change its direction to left
event "ghost hits wall" {
    condition "collides" object "ghost" with BLOCKING
    condition property "direction" object "ghost" equals "right"
    action "change_direction" object "ghost" to "left"
}
```

Actors cannot move through blocking objects, and will stop when they hit a blocking object.
Nor can they move through the edge of the map.

Properties can store boolean values or integers.

For example, here is a simple object with a boolean property:

```
object "door" type "clickable" 
    position 4x3
    size 1x1
    property "is_open" false
```

Properties can be used as conditions in events, for example:
`condition property "is_open" object "door" equals true`

Or they can be set to a value in an action, for example:
`action "set" property "is_open" object "door" to true`

==Player==

The player is a special object that can be controlled by the player. The player can move in all four directions (up, down, left, right) and can interact with other objects. The player moves when the player presses the arrow keys (or the WASD keys).

Like other objects, the player has a position and a size and cannot move through blocking objects or the edge of the map.

==Events==

Events are the core of the game logic. They are triggered by conditions and perform actions.
All events are checke each tick and if the conditions are met, the actions are performed.

for example, here is an even that ends the game if the counter 'gold_coins' reaches 10:
```
event "player_clicks_chest" {
    condition "clicked" object "chest"
    action "increment" counter "gold_coins" by 1
    action "game_end" message "You found a gold coin!"
}
```


Notice that events are evaluated in order and from top to bottom. 
And each event is evaluated each turn, progressing from top to bottom until it hits a failed condition.

This means that if an action has multiple conditions interleved with actions, only some of the actions may be performed.

For example, here is an event that increments a counter and ends the game if the counter reaches 10:

```
event "player_clicks_chest" {
    condition "clicked" object "chest"
    action "increment" counter "gold_coins" by 1
    condition "counter" counter "gold_coins" equals 10
    action "game_end" message "You found 10 gold coins!"
}
```


==Layouts==

Layouts are used to define the game world. They contain objects and actors, and can have additional properties like size and background image.

The layout should be defined at the beginning of the game, and all objects and actors should be placed inside the layout.

The layout may or may not contain a player object (depending on the game).


==Game End==

The game ends when the player triggers a "game_end" action. The game can end with a message, a score, or a custom message.

for example, here is game where the user loses if the player clicks on a bomb:
```
event "player_clicks_bomb" {
    condition "clicked" object "bomb"
    action "game_end" message "You clicked on a bomb! Game Over!"
}
```


Here are some examples of games implemented in GSL:

Here is a simple "raffle game"

```
minigame "Raffle" {
    layout "game_map" {
        size 8x6

        object "raffle_box" type "clickable" 
            position 4x3
            size 1x1
    }

    counter "tickets"

    event "player_clicks_raffle_box" {
        condition "clicked" object "raffle_box"
        action "increment" counter "tickets" by 1
        action "game_end" message "You got a raffle ticket!"
    }
}
```


Here is a game where a player must click on five apples to win a 'llama ticket'

```
minigame "Apple Picking" {
    layout "game_map" {
        size 8x6

        objects "apple" type "clickable" count 5 {
            position random
            size 1x1
            property "clicked" false
        }
    }

    counter "apples" start 0
    counter "llama_tickets" start GLOBAL

    events "player_clicks_apple" for each "apple" {
        condition "clicked" object "apple"
        condition property "clicked" object "apple" equals false
        action "set" property "clicked" object "apple" to true
        action "increment" counter "apples" by 1
    }

    event "win" {
        condition "counter" counter "apples" equals 5
        action "increment" counter "llama_tickets" by 1
        action "game_end" message "You found all the apples! You win a llama ticket!"
    }
}
```


Here is a game where a player must avoid a ghost to win a 'llama ticket'

```
minigame "Ghost Chase" {
    layout "game_map" {
        size 8x6

        object "player" type "player" 
            position 4x3
            size 1x1

        object "ghost" type "actor" 
            position 1x1
            size 1x1 
            direction "right"
            speed 1

        object "llama_ticket" type "clickable" 
            position 7x5
            size 1x1
    }

    counter "llama_tickets" start GLOBAL

    event "player_clicks_llama_ticket" {
        condition "clicked" object "llama_ticket"
        action "increment" counter "llama_tickets" by 1
        action "game_end" message "You found a llama ticket!"
    }

    event "player_hits_ghost" {
        condition "collides" object "player" with "ghost"
        action "game_end" message "You got caught by the ghost! Game Over!"
    }

    event "ghost_hits_all" {
        condition "collides" object "ghost" with EDGE
        action "reverse_direction" object "ghost"
    }
}
```



Here is a game where where the player must collect diamonds while avoiding bombs.  the game should increment the counter 'megabucks' by 10 upon victory.

minigame "Diamond Collector" {
    layout "game_map" {
        size 8x6

        objects "diamond" type "collectible" count 5 {
            position random
            size 1x1
            property "collected" false
        }

        objects "bomb" type "obstacle" count 3 {
            position random
            size 1x1
        }

        object "player" type "player" {
            position 0x0
            size 1x1
        }
    }

    counter "diamonds_collected" start 0
    counter "megabucks" start GLOBAL
    counter "player_lives" start 1

    events "player_collects_diamond" for each "diamond" {
        condition "collides_with" object "player" target "diamond"
        condition property "collected" object "diamond" equals false
        action "set" property "collected" object "diamond" to true
        action "increment" counter "diamonds_collected" by 1
    }

    events "player_hits_bomb" for each "bomb" {
        condition "collides_with" object "player" target "bomb"
        action "decrement" counter "player_lives" by 1
        action "game_end" message "You hit a bomb! Game over."
    }

    event "win" {
        condition "counter" counter "diamonds_collected" equals 5
        action "increment" counter "megabucks" by 10
        action "game_end" message "You collected all the diamonds! You win 10 megabucks!"
    }
}


Here is a game where a player uses a key from their inventory (collected in a previous game) to unlock a chest and win a 'Gold Star'

```
minigame "Unlock Chest"{
 layout "game_map" {
        size 8x6

        object "chest" type "clickable" 
            position 4x3
            size 1x1
            property "locked" true
    }

    counter "gold_stars" start GLOBAL

    event "player_clicks_chest" {
        condition "clicked" object "chest"
        condition property "locked" object "chest" equals false
        action "increment" counter "gold_stars" by 1
        action "game_end" message "You found a gold star!"
    }

    event "player_clicks_chest" {
        condition "clicked" object "chest"
        condition property "locked" object "chest" equals true
        condition "inventory" object "key" in inventory
        action "set" property "locked" object "chest" to false
    }
```


a game where the player must collect rubies while avoiding skeletons (that move in a random direction each turn).  the game ends when there are no more rubies.


minigame "Ruby Escape" {
    layout "game_map" {
        size 10x8

        objects "ruby" type "collectible" count 10 {
            position random
            size 1x1
            property "collected" false
        }

        objects "skeleton" type "actor" count 3 {
            position random
            size 1x1
            direction random
            speed 1
        }

        object "player" type "player" {
            position 1x1
            size 1x1
        }
    }

    counter "rubies_collected" start GLOBAL
    counter "player_lives" start 1

    events "player_collects_ruby" for each "ruby" {
        condition "collides_with" object "player" target "ruby"
        condition property "collected" object "ruby" equals false
        action "set" property "collected" object "ruby" to true
        action "increment" counter "rubies_collected" by 1
    }

    events "player_hits_skeleton" for each "skeleton" {
        condition "collides_with" object "player" target "skeleton"
        action "game_end" message "You were caught by a skeleton! Game over."
    }

    events "skeleton_moves" for each "skeleton" {
        action "move" object "skeleton" direction random
    }

    event "win" {
        condition "counter" counter "rubies_collected" equals 10
        action "game_end" message "You collected all the rubies! You've escaped the skeletons!"
    }
}

a game where a player spends a 'bonus ticket' (collected in another game) to get a 'magic potion' with a 50% chance


minigame "Magic Potion Raffle" {
    layout "game_map" {
        size 8x6

        object "raffle_box" type "clickable"
            position 4x3
            size 1x1
            property "used" false
    }

    counter "bonus_tickets" start GLOBAL
    counter "magic_potions" start GLOBAL

    event "player_clicks_raffle_box" {
        condition "clicked" object "raffle_box"
        condition property "used" object "raffle_box" equals false
        condition "counter" counter "bonus_tickets" greater than 0
        action "decrement" counter "bonus_tickets" by 1
        action "set" property "used" object "raffle_box" to true
        condition "random_chance" probability 50
        action "increment" counter "magic_potions" by 1
        action "game_end" message "Congratulations! You won a magic potion!"
    }

    event "raffle_box_used" {
        condition property "used" object "raffle_box" equals true
        action "game_end" message "You've already used the raffle box!"
    }
}


Here is the implementation for a GSL minigame titled "Dog Chase" where the player must catch a dog that randomly moves around a grid filled with rocks that serve as obstacles. Upon successfully catching the dog, the player wins a 'pet supply'.


minigame "Dog Chase" {
    layout "game_map" {
        size 8x8

        objects "rock" type "blocking" count 10 {
            position random
            size 1x1
        }

        object "dog" type "actor" {
            position random
            size 1x1
            direction random
            speed 1
        }

        object "player" type "player" {
            position random
            size 1x1
        }
    }

    counter "pet_supplies" start GLOBAL

    events "player_catches_dog" {
        condition "collides_with" object "player" target "dog"
        action "increment" counter "pet_supplies" by 1
        action "game_end" message "You caught the dog! You receive 1 pet supply."
    }

    events "dog_moves" for each "dog" {
        action "move" object "dog" direction random
    }

    events "dog_hits_rock" for each "dog" {
        condition "collides_with" object "dog" target "rock"
        action "change_direction" object "dog"
    }

    event "player_hits_rock" {
        condition "collides_with" object "player" target "rock"
        action "game_end" message "You hit a rock and lost sight of the dog. Game over."
    }
}

a zombie defense game


minigame "Zombie Defense" {
    layout "game_map" {
        size 10x10

        object "base" type "critical" {
            position 5x5
            size 2x2
        }
    }

    counter "zombies_defeated" start 0
    counter "traps_left" start 5 // Start with 5 traps available to place

    objects "zombie" type "actor" count 10 {
        position random
        size 1x1
        direction random
        speed 1
    }

    object player type "player" {
        position 0x0
        size 1x1
    }

    button "place_trap" label "Place Trap"

    // Player places a trap
    event "player_places_trap" {
        condition "clicked" button "place_trap"
        condition "counter" counter "traps_left" greater than 0
        action "place" object "trap" at player // Assumes functionality to place at cursor position
        action "decrement" counter "traps_left" by 1
    }

    events "zombie_steps_on_trap" for each "trap" {
        condition "collides_with" object "zombie" target "trap"
        action "remove" object "trap"
        action "remove" object "zombie"
        action "increment" counter "zombies_defeated" by 1
    }

    events "zombie_reaches_player" for each "zombie" {
        condition "collides_with" object "zombie" target "player"
        action "game_end" message "A zombie killed you! Game Over."
    }

    event "all_zombies_defeated" {
        condition "counter" counter "zombies_defeated" equals 10
        action "game_end" message "All zombies defeated! You win."
    }

    button "end_turn" label "End Turn"

    event "player_ends_turn" {
        condition "clicked" button "end_turn"
        action "advance_zombies"
    }

    function "advance_zombies" {
        action move_all "zombie" direction random
    }
}

Cooking competition game

minigame "Cooking Contest" {
    layout "kitchen" {
        size 8x8

        object "stove" type "clickable" {
            position 2x2
            size 1x1
            property "active" false
        }

        object "ingredient_box" type "clickable" {
            position 5x5
            size 1x1
            property "open" true
        }

        object "sink" type "clickable" {
            position 6x1
            size 1x1
            property "clean" true
        }
    }

    counter "score" start 0
    counter "dishes_completed" start 0
    counter "gold_stars" start GLOBAL

    button "cook_dish" label "Cook"

    events "prepare_ingredients" {
        condition "clicked" object "ingredient_box"
        condition property "open" object "ingredient_box" equals true
        action "set" property "open" object "ingredient_box" to false
        action "display_message" message "Ingredients prepared!"
    }

    events "start_cooking" {
        condition "clicked" object "stove"
        condition property "active" object "stove" equals false
        action "set" property "active" object "stove" to true
        action "display_message" message "Cooking started!"
    }

    events "clean_up" {
        condition "clicked" object "sink"
        action "set" property "clean" object "sink" to true
        action "display_message" message "Kitchen cleaned!"
    }

    event "cook_dish" {
        condition "clicked" button "cook_dish"
        condition property "active" object "stove" equals true
        condition property "open" object "ingredient_box" equals false
        condition property "clean" object "sink" equals true
        action "increment" counter "dishes_completed" by 1
        action "increment" counter "score" by 10
        action "display_message" message "Dish completed successfully!"
        action "set" property "active" object "stove" to false
        action "set" property "open" object "ingredient_box" to true
        action "set" property "clean" object "sink" to false        
    }

    event "end_contest" {
        condition "counter" counter "dishes_completed" equals 5
        action "increment" counter "gold_stars" by 1
        action "game_end" message "Contest finished! Your score: {score}"
    }
}

