import attack_shapes as shapes

def test_circle():
    circle_dirs = shapes.circle(1)
    expected = {
        (0,0),
        (1,0),
        (1,1), 
        (0,1),
        (-1,0),
        (-1,-1),
        (0,-1),
        (-1,1),
        (1,-1)
    }
    assert circle_dirs == expected

def test_circle_2():
    circle_dirs = shapes.circle(2)
    expected = {
        (0,0),
        (1,0),
        (1,1), 
        (0,1),
        (-1,0),
        (-1,-1),
        (0,-1),
        (-1,1),
        (1,-1),
        (0,2),
        (0,-2),
        (2,0),
        (-2,0),
        (2,2),
        (-2,-2),
        (2,-2),
        (-2,2),
        (1,2),
        (2,1), 
        (-1,2),
        (1,-2),
        (-2,1),
        (-2,-1),
        (2,-1),
        (-1,-2)
    }
    assert circle_dirs == expected