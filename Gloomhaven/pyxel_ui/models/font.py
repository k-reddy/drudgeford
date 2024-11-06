from PIL import Image, ImageDraw, ImageFont
import os

class PixelFont:
    def __init__(self, pyxel, font_path):
        """Initialize Press Start 2P font"""
        self.medium_font = ImageFont.truetype(font_path, 8)
        self.large_font = ImageFont.truetype(font_path, 12)
        self.pyxel = pyxel
        
    def get_line_height(self, size="medium"):
        """Get the line height for a given font size"""
        if size == "small":
            return 10  # Increased from 8
        elif size == "medium":
            return 14  # Increased from 10
        else:  # large
            return 18  # Increased from 14
            
    def get_text_width(self, text, size="medium"):
        """
        Get the width of text in pixels for the given size
        
        Args:
            text: Text to measure
            size: "small", "medium", or "large"
        
        Returns:
            Width in pixels
        """
        if size == "small":
            return len(text) * 4  # Pyxel's built-in font is 4 pixels wide
            
        font = self.medium_font if size == "medium" else self.large_font
        bbox = font.getbbox(text)
        padding = max(2, 8 if size == "medium" else 12 // 4)
        return bbox[2] - bbox[0] + padding * 2
        
    def wrap_text(self, text, max_width, size="medium"):
        """
        Wrap text to fit within max_width pixels
        
        Args:
            text: Text to wrap
            max_width: Maximum width in pixels
            size: Font size to use for measurement
            
        Returns:
            List of lines that fit within max_width
        """
        if max_width is None:
            return text.split('\n')
            
        lines = []
        for paragraph in text.split('\n'):
            words = paragraph.split()
            if not words:
                lines.append('')
                continue
                
            current_line = words[0]
            current_width = self.get_text_width(current_line, size)
            
            for word in words[1:]:
                word_width = self.get_text_width(' ' + word, size)
                
                if current_width + word_width <= max_width:
                    current_line += ' ' + word
                    current_width += word_width
                else:
                    lines.append(current_line)
                    current_line = word
                    current_width = self.get_text_width(word, size)
                    
            lines.append(current_line)
            
        return lines
            
    def draw_text(self, x, y, text, col, size="medium", max_width=None):
        """
        Draw text at the specified position with given size. Supports multi-line text
        and optional width-based line wrapping.
        
        Args:
            pyxel: Pyxel instance
            text: Text to draw (can include newlines)
            x: X coordinate
            y: Y coordinate
            col: Color
            size: "small", "medium", or "large"
            max_width: Optional maximum width in pixels. Text will wrap if it exceeds this width.
        """
        pyxel = self.pyxel
        
        # Split and wrap text into lines
        lines = self.wrap_text(str(text), max_width, size)
        current_y = y
        line_height = self.get_line_height(size)
        
        for line in lines:
            if size == "small":
                pyxel.text(x, current_y, line, col)
                current_y += line_height
                continue
                
            # Select the appropriate font based on size
            font = self.medium_font if size == "medium" else self.large_font
            font_size = 8 if size == "medium" else 12
            
            # Get text size first to create minimum sized image
            bbox = font.getbbox(line)
            
            # Add padding to prevent cutoff
            padding = max(2, font_size // 4)  # Scale padding with font size
            w = bbox[2] - bbox[0] + padding * 2
            h = bbox[3] - bbox[1] + padding * 2
            
            # Create image with padding
            img = Image.new('1', (w, h), 0)
            draw = ImageDraw.Draw(img)
            
            # Draw text in white (1) on black (0) background, with padding offset
            draw.text((padding, padding), line, font=font, fill=1)
            
            # Convert to pixels in Pyxel
            pixels = img.load()
            for py in range(h):
                for px in range(w):
                    if pixels[px, py]:
                        pyxel.pset(x + px - padding, current_y + py - padding, col)
            
            current_y += line_height
    
    def get_text_height(self, text, size="medium", max_width=None):
        """
        Get the total height of text in pixels, including all lines
        
        Args:
            text: Text to measure (can include newlines)
            size: "small", "medium", or "large"
            max_width: Optional maximum width for word wrapping
        
        Returns:
            Height in pixels
        """
        lines = self.wrap_text(str(text), max_width, size)
        line_height = self.get_line_height(size)
        return len(lines) * line_height

