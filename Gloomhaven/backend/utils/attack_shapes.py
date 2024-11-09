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

def bar(offset: int, depth: int):
    directions = set()
    for i in range(offset, depth+offset):
        for j in range(-1, 2):
            directions.add((i, j))
    return directions

def arc(length: int):
    directions = set()
    x = 0
    for i in range(length):
        directions.add((i+1, x))
        if i < length//2:
            x += 1
        elif i > length//2:
            x -= 1
    return directions

def cone(length: int):
    directions = set()
    for y in range(length+1):
        for x in range(y):
            directions.add((x,y))
            directions.add((-x,y))
            directions.add((0,y))
    return directions
    
def print_shape(shape):
    print_str = ''
    ymin = min([y for y, _ in shape])
    xmin = min([x for _, x in shape])
    ymax = max([y for y, _ in shape])
    xmax = max([x for _, x in shape])
    for i in range(min(0,ymin), max(0,ymax)+1):
        for j in range(min(0,xmin), max(0,xmax)+1):
            if (i,j) == (0,0):
                print_str += "@ "
            elif (i,j) in shape:
                print_str += '* '
            else:
                print_str += "  "
        print_str+="\n"
    return print_str
