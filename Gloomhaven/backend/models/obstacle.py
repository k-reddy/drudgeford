import random
from ..utils import attack_shapes as shapes

class TerrainObject:
    def __init__(self, round_num: int, obj_id: int):
        self.emoji = "Ⅹ"
        self.pyxel_sprite_name = "spores"
        self.round_placed = round_num
        self.duration = 2
        self.damage = 0
        self.id = obj_id
        
    def perform(self, row, col, board, affected_character):
        return

class Rock(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "🪨"
        self.pyxel_sprite_name = "boulder"

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

    def perform(self, row, col, board, affected_character):
        if random.random() < 0.25:
            if board.acting_character == affected_character:
                raise SlipAndLoseTurn("Slipped!")
            else:
                affected_character.lose_turn = True

class Trap(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "🗯️ "
        self.damage = 3
        self.pyxel_sprite_name="trap"
        self.duration = 1000
    
    def perform(self, row, col, board, affected_character):
        board.clear_terrain_square(row,col)

class PoisonShroom(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "🍄"
        self.pyxel_sprite_name = "poisonshroom"
        
    def perform(self, row, col, board, affected_character):
        board.clear_terrain_square(row, col)
        board.pyxel_manager.log.append("The mushroom exploded into spores!")
        board.add_effect_to_terrain_for_attack(Spores, row, col, shapes.circle(1))

class Spores(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "🍄"
        self.pyxel_sprite_name = "spores"
        self.damage = 1

class Wall(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "🪨"
        self.pyxel_sprite_name = "boulder"
        self.duration = 1000

class Shadow(TerrainObject):
    def __init__(self, round_num, obj_id):
        super().__init__(round_num, obj_id)
        self.emoji = "⚫️"
        self.pyxel_sprite_name = "shadow"

class SlipAndLoseTurn(Exception):
    pass