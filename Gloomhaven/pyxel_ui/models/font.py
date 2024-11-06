from PIL import Image, ImageDraw, ImageFont
import os

class PixelFont:
    def __init__(self, pyxel):
        """Initialize Press Start 2P font"""
        font_path = os.path.join("..", "assets", "Press_Start_2P", "PressStart2P-Regular.ttf")
        self.medium_font = ImageFont.truetype(font_path, 8)
        self.large_font = ImageFont.truetype(font_path, 12)
        self.pyxel = pyxel
            
    def draw_text(self, x, y, text, col, size="medium"):
        """
        Draw text at the specified position with given size
        
        Args:
            pyxel: Pyxel instance
            text: Text to draw
            x: X coordinate
            y: Y coordinate
            col: Color
            size: "small", "medium", or "large"
        """
        pyxel = self.pyxel
        if size == "small":
            pyxel.text(x, y, text, col)
            return
            
        # Select the appropriate font based on size
        font = self.medium_font if size == "medium" else self.large_font
        font_size = 8 if size == "medium" else 12
        
        # Get text size first to create minimum sized image
        bbox = font.getbbox(text)
        
        # Add padding to prevent cutoff
        padding = max(2, font_size // 4)  # Scale padding with font size
        w = bbox[2] - bbox[0] + padding * 2
        h = bbox[3] - bbox[1] + padding * 2
        
        # Create image with padding
        img = Image.new('1', (w, h), 0)
        draw = ImageDraw.Draw(img)
        
        # Draw text in white (1) on black (0) background, with padding offset
        draw.text((padding, padding), text, font=font, fill=1)
        
        # Convert to pixels in Pyxel
        pixels = img.load()
        for py in range(h):
            for px in range(w):
                if pixels[px, py]:
                    pyxel.pset(x + px - padding, y + py - padding, col)

# Example usage:
# import pyxel

# class App:
#     def __init__(self):
#         BITS=32
#         pyxel.init(320, 320)
        
#         # Create single font instance
#         self.font = PixelFont(pyxel)
        
#         pyxel.run(self.update, self.draw)
    
#     def update(self):
#         if pyxel.btnp(pyxel.KEY_Q):
#             pyxel.quit()
    
#     def draw(self):
#         pyxel.cls(0)
        
#         # Show different sizes
#         y = 5
#         self.font.draw_text(5, y, "SMALL", 8, "small")
        
#         y += 16
#         self.font.draw_text(5, y, "Medium 8px", 9, "medium")
        
#         y += 20
#         self.font.draw_text(5, y, "LARGE 12", 10, "large")
        
#         # Show some game-style text with the medium font
#         y += 25
#         self.font.draw_text( 5, y, "SCORE:1000",11, "medium")
        
#         # Show that it handles lowercase too
#         y += 15
#         self.font.draw_text(5, y,  "Hello World!", 12, "medium")

# App()