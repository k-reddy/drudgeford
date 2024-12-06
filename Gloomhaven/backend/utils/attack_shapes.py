def circle(radius: int):
    directions = set()
    for i in range(radius + 1):
        for j in range(radius + 1):
            directions.add((i, j))
            directions.add((-i, -j))
            directions.add((i, -j))
            directions.add((-i, j))
    return directions


def line(length: int):
    direction = (1, 0)
    directions = set()
    for i in range(1, length + 1):
        coord_to_add = [dir_coord * i for dir_coord in direction]
        directions.add(tuple(coord_to_add))
    return directions


def bar(offset: int, depth: int):
    directions = set()
    for i in range(offset, depth + offset):
        for j in range(-1, 2):
            directions.add((i, j))
    return directions


def arc(length: int):
    directions = set()
    x = 0
    for i in range(length):
        directions.add((i + 1, x))
        if i < length // 2:
            x += 1
        elif i > length // 2:
            x -= 1
    return directions


def cone(length: int):
    directions = set()
    for y in range(length + 1):
        for x in range(y):
            directions.add((y, -x))
            directions.add((y, x))
            directions.add((y, 0))
    return directions


def ring(radius):
    """Creates a ring shape with the given radius.
    Only includes cells at exactly the specified radius (outer edge only).

    Args:
        radius (int): The radius of the ring

    Returns:
        set: Set of (x,y) coordinates forming a ring
    """
    shape = set()
    # Add all points at distance radius from center
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            # Use manhattan distance for consistent spacing
            if abs(x) + abs(y) == radius:
                shape.add((x, y))
    return shape


def is_circle_or_ring(shape):
    # sometimes we remove (0,0), so add just in case
    shape.add((0, 0))
    max_coord = max(max(abs(x), abs(y)) for x, y in shape)
    circle_points = circle(max_coord)
    ring_points = ring(max_coord)
    return shape == circle_points or shape == ring_points


def is_circle(shape):
    # sometimes we remove (0,0), so add just in case
    shape.add((0, 0))
    max_coord = max(max(abs(x), abs(y)) for x, y in shape)
    circle_points = circle(max_coord)
    return shape == circle_points


def print_shape(shape):
    print_str = ""
    ymin = min([y for y, _ in shape])
    xmin = min([x for _, x in shape])
    ymax = max([y for y, _ in shape])
    xmax = max([x for _, x in shape])
    for i in range(min(0, ymin), max(0, ymax) + 1):
        line = ""
        for j in range(min(0, xmin), max(0, xmax) + 1):
            if (i, j) == (0, 0):
                line += "@ "
            elif (i, j) in shape:
                line += "* "
            else:
                line += "  "
        print_str += line.rstrip() + "\n"
    return print_str


def get_all_directional_rotations(shape):
    transforms = [
        lambda x, y: (x, y),
        lambda x, y: (x, y - 1),
        lambda x, y: (y + 1, -x),
        lambda x, y: (y, -x),
        lambda x, y: (y - 1, -x),
        lambda x, y: (-x, -y - 1),
        lambda x, y: (-x, -y),
        lambda x, y: (-x, -y + 1),
        lambda x, y: (-y - 1, x),
        lambda x, y: (-y, x),
        lambda x, y: (-y + 1, x),
        lambda x, y: (x, y + 1),
    ]
    print(f"shape in shapes.get_all_directional_values: {shape}")
    all_shapes = {}
    for i, transform in enumerate(transforms):
        all_shapes[i] = [transform(x, y) for x, y in shape]
    return all_shapes


def print_all_directions(shape):
    """Prints the shape rotated in all 8 directions."""
    rotations = get_all_directional_rotations(shape)

    for direction, rotated_shape in rotations.items():
        print(f"Direction {direction}:")
        print(print_shape(rotated_shape))
        print(rotated_shape)


# Example usage with a simple line
def demo_directional_rotations():
    # Create a vertical line
    # vertical_line = line((1, 0), 3)
    vertical_line = cone(2)

    print_all_directions(vertical_line)
