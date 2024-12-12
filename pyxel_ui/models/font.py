from types import ModuleType
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont  # type: ignore


class PixelFont:
    def __init__(self, pyxel: ModuleType, font_path: str):
        """Initialize Press Start 2P font"""
        self.medium_font = ImageFont.truetype(font_path, 8)
        self.large_font = ImageFont.truetype(font_path, 12)
        self.pyxel = pyxel
        self.word_colors = {}  # {"damage": 5, "health": 3, "attack": 4, "Attack": 4}

    def get_line_height(self, size="medium"):
        """Get the line height for a given font size"""
        if size == "small":
            return 10
        elif size == "medium":
            return 14
        else:  # large
            return 18

    def get_text_width(self, text, size="medium"):
        """Get the width of text in pixels for the given size"""
        if size == "small":
            return len(text) * 4

        font = self.medium_font if size == "medium" else self.large_font
        bbox = font.getbbox(text)
        padding = max(2, 4 if size == "medium" else 12)
        return bbox[2] - bbox[0] + padding * 2

    def wrap_text(self, text, max_width, size="medium"):
        """Wrap text to fit within max_width pixels"""
        if max_width is None:
            return text.split("\n")

        lines = []
        for paragraph in text.split("\n"):
            words = paragraph.split(" ")
            if not words:
                lines.append("")
                continue

            current_line = words[0]
            current_width = self.get_text_width(current_line, size)

            for word in words[1:]:
                next_piece = " " + word
                word_width = self.get_text_width(next_piece, size)

                if current_width + word_width <= max_width:
                    current_line += next_piece
                    current_width += word_width
                else:
                    lines.append(current_line)
                    current_line = word
                    current_width = self.get_text_width(word, size)

            lines.append(current_line)

        return lines

    def get_word_positions(self, text: str) -> List[Tuple[int, int, int]]:
        """
        Find positions of colored words in text
        Returns list of (start_pos, end_pos, color)
        """
        if not self.word_colors:
            return []

        positions = []
        text_lower = text.lower()

        for word, color in self.word_colors.items():
            word = word.lower()
            start = 0
            while True:
                # Find next occurrence of word
                pos = text_lower.find(word, start)
                if pos == -1:
                    break

                # Verify it's a whole word by checking boundaries
                before = pos == 0 or not text_lower[pos - 1].isalnum()
                after = (
                    pos + len(word) >= len(text)
                    or not text_lower[pos + len(word)].isalnum()
                )

                if before and after:
                    positions.append((pos, pos + len(word), color))
                start = pos + 1

        return sorted(positions)

    def redraw_text(self, col: int, text_pixels: List[Tuple[int, int, int]]) -> None:
        """Redraw text pixels with their saved colors"""
        if not text_pixels:
            return
        for px_x, px_y, px_col in text_pixels:
            self.pyxel.pset(px_x, px_y, px_col)

    def draw_text(
        self, x: int, y: int, text: str, col: int, size="medium", max_width=None
    ) -> List[Tuple[int, int, int]]:
        """Draw text with colored words"""
        text_pixels = []
        lines = self.wrap_text(str(text), max_width, size)
        current_y = y

        for line in lines:
            word_positions = self.get_word_positions(line)

            if size == "small":
                current_x = x
                last_pos = 0

                # Draw text segments with appropriate colors
                for start, end, word_col in word_positions:
                    # Draw text before the colored word
                    if start > last_pos:
                        segment = line[last_pos:start]
                        self.pyxel.text(current_x, current_y, segment, col)
                        for dx in range(len(segment) * 4):
                            text_pixels.append((current_x + dx, current_y, col))
                        current_x += len(segment) * 4

                    # Draw the colored word
                    segment = line[start:end]
                    self.pyxel.text(current_x, current_y, segment, word_col)
                    for dx in range(len(segment) * 4):
                        text_pixels.append((current_x + dx, current_y, word_col))
                    current_x += len(segment) * 4
                    last_pos = end

                # Draw remaining text
                if last_pos < len(line):
                    segment = line[last_pos:]
                    self.pyxel.text(current_x, current_y, segment, col)
                    for dx in range(len(segment) * 4):
                        text_pixels.append((current_x + dx, current_y, col))

            else:  # medium and large fonts
                font = self.medium_font if size == "medium" else self.large_font
                padding = max(2, 8 if size == "medium" else 12)

                # Create image for the whole line
                bbox = font.getbbox(line)
                w = bbox[2] - bbox[0] + padding * 2
                h = bbox[3] - bbox[1] + padding * 2
                img = Image.new("1", (w, h), 0)
                draw = ImageDraw.Draw(img)
                draw.text((padding, padding), line, font=font, fill=1)
                pixels = img.load()

                # Draw with colors based on word positions
                for py in range(h):
                    for px in range(w):
                        if not pixels[px, py]:
                            continue

                        pixel_x = x + px - padding
                        pixel_y = current_y + py - padding

                        # Determine which word this pixel belongs to
                        char_pos = int((px - padding) * len(line) / (w - padding * 2))
                        pixel_col = col

                        for start, end, word_col in word_positions:
                            if start <= char_pos < end:
                                pixel_col = word_col
                                break

                        text_pixels.append((pixel_x, pixel_y, pixel_col))
                        self.pyxel.pset(pixel_x, pixel_y, pixel_col)

            current_y += self.get_line_height(size)

        return text_pixels

    def get_text_height(self, text, size="medium", max_width=None):
        """Get the total height of text in pixels"""
        lines = self.wrap_text(str(text), max_width, size)
        line_height = self.get_line_height(size)
        return len(lines) * line_height
