import sys
import json

def load_map(filename):
    try:
        with open(filename, 'r') as file:
            game_map = json.load(file)
        validate_map(game_map)
        return game_map
    except FileNotFoundError:
        sys.exit("Error: Map file not found.")

def validate_map(game_map):
    if "start" not in game_map or "rooms" not in game_map:
        sys.exit("Error: Map is missing required 'start' or 'rooms' keys.")
    
    if not isinstance(game_map["rooms"], list):
        sys.exit("Error: 'rooms' must be a list.")
    
    room_names = set()
    
    for room in game_map["rooms"]:
        # Check for the presence of necessary keys
        if "name" not in room or "desc" not in room or "exits" not in room:
            sys.exit("Error: One or more rooms are missing 'name', 'desc', or 'exits'.")
        
        # Check for the correct data types
        if not isinstance(room["name"], str):
            sys.exit(f"Error: Room name must be a string, found {type(room['name'])}.")
        if not isinstance(room["desc"], str):
            sys.exit(f"Error: Room description must be a string, found {type(room['desc'])}.")
        if not isinstance(room["exits"], dict):
            sys.exit(f"Error: Room exits must be a dictionary, found {type(room['exits'])}.")

        # Ensure unique room names
        if room["name"] in room_names:
            sys.exit("Error: Duplicate room name found.")
        room_names.add(room["name"])
        
        # Check if all exits point to valid room names
        for direction, exit_room in room["exits"].items():
            if not isinstance(exit_room, str):
                sys.exit(f"Error: Exit destination must be a string, found {type(exit_room)}.")
            if exit_room not in room_names:
                # To account for forward references, we validate all exits at the end.
                continue

    # Final check for exit validity to account for forward references
    for room in game_map["rooms"]:
        for exit_room in room["exits"].values():
            if exit_room not in room_names:
                sys.exit(f"Error: Exit '{exit_room}' points to a non-existing room.")


class GameState:
    def __init__(self, game_map):
        self.game_map = game_map
        self.current_room = game_map["start"]
        self.inventory = []

    def get_current_room(self):
        for room in self.game_map["rooms"]:
            if room["name"] == self.current_room:
                return room
        return None

def resolve_command(abbreviation, options):
    """Resolve command abbreviation with possible options."""
    matches = [option for option in options if option.startswith(abbreviation)]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        return f"Did you want to {' or '.join(matches)}?"
    else:
        return None

def process_command(command, game_state):
    words = command.strip().lower().split()
    if not words:
        return "You need to enter a command."
    cmd = words[0]
    full_cmd = resolve_command(cmd, function_dict.keys())
    if full_cmd and full_cmd in function_dict:
        return function_dict[full_cmd](words[1:], game_state)
    elif "Did you want to" in full_cmd:
        return full_cmd
    else:
        return "Unknown command."

def handle_go(words, game_state):
    if not words:
        return "Sorry, you need to 'go' somewhere."
    direction = words[0]
    room = game_state.get_current_room()
    resolved_direction = resolve_command(direction, room["exits"].keys())
    if isinstance(resolved_direction, str) and resolved_direction in room["exits"]:
        game_state.current_room = room["exits"][resolved_direction]
        return f"You go {resolved_direction}.\n\n" + look(game_state)
    elif "Did you want to" in resolved_direction:
        return resolved_direction
    else:
        return "There's no way to go that direction."

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


def handle_get(words, game_state):
    if not words:
        return "Sorry, you need to 'get' something."
    item_query = words[0]
    room = game_state.get_current_room()
    items = room.get("items", [])
    # Handle substring matching for items
    matches = [item for item in items if item_query in item]
    if len(matches) == 1:
        item = matches[0]
        room["items"].remove(item)
        game_state.inventory.append(item)
        return f"You pick up the {item}."
    elif len(matches) > 1:
        return f"Did you want to get the {' or the '.join(matches)}?"
    else:
        return "There's no such item here."

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
        inventory_list = '\n  '.join(game_state.inventory)
        return f"Inventory:\n  {inventory_list}"
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
    try:
        if len(sys.argv) != 2:
            print("Usage: python3 adventure.py [map filename]", file=sys.stderr)
            return
        
        game_map = load_map(sys.argv[1])
        game_state = GameState(game_map)
        output = look(game_state)
        print(output)
        
        while True:
            command = input("What would you like to do? ")
            output = process_command(command, game_state)
            print(output)

    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")


if __name__ == "__main__":
    main()
