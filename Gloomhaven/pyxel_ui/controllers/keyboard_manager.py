import pyxel

class KeyboardManager:
    def __init__(self, view_manager, server_client):
        self.view_manager = view_manager
        self.accept_input = False
        self.input = ""
        self.prompt = ""
        self.server_client = server_client

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
                self.view_manager.reset_keyboard()
                self.accept_input = False
                self.return_input_to_server()
                return 
                
        
            # Handle backspace
            elif pyxel.btnp(pyxel.KEY_BACKSPACE):
                if len(self.input) > 0:
                    self.input = self.input[:-1]
            
            # Handle space
            elif pyxel.btnp(pyxel.KEY_SPACE):
                self.input += ' '
            
            # Check for A-Z (ASCII 65-90)
            for key in range(pyxel.KEY_A, pyxel.KEY_Z + 1):
                if pyxel.btnp(key):
                    self.input += chr(key).lower()
            
            # Check for 0-9 (ASCII 48-57)
            for key in range(pyxel.KEY_0, pyxel.KEY_9 + 1):
                if pyxel.btnp(key):
                    self.input += chr(key)

            self.print_keyboard(self.input)

    def print_keyboard(self, keyboard_input):
        self.view_manager.update_keyboard(self.prompt + "\n" + keyboard_input)

    def get_keyboard_input(self, prompt):
        # clear out input
        self.input = ""
        self.accept_input = True
        self.prompt = prompt

    def return_input_to_server(self):
        self.server_client.post_user_input(self.input)
