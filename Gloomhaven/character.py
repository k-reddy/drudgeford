import random
import helpers


# characters are our actors
# they have core attributes (health, name, etc.) and a set of attacks they can do
# they will belong to a board, and they will send attacks out to the board to be carried out
class Character:
    # basic monster setup
    def __init__(self, name, health, is_player, starting_location):
        self.name = name
        self.health = health
        # randomly generate a stack of possible attacks
        self.action_cards = self.create_action_cards()
        # is this the player or the monster?
        self.is_player = is_player
        self.location = starting_location

    # think of this as a deck of attack cards that we will randomly pull from
    # here we generate that deck of attack cards
    def create_action_cards(self):
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
        adjectives = ['Shadowed', 'Infernal', 'Venomous', 'Blazing', 'Cursed']
        elements = ['Fang', 'Storm', 'Flame', 'Void', 'Thorn']
        actions = ['Strike', 'Surge', 'Rend', 'Burst', 'Reaver']

        for item in [adjectives, elements, actions]:
            random.shuffle(item)

        # generate each attack card
        for i in range(num_action_cards):
            strength = random.choices(strengths, strength_weights)[0]
            movement = random.choices(movements, movement_weights)[0]
            distance = random.randint(1, max_distance)
            action_card = {
                "attack_name": f"{adjectives.pop()} {elements.pop()} {actions.pop()}",
                "strength": strength,
                "distance": distance,
                "movement": movement
            }
            action_cards.append(action_card)
        return action_cards

    def select_action_card(self):
        pass

    def print_action_card(self, action_card):
        print(f"{self.name} is performing " + action_card["attack_name"] + ": Attack " + str(
            action_card["strength"]) + ", Range " + str(action_card["distance"]) + ", Movement " + str(
            action_card["movement"]) + "\n")
    def set_action_order(self, action_card, board):
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

    def set_action_order(self, action_card, board):
        self.print_action_card(action_card)
        action_orders = {
            "1": [self.perform_movement(), self.select_attack_target],
            "2": [self.select_attack_target, self.perform_movement()]
        }
        action_num = input("Type 1 to move first or 2 to attack first. ")
        while not action_num in action_order_map:
            action_num = input("Invalid input. Please type 1 or 2. ")

        return action_orders[action_num]


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
                self.player.location = list(np.add(self.player.location, direction_map[direction]))
                helpers.clear_terminal()
                self.draw()
            else:
                print("Incorrect input. Try again!")
                continue
            remaining_movement -= 1
        print("movement done!")

    def select_attack_target(self):
        # ask the board who's in range
        # ask the player who they want to attack
        # ask the board to attack that person
        return target_id

class Monster(Character):
    def select_action_card(self):
        return random.choice(self.action_cards)

    def set_action_order(self, action_card, board):
        self.print_action_card(action_card)
        action_order = []
        # if not in range, move first
        if not board.check_attack_in_range(action_card["distance"]):
            action_order.append(self.perform_movement)

        # after movement, try to attack
        action_order.append(self.select_attack_target)
        return action_order

    def perform_movement(self, attack):
        # WORK ON THIS TOMORROW
        # ask the board for the closest opponent
        # ask the board to move you as close as possible (board will have paths)

        # keeping until I implement the above, with these known issues:
        # can probably simplify the distance calculations
        # I think there's also an issue here if one distance is negative and the other is positive
        y_dist = self.monster.location[0] - self.player.location[0]
        x_dist = self.monster.location[1] - self.player.location[1]

        distance = attack["distance"]
        if distance > 0:
            print("Monster moved!\n")
            # first move vertically if you can
            if y_dist > 1:
                dist_to_travel = distance if (x_dist + y_dist) > distance else y_dist - 1
                if is_player:
                    self.player.location[0] += dist_to_travel
                else:
                    self.monster.location[0] -= dist_to_travel

                distance -= y_dist

            # if there's distance left, move horizontally
            if x_dist > 1:
                dist_to_travel = distance if x_dist > distance else x_dist - 1
                if is_player:
                    self.player.location[1] += dist_to_travel
                else:
                    self.monster.location[1] -= dist_to_travel
            self.draw()

    def select_attack_target(self):
        # ask the board for your closest opponent in range
        return target_id
