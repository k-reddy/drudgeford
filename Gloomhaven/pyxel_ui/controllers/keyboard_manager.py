import pyxel

class KeyboardManager:
    def __init__(self, view_manager):
        self.view_manager = view_manager
        
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # Add controls for scrolling action cards
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.view_manager.scroll_action_cards_right()
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.view_manager.scroll_action_cards_left()