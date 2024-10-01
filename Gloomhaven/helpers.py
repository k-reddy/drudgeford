import os


def clear_terminal():
    # Check if the system is Windows
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    return


def give_help():
    print('''Welcome to the game! Here's how it works:
- You and the monster will attack each other once per turn in a random order
- You can only attack if you are within range of your enemy
- You pick your attacks, and the monster's are randomly generated
- Each attack has a movement associated with it. If you're not in range, you'll move that amount toward your enemy
- If you end in range, you will attack. If not, you won't attack this turn.
- Whoever runs out of health first loses

Good luck!
        ''')
    input("Hit enter to continue")
    clear_terminal()
