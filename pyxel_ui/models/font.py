from types import ModuleType
from typing import Dict, List, Tuple
import re
from PIL import Image, ImageDraw, ImageFont


class PixelFont:
    def __init__(self, pyxel: ModuleType, font_path: str):
        """Initialize Press Start 2P font"""
        self.medium_font = ImageFont.truetype(font_path, 8)
        self.large_font = ImageFont.truetype(font_path, 12)
        self.pyxel = pyxel
        # Cache of (text, size) -> (pixels, width)
        # pixels are relative to (0,0) origin
        # width is exact bbox width for positioning
        self.cache: Dict[Tuple[str, str], Tuple[List[Tuple[int, int]], int]] = {}

    def get_line_height(self, size="medium"):
        """Get the line height for a given font size"""
        if size == "small":
            return 10
        elif size == "medium":
            return 14
        else:  # large
            return 18

    def get_text_width(self, text: str, size="medium"):
        """Get the width of text in pixels for the given size"""
        if size == "small":
            return len(text) * 4

        # Remove color tags for width calculation
        text_no_tags = re.sub(r"<color:\s*\d+>|</color>", "", text)
        font = self.medium_font if size == "medium" else self.large_font
        bbox = font.getbbox(text_no_tags)
        return bbox[2] - bbox[0]

    def wrap_text(self, text: str, max_width, size="medium"):
        """
        Wrap text to fit within max_width pixels, properly handling color tags
        across line breaks.

        Args:
            text: Text to wrap (can include color tags)
            max_width: Maximum width in pixels
            size: Font size to use for measurement

        Returns:
            List of lines that fit within max_width
        """
        if max_width is None:
            return text.split("\n")

        lines = []
        for paragraph in text.split("\n"):
            if not paragraph:
                lines.append("")
                continue

            # Split into segments preserving color tags
            segments = []
            current_pos = 0
            current_color = None

            while current_pos < len(paragraph):
                # Check for color start tag
                color_start = re.match(r"<color:\s*(\d+)>", paragraph[current_pos:])
                if color_start:
                    current_color = color_start.group(1)
                    current_pos += len(color_start.group(0))
                    continue

                # Check for color end tag
                if paragraph[current_pos:].startswith("</color>"):
                    current_color = None
                    current_pos += len("</color>")
                    continue

                # Find next space or tag
                next_space = paragraph.find(" ", current_pos)
                next_color_start = paragraph.find("<color:", current_pos)
                next_color_end = paragraph.find("</color>", current_pos)

                # Find the nearest delimiter
                delimiters = [
                    pos
                    for pos in [next_space, next_color_start, next_color_end]
                    if pos != -1
                ]
                next_break = min(delimiters) if delimiters else len(paragraph)

                word = paragraph[current_pos:next_break]
                if word:  # Only add non-empty segments
                    segments.append((word, current_color))
                current_pos = next_break

                # Add space as separate segment if we broke at a space
                if next_break == next_space:
                    current_pos += 1
                    segments.append((" ", current_color))

            # Build lines from segments
            current_line = []
            current_width = 0

            for text_segment, color in segments:
                # Calculate width of this segment
                measure_text = text_segment
                segment_width = self.get_text_width(measure_text, size)

                # If adding this segment would exceed max_width
                if current_width + segment_width > max_width and current_line:
                    # Complete the current line
                    line_text = ""
                    active_color = None

                    for line_segment, seg_color in current_line:
                        if seg_color != active_color:
                            if active_color is not None:
                                line_text += "</color>"
                            if seg_color is not None:
                                line_text += f"<color:{seg_color}>"
                            active_color = seg_color
                        line_text += line_segment

                    if active_color is not None:
                        line_text += "</color>"

                    lines.append(line_text)

                    # Start new line with this segment
                    current_line = [(text_segment, color)]
                    current_width = segment_width
                else:
                    current_line.append((text_segment, color))
                    current_width += segment_width

            # Add the last line if there is one
            if current_line:
                line_text = ""
                active_color = None

                for line_segment, seg_color in current_line:
                    if seg_color != active_color:
                        if active_color is not None:
                            line_text += "</color>"
                        if seg_color is not None:
                            line_text += f"<color:{seg_color}>"
                        active_color = seg_color
                    line_text += line_segment

                if active_color is not None:
                    line_text += "</color>"

                lines.append(line_text)

        return lines

    def parse_color_tags(self, text: str, default_color: int) -> List[Tuple[str, int]]:
        """Parse text with color tags into segments of (text, color)"""
        segments = []
        current_pos = 0

        # Updated pattern to specifically match color tags or any text
        pattern = r"<color:\s*(\d+)>(.*?)</color>|(.*?(?=<color:|$))"

        for match in re.finditer(pattern, text):
            if match.group(3) is not None:  # Plain text
                if match.group(3):  # Only add if non-empty
                    segments.append((match.group(3), default_color))
            elif match.groups()[0]:  # Colored text
                color = int(match.group(1))
                content = match.group(2)
                segments.append((content, color))

        return segments

    def cache_text(self, text: str, size: str) -> Tuple[List[Tuple[int, int]], int]:
        """Generate and cache pixel positions for text"""
        cache_key = (text, size)
        if cache_key in self.cache:
            return self.cache[cache_key]

        if size == "small":
            width = len(text) * 4
            # For small size, we don't cache pixels since it uses built-in font
            return ([], width)

        font = self.medium_font if size == "medium" else self.large_font
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        # Create image with no padding
        img = Image.new("1", (width, height), 0)
        draw = ImageDraw.Draw(img)

        # Draw text aligned to top-left
        draw.text((0, 0), text, font=font, fill=1)

        # Store pixel positions relative to (0,0)
        pixels = []
        for py in range(height):
            for px in range(width):
                if img.getpixel((px, py)):
                    pixels.append((px, py))

        self.cache[cache_key] = (pixels, width)
        return (pixels, width)

    def draw_text(
        self, x: int, y: int, text: str, col: int, size="medium", max_width=None
    ) -> List[Tuple[int, int, int]]:
        """
        Draw text at the specified position with given size. Supports multi-line text,
        optional width-based line wrapping, and color tags.

        Args:
            x: X coordinate
            y: Y coordinate
            text: Text to draw (can include newlines and color tags)
            col: Default color (used for text without color tags)
            size: "small", "medium", or "large"
            max_width: Optional maximum width in pixels. Text will wrap if it exceeds this width.

        Returns:
            List of tuples (x, y, color) for each pixel
        """
        if not text:
            return []

        all_pixels = []
        current_y = y
        line_height = self.get_line_height(size)

        # Split and wrap text into lines
        lines = self.wrap_text(str(text), max_width, size)

        for line in lines:
            if size == "small":
                self.pyxel.text(x, current_y, line, col)
                current_y += line_height
                continue

            current_x = x
            segments = self.parse_color_tags(line, col)

            for segment_text, color in segments:
                cached_pixels, width = self.cache_text(segment_text, size)

                # Offset cached pixels to current position and include color
                segment_pixels = [
                    (px + current_x, py + current_y, color) for px, py in cached_pixels
                ]

                # Draw pixels with segment color
                for px_x, px_y, px_color in segment_pixels:
                    self.pyxel.pset(px_x, px_y, px_color)

                all_pixels.extend(segment_pixels)
                current_x += width

            current_y += line_height

        return all_pixels

    def redraw_text(self, text_pixels: List[Tuple[int, int, int]]) -> None:
        """Redraw cached pixel positions with their stored colors"""
        if not text_pixels:
            return
        for px_x, px_y, px_color in text_pixels:
            self.pyxel.pset(px_x, px_y, px_color)

    def get_text_height(self, text: str, size="medium", max_width=None):
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
