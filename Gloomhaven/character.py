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
        self.attacks = self.create_attack_cards()
        # is this the player or the monster?
        self.is_player = is_player
        self.location = starting_location

    # think of this as a deck of attack cards that we will randomly pull from
    # here we generate that deck of attack cards
    def create_attack_cards(self):
        # each attack card will be generated with a strength, distance, and number of targets, so set
        # some values to pull from
        strengths = [1, 2, 3, 4, 5]
        strength_weights = [3, 5, 4, 2, 1]
        movements = [0, 1, 2, 3, 4]
        movement_weights = [1, 3, 4, 3, 1]
        max_distance = 3
        num_attacks = 5
        attacks = []

        # some things for attack names
        adjectives = ['Shadowed', 'Infernal', 'Venomous', 'Blazing', 'Cursed']
        elements = ['Fang', 'Storm', 'Flame', 'Void', 'Thorn']
        actions = ['Strike', 'Surge', 'Rend', 'Burst', 'Reaver']

        for item in [adjectives, elements, actions]:
            random.shuffle(item)

        # generate each attack card
        for i in range(num_attacks):
            strength = random.choices(strengths, strength_weights)[0]
            movement = random.choices(movements, movement_weights)[0]
            distance = random.randint(1, max_distance)
            attack = {
                "attack_name": f"{adjectives.pop()} {elements.pop()} {actions.pop()}",
                "strength": strength,
                "distance": distance,
                "movement": movement
            }
            attacks.append(attack)
        return attacks

    # grabs an attack card and send it to the board to be played
    def select_and_submit_attack(self, board):
        board.draw()
        attack_to_perform = self.get_attack_selection(self, board)
        board.perform_character_card(attack_to_perform)
    def get_attack_selection(self, board):
        pass

    def perform_card(self, attack):
        pass

    def perform_movement(self, attack):
        pass

class Player(Character):
    # asks player what card they want to play
    def get_attack_selection(self, board):
        # if you run out of actions without killing the monster, you get exhausted
        if len(self.attacks) == 0:
            print("Oh no! You have no more attacks left!")
            board.lose_game()
        # if they have attacks, show them what they have
        print("Your attacks are: ")
        for i, attack in enumerate(self.attacks):
            print(
                f"{i}: {attack['attack_name']}: Strength {attack['strength']}, Distance: {attack['distance']}, ",
                f"Movement: {attack['movement']}")
        # let them pick a valid attack
        while True:
            attack_num = input("\nWhich attack card would you like to pick? Type the number exactly.")
            # PUT SOMETHING IN HERE TO CATCH IF IT'S NOT AN INT

            if attack_num == '':
                print("Oops, typo! Try typing the number again.")
            else:
                attack_num = int(attack_num)
                if 0 <= attack_num < len(self.attacks):
                    helpers.clear_terminal()
                    attack_to_perform = self.attacks.pop(attack_num)
                    break
                else:
                    print("Oops, typo! Try typing the number again.")
        return attack_to_perform

    def perform_card(self, attack):
        print(f"{self.player.name} performs " + attack["attack_name"] + ": Attack " + str(
            attack["strength"]) + ", Range " + str(attack["distance"]) + ", Movement " + str(attack["movement"]) + "\n")
        good_action = False
        self.draw()
        while not good_action:
            action = input("Type 1 to move first or 2 to attack first. ")
            if action == "1":
                good_action = True
                self.perform_player_movement(attack)
                time.sleep(3)
                self.attack_opponent(attack, True)
            elif action == "2":
                good_action = True
                self.attack_opponent(attack, True)
                time.sleep(3)
                self.perform_player_movement(attack)
        time.sleep(3)

    def perform_movement(self, attack):
        remaining_movement = attack["movement"]
        if remaining_movement == 0:
            print("No movement!")
            return
        print("\nNow it's time to move!")
        while remaining_movement > 0:
            print(
                f"You are performing {attack['attack_name']} with Attack " + str(attack["strength"]) + ", Range " + str(
                    attack["distance"]))
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
                self.player.location = list(np.add(self.player.location, direction_map[direction]))
                helpers.clear_terminal()
                self.draw()
            else:
                print("Incorrect input. Try again!")
                continue
            remaining_movement -= 1
        print("movement done!")

class Monster(Character):
    def get_attack_selection(self, board):
        return random.choice(self.attacks)

    def perform_card(self, attack):
        print("Monster performs " + attack["attack_name"] + ": Attack " + str(attack["strength"]) + ", Range " + str(
            attack["distance"]) + ", Movement " + str(attack["movement"]) + "\n")
        if not self.check_attack_in_range(attack["distance"]):
            self.perform_monster_movement(False, attack["movement"])

        # after movement, try to attack
        self.attack_opponent(attack, False)
        time.sleep(3)

    def perform_movement(self, attack):
        # WORK ON THIS TOMORROW
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
