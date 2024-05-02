# version 4
import json
import sys
def load_map(map_file):
    with open(map_file, 'r') as f:
        map_data = json.load(f)
    return map_data


class Room:
    def __init__(self, name, desc, exits, items=None, locked_exits=None):
        self.name = name
        self.desc = desc
        self.exits = exits
        self.items = items if items else []
        self.locked_exits = locked_exits if locked_exits else {}

    def unlock_exit(self, direction, required_item):
        self.locked_exits.pop(direction, None)
        print(f"The {direction} exit is now unlocked with {required_item}.")

    def lock_exit(self, direction, required_item):
        self.locked_exits[direction] = required_item
        print(f"The {direction} exit is now locked and requires {required_item} to unlock.")

    def __str__(self):
        exits_str = ' '.join(self.exits.keys())
        items_str = ', '.join(self.items) if self.items else "None"
        return f"{self.name}\n\n{self.desc}\n\nItems: {items_str}\n\nExists: {exits_str}\n"
    

class Player:
    def __init__(self):
        self.current_room = None
        self.inventory = []

    def describe_room(self):
        print(f'> {self.current_room.name}\n\n{self.current_room.desc}\n')
        exits_str = ' '.join(self.current_room.exits.keys())
        items_str = ', '.join(self.current_room.items) if self.current_room.items else "None"

        if(self.current_room.items):
            print(f'Items: {items_str}\n')
        print(f'Exits: {exits_str}\n')

    def go(self, direction):
        if direction in ["n", "s", "e", "w", "u", "d"]:
            direction = {"n": "north", "s": "south", "e": "east", "w": "west", "u": "up", "d": "down"}[direction]
        
        if direction in self.current_room.exits:
            if direction in self.current_room.locked_exits:
                required_item = self.current_room.locked_exits[direction]
                if required_item in self.inventory:
                    print(f"You unlock the {direction} exit with {required_item}.")
                    self.current_room.unlock_exit(direction, required_item)
                else:
                    print(f"The {direction} exit is locked. You need {required_item} to unlock it.")
                    return False
            self.current_room = self.current_room.exits[direction]
            print(f"You go {direction}.")
            print()
            return True
        else:
            print(f"There's no way to go {direction}.")
            return False

    def look(self):
        self.describe_room()

    def get(self, item):
        if item in self.current_room.items:
            self.current_room.items.remove(item)
            self.inventory.append(item)
            print(f"You pick up the {item}.")
        else:
            print(f"There's no {item} anywhere.")

    def show_inventory(self):
        if not self.inventory:
            print("You're not carrying anything.")
        else:
            print("Inventory:")
            for item in self.inventory:
                print(f" {item}")

    def drop(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            self.current_room.items.append(item)
            print(f"You drop the {item}")
        else:
            print(f"You don't have {item} in your inventory.")

    def help(self):
        print("You can run the following commands:")
        print("  go ...")
        print("  get ...")
        print("  look")
        print("  inventory")
        print("  quit")
        print("  help")
        print("  drop")

# print(sys.argv)
map_data = load_map(sys.argv[1])

rooms = {}  # 用于存储房间对象的字典


# 创建房间对象并添加到字典中
for room_data in map_data["rooms"]:
    room = Room(room_data["name"], room_data["desc"], room_data["exits"], room_data.get("items", []))
    rooms[room_data["name"]] = room

# 连接房间
for room_data in map_data["rooms"]:
    current_room = rooms[room_data["name"]]
    # print(rooms)
    for direction, room_name in room_data["exits"].items():
        
        # print(direction,room_name)
        current_room.exits[direction] = rooms[room_name]


# Initialize Player
player = Player()
# 设置玩家初始房间
player.current_room = rooms[map_data["start"]]

player.describe_room()
while True:
    try:
        action = input("What would you like to do? ").strip().lower().split()
        if not action:
            continue
        verb = action[0]
        if verb == "go":
            if len(action) < 2:
                print("Sorry, you need to 'go' somewhere.")
                continue
            direction = action[1]
            if direction in player.current_room.exits:
                if player.go(direction):
                    player.look()
            else:
                matches = [dire for dire in player.current_room.exits if direction in dire]
                if matches:
                    print(f"Did you want to go {matches[0]} or {matches[1]}?")
                else:
                    print(f"There's no way to go {direction}.")
        elif verb == "look":
            player.look()
        elif verb == "get":
            if len(action) < 2:
                print("Sorry, you need to 'get' something.")
                continue
            item = action[1]
            player.get(item)
        elif verb == "inventory":
            player.show_inventory()
        elif verb == "quit":
            print("Goodbye!")
            break
        elif verb == "help":
            player.help()
        elif verb == "drop":
            if len(action) < 2:
                print("Sorry, you need to drop something")
                continue
            item = action[1]
            player.drop(item)
            # player.look()
        else:
            print("I don't understand that command.")
    except EOFError:
        print("Use 'quit' to exit.")
