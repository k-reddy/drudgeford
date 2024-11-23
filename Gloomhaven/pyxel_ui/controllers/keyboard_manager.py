import pyxel

class KeyboardManager:
    def __init__(self, view_manager):
        self.view_manager = view_manager
        self.accept_input = False
        self.current_input = ""
        self.prompt = ""

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        # Add controls for scrolling action cards
        if pyxel.btnp(pyxel.KEY_RIGHT):
            self.view_manager.scroll_action_cards_right()
        if pyxel.btnp(pyxel.KEY_LEFT):
            self.view_manager.scroll_action_cards_left()
        
        if self.accept_input:
            # Handle enter
            if pyxel.btnp(pyxel.KEY_RETURN):
                self.accept_input = False
                self.prompt = ""
                return 
        
            # Handle backspace
            elif pyxel.btnp(pyxel.KEY_BACKSPACE):
                if len(self.current_input) > 0:
                    self.current_input = self.current_input[:-1]
            
            # Handle space
            elif pyxel.btnp(pyxel.KEY_SPACE):
                self.current_input += ' '
            
            # Check for A-Z (ASCII 65-90)
            for key in range(pyxel.KEY_A, pyxel.KEY_Z + 1):
                if pyxel.btnp(key):
                    self.current_input += chr(key).lower()
            
            # Check for 0-9 (ASCII 48-57)
            for key in range(pyxel.KEY_0, pyxel.KEY_9 + 1):
                if pyxel.btnp(key):
                    self.current_input += chr(key)

            self.print_keyboard(self.current_input)

        
    def print_keyboard(self, keyboard_input):
        self.view_manager.update_keyboard(self.prompt + "\n" + keyboard_input, True)

    def get_keyboard_input(self, prompt):
        # clear out input
        self.current_input = ""
        self.accept_input = True
        self.prompt = prompt
        self.print_keyboard("")
