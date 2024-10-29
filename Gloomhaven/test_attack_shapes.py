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