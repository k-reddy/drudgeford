import pytest 
from unittest.mock import patch
from board import Board
from character import Monster, Player
from agent import Agent, Ai, Human
from display import Display

disp = Display()
monsters = [Monster("Monster", 10, disp, "🦁", Ai())]
ai_players = [Player("Player", 10, disp, "🐷", Ai())]
human_players = [Player("Player", 10, disp, "🐷", Human())]
ai_board = Board(10, monsters, ai_players, disp)
human_board = Board(10, monsters, human_players, disp)

def test_ai_select_action_card():
    for char in ai_board.characters:
        assert char.select_action_card() in char.available_action_cards

def test_human_select_action_card():
    with patch('display.Display.get_user_input', return_value ='0'):
        for char in human_board.characters:
            avail_cards = char.available_action_cards.copy()
            assert char.select_action_card() in avail_cards