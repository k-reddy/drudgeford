def circle(radius: int):
    directions = set()
    for i in range(radius + 1):
        for j in range(radius + 1):
            directions.add((i, j))
            directions.add((-i, -j))
            directions.add((i, -j))
            directions.add((-i, j))
    return directions


def line(direction: tuple, length: int):
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
            directions.add((x, y))
            directions.add((-x, y))
            directions.add((0, y))
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


# def rotate_90_degrees(shape):
#     """Rotates a shape 90 degrees clockwise around the origin.

#     Args:
#         shape (set): Set of (x,y) coordinates representing the shape

#     Returns:
#         set: New set of coordinates representing the rotated shape
#     """
#     rotated = set()
#     for x, y in shape:
#         # For 90-degree clockwise rotation: (x,y) -> (y,-x)
#         rotated.add((y, -x))
#     return rotated


def rotate_to_direction(shape, target_x, target_y):
    """
    Rotates a shape to point towards a specific adjacent square.
    The rotation is calculated based on the angle to the target square.

    Args:
        shape (set): Set of (x,y) coordinates representing the shape
        target_x (int): x coordinate of target direction (-1, 0, or 1)
        target_y (int): y coordinate of target direction (-1, 0, or 1)

    Returns:
        set: New set of coordinates representing the rotated shape
    """
    if target_x == 0 and target_y == 0:
        return shape

    # Direction dictionary mapping (target_x, target_y) to rotation transformation function
    DIRECTION_TRANSFORMS = {
        (0, 1): lambda x, y: (x, y),  # North
        (0, -1): lambda x, y: (-x, -y),  # South
        (1, 0): lambda x, y: (y, -x),  # East
        (-1, 0): lambda x, y: (-y, x),  # West
        (1, 1): lambda x, y: (x + y, y - x),  # Northeast
        (1, -1): lambda x, y: (x - y, x + y),  # Southeast
        (-1, 1): lambda x, y: (-x + y, x + y),  # Northwest
        (-1, -1): lambda x, y: (-x - y, -y + x),  # Southwest
    }

    # Get the appropriate transformation function
    transform = DIRECTION_TRANSFORMS.get((target_x, target_y))
    if transform is None:
        raise ValueError(f"Invalid direction: ({target_x}, {target_y})")

    # Apply the transformation to each point
    return {transform(x, y) for x, y in shape}


def get_all_directional_rotations(shape):
    """
    Gets all 8 directional rotations of a shape.

    Args:
        shape (set): Set of (x,y) coordinates representing the shape

    Returns:
        dict: Dictionary mapping direction names to rotated shapes
    """
    directions = {
        "N": (0, 1),
        "NE": (1, 1),
        "E": (1, 0),
        "SE": (1, -1),
        "S": (0, -1),
        "SW": (-1, -1),
        "W": (-1, 0),
        "NW": (-1, 1),
    }

    return {
        direction: rotate_to_direction(shape, x, y)
        for direction, (x, y) in directions.items()
    }


def print_all_directions(shape):
    """Prints the shape rotated in all 8 directions."""
    rotations = get_all_directional_rotations(shape)

    print("Original shape:")
    print(print_shape(shape))
    print()

    for direction, rotated_shape in rotations.items():
        print(f"Direction {direction}:")
        print(print_shape(rotated_shape))
        print()


# Example usage with a simple line
def demo_directional_rotations():
    # Create a vertical line
    # vertical_line = line((0, 1), 3)
    vertical_line = cone(2)

    print_all_directions(vertical_line)


# demo_directional_rotations()
