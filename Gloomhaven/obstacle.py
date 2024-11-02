import random
import attack_shapes as shapes

class TerrainObject:
    def __init__(self, round_num: int, obj_id: int):
        self.emoji = "Ⅹ"
        self.pyxel_sprite_name = "spores"
        self.round_placed = round_num
        self.duration = 2
        self.damage = 0
        self.id = obj_id
    
    def perform(self, row, col, board):
        return

class Rock(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "🪨"
        self.pyxel_sprite_name = "poisonshroom"

class Fire(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "🔥"
        self.pyxel_sprite_name = "fire"
        self.damage = 1

class Ice(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "🧊"
        self.pyxel_sprite_name = "ice"

    def perform(self, row, col, board):
        if random.random() < 0.25:
            raise SlipAndLoseTurn("Slipped!")
        else:
            return 0

class Trap(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "🗯️ "
        self.damage = 3
    
    def perform(self, row, col, board):
        board.terrain[row][col] = None

class PoisonShroom(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "🍄"
        self.pyxel_sprite_name = "poisonshroom"
        
    def perform(self, row, col, board):
        board.terrain[row][col] = None
        board.log.append("The mushroom exploded into spores!")
        board.add_effect_to_terrain_for_attack(Spores, row, col, shapes.circle(1))

class Spores(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "🍄"
        self.pyxel_sprite_name = "spores"
        self.damage = 1


class SlipAndLoseTurn(Exception):
    pass