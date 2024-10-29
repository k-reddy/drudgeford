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
    for i in range(1,length+1):
        coord_to_add = [dir_coord*i for dir_coord in direction]
        directions.add(tuple(coord_to_add))
    return directions