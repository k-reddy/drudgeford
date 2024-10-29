def circle(radius: int):
    directions = set()
    for i in range(radius + 1):
        for j in range(radius + 1):
            directions.add((i, j))
            directions.add((-i, -j))
            directions.add((i, -j))
            directions.add((-i, j))
    return directions