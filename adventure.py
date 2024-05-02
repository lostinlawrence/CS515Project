# version 3
# version 2
import sys
import json

def load_map(filename):
    """Load the game map from a file and validate it."""
    try:
        with open(filename, 'r') as file:
            game_map = json.load(file)
        validate_map(game_map)
        return game_map
    except FileNotFoundError:
        print("Error: Map file not found.", file=sys.stderr)
        sys.exit(1)

def validate_map(game_map):
    """Validate the structure and content of the game map."""
    if "start" not in game_map or "rooms" not in game_map:
        print("Error: Map is missing required 'start' or 'rooms' keys.", file=sys.stderr)
        sys.exit(1)
    
    room_names = set()
    for room in game_map["rooms"]:
        if "name" not in room or "desc" not in room or "exits" not in room:
            print("Error: One or more rooms are missing required fields.", file=sys.stderr)
            sys.exit(1)
        if not isinstance(room["name"], str) or not isinstance(room["desc"], str) or not isinstance(room["exits"], dict):
            print("Error: Incorrect data types in room definitions.", file=sys.stderr)
            sys.exit(1)
        if room["name"] in room_names:
            print("Error: Duplicate room name found.", file=sys.stderr)
            sys.exit(1)
        room_names.add(room["name"])
        for exit_room in room["exits"].values():
            if exit_room not in room_names:
                # Allow forward references
                continue

    # Validate if all exits are correct at the end of the loop
    for room in game_map["rooms"]:
        for exit_room in room["exits"].values():
            if exit_room not in room_names:
                print(f"Error: Exit '{exit_room}' points to a non-existing room.", file=sys.stderr)
                sys.exit(1)


class GameState:
    """Class to hold the state of the game."""
    def __init__(self, game_map):
        self.game_map = game_map
        self.current_room = game_map["start"]
        self.inventory = []

    def get_current_room(self):
        """Retrieve the current room based on the player's location."""
        return next((room for room in self.game_map["rooms"] if room["name"] == self.current_room), None)

def process_command(command, game_state):

    # This is a dictionary of fuctions. When a verb or function is added, it should be added in the dictionary.
    # Below there is a handle_help function that will print all the keys of this dictionary.
    function_dict = {"go":handle_go,"east":handle_direction,"west":handle_direction,
                     "south":handle_direction,"north":handle_direction,"look":handle_look,
                     "get":handle_get,"drop":handle_drop,"inventory":handle_inventory,"help":handle_help,
                     "quit":None
                     }
    words = command.strip().lower().split()
    if not words:
        return "You need to enter a command."

    cmd = words[0]
    if cmd == "quit":
        print("Goodbye!")
        sys.exit(0)
    elif cmd == "go":
        return function_dict[cmd](words[1:], game_state)
    elif cmd == "east" or cmd == "west" or cmd == "south" or cmd == "north" or cmd == "southeast" or cmd == "southwest" or cmd == "northeast" or cmd == "northwest":
        return function_dict[cmd](words[0], game_state)
    elif cmd == "look":
        return function_dict[cmd](game_state)
    elif cmd == "get":
        return function_dict[cmd](words[1:], game_state)
    elif cmd == "drop":
        return function_dict[cmd](words[1:], game_state)
    elif cmd == "inventory":
        return function_dict[cmd](game_state)
    elif cmd == "help":
        return function_dict[cmd](function_dict)       
    else:
        return "Use 'quit' to exit."

def handle_go(direction, game_state):#direction is a list here with only one element
    if len(direction) == 0:
        return "Sorry, you need to 'go' somewhere."
    room = game_state.get_current_room()
    if direction[0] in room["exits"]:
        game_state.current_room = room["exits"][direction[0]]
        print(f"You go {direction[0]}.\n")
        return look(game_state)
    else:
        return f"There's no way to go {direction[0]}."

# This is an extension to convert direction to a verb.
# This method take in directions including east, west, south and north
def handle_direction(direction, game_state):#direction在这里是一个string
    room = game_state.get_current_room()
    if direction in room["exits"]:
        game_state.current_room = room["exits"][direction]
        print(f"You go {direction}.\n")
        return look(game_state)
    else:
        return f"There's no way to go {direction}."

def handle_look(game_state):
    return look(game_state)

def look(game_state):
    room = game_state.get_current_room()
    if "items" in room and room["items"]:
        items = " ".join(room.get("items", []))
        exits = " ".join(room["exits"].keys())
        return f"> {room['name']}\n\n{room['desc']}\n\nItems: {items}\n\nExits: {exits}\n"
    else:
        exits = " ".join(room["exits"].keys())
        return f"> {room['name']}\n\n{room['desc']}\n\nExits: {exits}\n"


def handle_get(items, game_state):#items here is a list
    if not items:
        return "Sorry, you need to 'get' something."
    item = items[0]# To take out the only element from list items and pass it to variable item
    room = game_state.get_current_room()#room here is a dictionary
    if "items" in room and item in room["items"]:
        room["items"].remove(item)
        game_state.inventory.append(item)
        return f"You pick up the {item}."
    else:
        return f"There's no {item} anywhere."

# This is an extension to drop items.
def handle_drop(items, game_state):
    if not items:
        return "Sorry, you need to 'drop' something."
    item = items[0]
    room = game_state.get_current_room()
    if "items" in room and item in game_state.inventory:
        game_state.inventory.remove(item)
        room["items"].append(item)
        return f"You drop the {item}."
    else:
        return f"You don't have {item} or you can't drop {item} in this room"

def handle_inventory(game_state):
    if game_state.inventory:
        return "Inventory:\n  " + "\n  ".join(game_state.inventory)
    else:
        return "You're not carrying anything."

# This is an extension to help verb, it will print all possible verbs.
# All the verbs are stored in a dictionary, when the help function is call, it will print all the dict keys
def handle_help(function_dict):
    list1 = list(function_dict.keys())
    s = ""
    s = s + "You can run the following commands:" + "\n"
    for i in list1:
        s = s + i +"\n"
    s = s.strip()
    return s

def main():
    """Main game loop."""
    if len(sys.argv) != 2:
        print("Usage: python3 adventure.py [map filename]", file=sys.stderr)
        return
    
    game_map = load_map(sys.argv[1])
    game_state = GameState(game_map)
    print(look(game_state))
    
    while True:
        try:
            command = input("What would you like to do? ")
            output = process_command(command, game_state)
            print(output)
        except EOFError:
            print("Use 'quit' to exit.")

if __name__ == "__main__":
    main()
