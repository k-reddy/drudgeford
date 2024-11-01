import character

def load_board(locations):
    for row_num, row in enumerate(locations):
        for col_num, el in enumerate(row):
            if el:
                if el isinstance(Character):
                    sprite=type(el).__name__+'.png'
                elif el isinstance(str):
                    sprite=el+".png"
                # send payload to pyxel


class_to_sprite_mapping = {
    "fire": "fire.png",
    character.Wizard: "wizard.png",
    character.Character: "generic_character.png"
}