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
        # if it's the monster grab a random attack card
        board.draw()
        if self.is_player is False:
            attack_to_perform = random.choice(self.attacks)
            board.perform_monster_card(attack_to_perform)
        # if it's the player, let them pick their own actions
        else:
            attack_to_perform = self.get_player_attack_selection(board)
            board.perform_player_card(attack_to_perform)

    # asks player what card they want to play
    def get_player_attack_selection(self, board):
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
