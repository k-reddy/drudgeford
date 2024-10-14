import pytest 
from board import Board
from character import Monster, Player
from agent import Agent, Ai, Human
from display import Display

disp = Display()
monsters = [Monster("Monster", 10, disp, "🦁", Ai())]
players = [Player("Player", 10, disp, "🐷", Ai())]
board = Board(10, monsters, players, disp)

def test_ai_select_action_card():
    for char in board.characters:
        assert char.select_action_card() in char.available_action_cards