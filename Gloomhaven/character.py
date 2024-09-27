import random
import helpers


# characters are our actors
# they have core attributes (health, name, etc.) and a set of attacks they can do
# they will belong to a board, and they will send attacks out to the board to be carried out
class Character:
    # basic monster setup
    def __init__(self, name, health, id):
        self.name = name

    def select_action_card(self):
        pass

    def print_action_card(self, action_card):
        print(f"{self.name} is performing " + action_card["attack_name"] + ": Attack " + str(
            action_card["strength"]) + ", Range " + str(action_card["distance"]) + ", Movement " + str(
            action_card["movement"]) + "\n")
    def decide_if_move_first(self, action_card, board):
        pass

    def perform_movement(self, action_card, board):
        pass

    def select_attack_target(self):
        pass

class Player(Character):
    # asks player what card they want to play
    def select_action_card(self):
        # if you run out of actions without killing the monster, you get exhausted
        if len(self.action_cards) == 0:
            print("Oh no! You have no more action cards left!")
            board.lose_game()
        # if they have action cards, show them what they have
        print("Your action cards are: ")
        for i, action_card in enumerate(self.action_card):
            print(
                f"{i}: {action_card['attack_name']}: Strength {action_card['strength']}, Distance: {action_card['distance']}, ",
                f"Movement: {action_card['movement']}")
        # let them pick a valid action_card
        while True:
            action_card_num = input("\nWhich action card would you like to pick? Type the number exactly.")
            try:
                action_card_num = int(action_card_num)
                helpers.clear_terminal()
                action_card_to_perform = self.action_cards.pop(action_card_num)
                break
            except (ValueError, IndexError):
                print("Oops, typo! Try typing the number again.")
        return action_card_to_perform

    def decide_if_move_first(self, action_card, board):
        self.print_action_card(action_card)
        action_num = input("Type 1 to move first or 2 to attack first. ")
        while action_num not in ["1","2"]:
            action_num = input("Invalid input. Please type 1 or 2. ")
        return action_num == "1"

    # !!! Legacy code: implement
    def perform_movement(self, action_card, board):
        remaining_movement = action_card["movement"]
        if remaining_movement == 0:
            print("No movement!")
            return
        print("\nNow it's time to move!")
        while remaining_movement > 0:
            self.print_action_card(action_card)
            print(f"\nmovement remaining: {remaining_movement}")
            direction = input(
                "Type w for up, a for left, d for right, s for down, or f to finish. "
                "If you move off the map, you'll disappear!")
            direction_map = {
                "w": [-1, 0],
                "s": [1, 0],
                "a": [0, -1],
                "d": [0, 1]
            }
            if direction == "f":
                break
            elif direction in direction_map:
                # ask the board to move in a direction
                # if legal, the board will allow you
                # else the board will say no and you try again
                board.adjudicate_movement_request()
            else:
                print("Incorrect input. Try again!")
                continue
            remaining_movement -= 1
        print("movement done!")

    # !!! Implement
    def select_attack_target_id(self):
        # ask the board who's in range
        # ask the player who they want to attack
        # ask the board to attack that person
        return target_id

class Monster(Character):
    def select_action_card(self):
        return random.choice(self.action_cards)

    def decide_if_move_first(self, action_card, board):
        self.print_action_card(action_card)
        # monster always moves first - won't move if they're within range
        return True

    def perform_movement(self, action_card, board):
        target_location = board.find_closest_opponent_location(self)
        board.move_character_to_location(self, target_location, action_card["distance"])

    def select_attack_target_id(self, board):
        # monster always attacks the closest opponent
        return board.find_closest_opponent_id(self)
