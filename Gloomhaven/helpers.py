import os


def clear_terminal():
    # Check if the system is Windows
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')



