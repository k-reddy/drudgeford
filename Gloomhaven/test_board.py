import board
import display

def test_update_terrain():
    disp = display.Display(False)
    b = board.Board(5, [], [], disp)
    b.terrain = b._initialize_map()
    b.terrain[0][2] = ("FIRE", 2)
    expected = b.terrain
    b.update_terrain(3)
    assert b.terrain == expected

def test_update_terrain_2():
    disp = display.Display(False)
    b = board.Board(5, [], [], disp)
    b.terrain = b._initialize_map()
    b.terrain[0][2] = ("FIRE", 5)
    expected = b.terrain
    expected[0][2] = 'X'
    b.update_terrain(7)
    assert b.terrain == expected