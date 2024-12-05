import attack_shapes as shapes


def test_circle():
    circle_dirs = shapes.circle(1)
    expected = {
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1),
        (-1, 0),
        (-1, -1),
        (0, -1),
        (-1, 1),
        (1, -1),
    }
    assert circle_dirs == expected


def test_circle_2():
    circle_dirs = shapes.circle(2)
    expected = {
        (0, 0),
        (1, 0),
        (1, 1),
        (0, 1),
        (-1, 0),
        (-1, -1),
        (0, -1),
        (-1, 1),
        (1, -1),
        (0, 2),
        (0, -2),
        (2, 0),
        (-2, 0),
        (2, 2),
        (-2, -2),
        (2, -2),
        (-2, 2),
        (1, 2),
        (2, 1),
        (-1, 2),
        (1, -2),
        (-2, 1),
        (-2, -1),
        (2, -1),
        (-1, -2),
    }
    assert circle_dirs == expected


def test_line():
    line_dirs = shapes.line(3)
    expected = {(0, 1), (0, 2), (0, 3)}
    assert line_dirs == expected


def test_line_2():
    line_dirs = shapes.line(2)
    expected = {(-1, 0), (-2, 0)}
    assert line_dirs == expected


def test_line_3():
    line_dirs = shapes.line(2)
    expected = {(-1, -1), (-2, -2)}
    assert line_dirs == expected


def test_bar():
    line_dirs = shapes.bar(1, 1)
    expected = {(1, -1), (1, 0), (1, 1)}
    assert line_dirs == expected


def test_bar_2():
    line_dirs = shapes.bar(2, 1)
    expected = {(2, -1), (2, 0), (2, 1)}
    assert line_dirs == expected


def test_bar_3():
    line_dirs = shapes.bar(2, 2)
    expected = {(2, -1), (2, 0), (2, 1), (3, -1), (3, 0), (3, 1)}
    assert line_dirs == expected
