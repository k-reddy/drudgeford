import abc

class ViewSection(abc.ABC):
    def __init__(self, font, start_pos, bounding_coordinate):
        self.font = font
        self.start_pos = start_pos
        self.end_pos = start_pos
        self.bounding_coordinate = bounding_coordinate

    @abc.abstractmethod
    def draw(self):
        pass

class LogView(ViewSection):
    log: list[str] = []
    round_number: int = 0
    acting_character_name: str = ""
    max_log_lines: int = 5

    def draw(self) -> None:
        # only draw if you have something loaded
        if not (self.log or self.round_number > 0):
            return 
        
        log_line_y = self.start_pos[1]
        
        for line in [f"Round {self.round_number}, {self.acting_character_name}'s turn"] + self.log[
            -self.max_log_lines:
        ]:
            self.font.draw_text(
                self.start_pos[0],
                log_line_y,
                line,
                col=7,
                size="medium",
                max_width=self.bounding_coordinate[0]-self.start_pos[0]
            )
            line_height = self.font.get_text_height(line, size="medium", max_width=self.bounding_coordinate[0]-self.start_pos[0]) + 4
            log_line_y += line_height

