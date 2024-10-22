from unittest.mock import patch
from board import Board
from character import Monster, Player
from agent import Ai, Human
from display import Display
from gh_types import ActionCard

# !!! implement pytest fixtures 
# !!! try parameterizing tests 
# !!! property based testing - hypothesis? python library
disp = Display(False)
ai_monsters = [Monster("Monster", 10, disp, "🦁", Ai())]
ai_players = [Player("Player", 10, disp, "🐷", Ai())]
human_players = [Player("Player", 10, disp, "🐷", Human())]
human_monsters = [Monster("Player", 10, disp, "🐷", Human())]
ai_board = Board(10, ai_monsters, ai_players, disp)
human_board = Board(10, human_monsters, human_players, disp)


def test_ai_select_action_card():
    for char in ai_board.characters:
        avail_cards = char.available_action_cards.copy()
        assert char.select_action_card() in avail_cards


def test_human_select_action_card():
    with patch("display.Display.get_user_input", return_value="0"):
        for char in human_board.characters:
            avail_cards = char.available_action_cards.copy()
            assert char.select_action_card() in avail_cards


def test_ai_decide_if_move_first():
    for char in ai_board.characters:
        assert char.decide_if_move_first(disp) is True


def test_human_decide_if_move_first():
    with patch("display.Display.get_user_input", return_value="1"):
        for char in human_board.characters:
            assert char.decide_if_move_first(disp) is True

    with patch("display.Display.get_user_input", return_value="2"):
        for char in human_board.characters:
            assert char.decide_if_move_first(disp) is False

def test_human_select_attack_target():
    char = human_players[0]
    assert char.select_attack_target([]) is None
    with patch("display.Display.get_user_input", return_value="0"):
        assert char.select_attack_target(ai_monsters)==ai_monsters[0]

def test_ai_select_attack_target():
    char = ai_monsters[0]
    assert char.select_attack_target([]) is None
    assert char.select_attack_target(ai_players) in ai_players

# !!! I should clear all obstacles from the board or this will mess up
# !!! all these tests feel really messy - lots of failure points unrelated to what we're testing
# !!! they also just check the most base cases - but doing otherwise feels like it'd be a ton of work
def test_ai_perform_movement():
    action_card = ActionCard(
        attack_name="test",
        strength=1,
        distance=2,
        movement=1
    )
    # clear a spot on the board
    for i in range(2):
        for j in range(2):
            ai_board.update_locations(i,j,None)
    
    # put the characters in known, clear locations
    try:
        ai_board.update_character_location(
            ai_monsters[0],
            ai_board.find_location_of_target(ai_monsters[0]),
            [0,0]
        )
    except ValueError:
        ai_board.update_locations(0,0,ai_monsters[0])
    
    try: 
        ai_board.update_character_location(
            ai_players[0],
            ai_board.find_location_of_target(ai_players[0]),
            [2,2]
        )
    except ValueError:
        ai_board.update_locations(
            2,2, ai_players[0]
        )
    # move
    ai_monsters[0].perform_movement(action_card, ai_board)
    # check new loc
    assert ai_board.find_location_of_target(ai_monsters[0]) == (1,1)
    # move again
    ai_monsters[0].perform_movement(action_card, ai_board)
    # check new loc - shouldn't move
    assert ai_board.find_location_of_target(ai_monsters[0]) == (1,1)

def test_human_perform_movement():
    action_card = ActionCard(
        attack_name="test",
        strength=1,
        distance=2,
        movement=1
    )
    # clear a spot on the board
    for i in range(2):
        for j in range(2):
            human_board.update_locations(i,j,None)
    
    # put the characters in known, clear locations - if we cleared them, have to reinsert them
    try:
        human_board.update_character_location(
            human_players[0],
            human_board.find_location_of_target(human_players[0]),
            [1,1]
        )
    except ValueError:
        human_board.update_locations(1,1,human_players[0])
    # move
    with patch("display.Display.get_user_input", return_value="q"):
        human_players[0].perform_movement(action_card, human_board)
    # check new loc
    assert human_board.find_location_of_target(human_players[0]) == (0,0)

    # move
    with patch("display.Display.get_user_input", return_value="c"):
        human_players[0].perform_movement(action_card, human_board)
    # check new loc
    assert human_board.find_location_of_target(human_players[0]) == (1,1)

    # move
    with patch("display.Display.get_user_input", return_value="s"):
        human_players[0].perform_movement(action_card, human_board)
    # check new loc
    assert human_board.find_location_of_target(human_players[0]) == (2,1)