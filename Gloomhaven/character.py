import random
import sys

import helpers
from gh_types import ActionCard
DIRECTION_MAP = {
    "w": [-1, 0],
    "s": [1, 0],
    "a": [0, -1],
    "d": [0, 1],
    "q": [-1, -1],
    "e": [-1, 1],
    "z": [1, -1],
    "c": [1, 1],
    "f": None
}

# characters are our actors
# they have core attributes (health, name, etc.) and a set of attacks they can do
# they will belong to a board, and they will send attacks out to the board to be carried out
class Character:
    # basic monster setup
    def __init__(self, name, health, disp):
        self.health = health
        self.name = name
        self.action_cards = create_action_cards()
        self.disp = disp

    def select_action_card(self):
        pass

    def decide_if_move_first(self, action_card, board):
        pass

    def perform_movement(self, action_card, board):
        pass

    def select_attack_target(self, in_range_opponents):
        pass


class Player(Character):
    # asks player what card they want to play
    def select_action_card(self) -> ActionCard:
        # if you run out of actions without killing the monster, you get exhausted
        if len(self.action_cards) == 0:
            self.disp.add_to_log("Oh no! You have no more action cards left!")
            # !!! implement ending the game here more gracefully
            sys.exit()
        # let them pick a valid action_card
        self.disp.log_action_cards(self.action_cards)
        prompt = "Which action card would you like to pick? Type the number exactly."
        valid_inputs = [str(i) for i, _ in enumerate(self.action_cards)]

        action_card_num = self.disp.get_user_input(prompt=prompt, valid_inputs=valid_inputs)
        action_card_to_perform = self.action_cards.pop(int(action_card_num))

        self.disp.clear_log()
        self.disp.add_to_log(f"{self.name} is performing {action_card_to_perform.attack_name}")

        return action_card_to_perform
    

    def decide_if_move_first(self, action_card: ActionCard, board) -> bool:
        self.disp.add_to_log(action_card)
        key_press = self.disp.get_user_input(prompt="Type 1 to move first or 2 to attack first.", valid_inputs=["1","2"])
        return key_press == "1"

    def perform_movement(self, action_card, board):
        remaining_movement = action_card["movement"]
        if remaining_movement == 0:
            self.disp.add_to_log("No movement!")
            return

        self.disp.add_to_log(f"\n{self.name} is moving")
        while remaining_movement > 0:
            self.disp.add_to_log(f"\nMovement remaining: {remaining_movement}")    
            prompt = "Type w for up, a for left, d for right, s for down, (q, e, z or c) to move diagonally, or f to finish. "
            direction = self.disp.get_user_input(prompt=prompt, valid_inputs=DIRECTION_MAP.keys())
            
            if direction == "f":
                break

            # get your currnet and new locations, then find out if the move is legal
            current_loc = board.find_location_of_target(self)
            new_row, new_col = [
                a + b for a, b in zip(current_loc, DIRECTION_MAP[direction])
            ]
            if board.is_legal_move(new_row, new_col):
                # do this instead of update location because it deals with terrain
                board.move_character_toward_location(self, (new_row, new_col), 1)
                remaining_movement -= 1
                continue
            else:
                self.disp.add_to_log(
                    "Invalid movement direction (obstacle, character, or board edge) - try again"
                )

        self.disp.add_to_log("Movement done! \n")

    def select_attack_target(self, in_range_opponents):
        if not in_range_opponents:
            self.disp.add_to_log("No opponents in range")
            return None

        self.disp.add_to_log("Opponents in range: ")
        for i, opponent in enumerate(in_range_opponents):
            self.disp.add_to_log(f"{i}: {opponent.name}")

        prompt = "Please type the number of the opponent you want to attack"
        valid_inputs = [str(i) for i, _ in enumerate(in_range_opponents)]
        target_num = self.disp.get_user_input(prompt=prompt, valid_inputs=valid_inputs)
        self.disp.add_to_log("")
        # ask the player who they want to attack
        # ask the board to attack that person
        return in_range_opponents[int(target_num)]


class Monster(Character):
    def select_action_card(self):
        return random.choice(self.action_cards)

    def decide_if_move_first(self, action_card: ActionCard, board):
        self.disp.add_to_log(f"{self.name} is performing {action_card}\n")
        # monster always moves first - won't move if they're within range
        return True

    def perform_movement(self, action_card: ActionCard, board):
        if action_card["distance"] == 0:
            return
        self.disp.add_to_log(f"{self.name} is moving")
        targets = board.find_opponents(self)
        target_loc = board.find_location_of_target(random.choice(targets))
        board.move_character_toward_location(self, target_loc, action_card["distance"])
        # add some space between the movement and attack
        self.disp.add_to_log("")

    def select_attack_target(self, in_range_opponents: list["Character"]):
        # monster picks a random opponent
        if not in_range_opponents:
            return None
        return random.choice(in_range_opponents)


def create_action_cards() -> list[ActionCard]:
    # each attack card will be generated with a strength, distance, and number of targets, so set
    # some values to pull from
    strengths = [1, 2, 3, 4, 5]
    strength_weights = [3, 5, 4, 2, 1]
    movements = [0, 1, 2, 3, 4]
    movement_weights = [1, 3, 4, 3, 1]
    max_distance = 3
    num_action_cards = 5
    action_cards = []

    # some things for attack names
    adjectives = ["Shadowed", "Infernal", "Venomous", "Blazing", "Cursed"]
    elements = ["Fang", "Storm", "Flame", "Void", "Thorn"]
    actions = ["Strike", "Surge", "Rend", "Burst", "Reaver"]

    for item in [adjectives, elements, actions]:
        random.shuffle(item)

    # generate each attack card
    for i in range(num_action_cards):
        strength = random.choices(strengths, strength_weights)[0]
        movement = random.choices(movements, movement_weights)[0]
        distance = random.randint(1, max_distance)
        action_card = ActionCard(
            attack_name=f"{adjectives.pop()} {elements.pop()} {actions.pop()}",
            strength=strength,
            distance=distance,
            movement=movement,
        )
        action_cards.append(action_card)
    return action_cards


CharacterType = Player | Monster
