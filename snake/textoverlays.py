import pygame as pg

from tools import get_resource_path

FONT_PATH = get_resource_path("../assets/fonts/ThaleahFat.ttf")


class BaseTextOverlay(pg.sprite.Sprite):
    """Base class for text overlays for inheritance."""

    def __init__(self,
                 text_lines: list[str],
                 font_sizes: list[int],
                 pos: tuple[int, int],
                 line_padding: list[int] | bool = True,
                 anchor: str = "center",
                 font_color: str | tuple[int, int, int] = "red",
                 bg_color: str | tuple[int, int, int] = None,
                 bg_size: tuple[int, int] = None,
                 line_centering: list[int] | bool = False) -> None:
        """line_centering is a list of line int indices to center on the screen.
        If false or empty, no lines are centered. If True all lines are centered.

        line_padding is a list of extra padding int values between lines.
         If false or empty, no extra padding is used."""
        super().__init__()
        # default values for line_centering is a bool
        if line_centering is False:
            line_centering = []
        elif line_centering is True:
            line_centering = list(range(len(text_lines)))
        self.line_centering = line_centering
        self.pos = pos
        self.text_lines = text_lines
        self.font_sizes = font_sizes
        self._anchor = anchor

        # Create text surface
        fonts = [
            pg.font.Font(FONT_PATH, size)
            for size in font_sizes
        ]
        rendered_lines = [font.render(line, True, font_color) for font, line in zip(fonts, text_lines)]

        # default values for line_padding:
        if isinstance(line_padding, bool):  # line_padding is bool -> no list given, use default padding
            line_padding = [0] * (len(text_lines) - 1)
        if len(line_padding) != len(text_lines) - 1:
            raise ValueError(f"Number of line paddings not matching number of lines.")

        # Create background surface
        if bg_size:
            width, height = bg_size
        else:
            width = max(rendered_line.get_width() for rendered_line in rendered_lines)
            height = sum(rendered_line.get_height() for rendered_line in rendered_lines) + sum(line_padding)
        self.image = pg.Surface((width, height), pg.SRCALPHA)
        if bg_color:
            self.image.fill(bg_color)

        no_lines = len(rendered_lines)
        # y positions for lines from font heights and padding
        y = [0] * no_lines  # first line is always at the top
        for i in range(no_lines - 1):
            prev_y = y[i]
            prev_h = rendered_lines[i].get_height()
            next_h = rendered_lines[i + 1].get_height()
            # y add: half of of the current fonts height + half of the next fonts height + any optional padding
            y[i + 1] = prev_y + prev_h // 2 + next_h // 2 + line_padding[i]

        # x positions for lines from centering or not:
        if line_centering:
            x = []
            for i, rendered_line in enumerate(rendered_lines):
                if i in line_centering:
                    x.append((width - rendered_line.get_width()) // 2)  # center line
        else:
            x = [0] * no_lines  # all lines default to left
        self.image.blits([(rendered_line, (x, y)) for rendered_line, x, y in zip(rendered_lines, x, y)])
        self.rect = self.get_rect(self.pos, self._anchor)

    def get_rect(self,
                 pos: tuple[int, int],
                 anchor: str = "center") -> pg.rect.Rect:
        """Returns a sprite rect at a given position."""
        anchor_positions = {
            "topleft": self.image.get_rect(topleft=pos),
            "topright": self.image.get_rect(topright=pos),
            "bottomleft": self.image.get_rect(bottomleft=pos),
            "bottomright": self.image.get_rect(bottomright=pos),
            "center": self.image.get_rect(center=pos),
        }
        if (rect := anchor_positions.get(anchor)) is None:
            raise ValueError(f"Invalid anchor position: '{anchor}'.\n"
                             f" Valid positions are: {[i for i in anchor_positions.keys()]}")
        return rect


class GameOverOverlay(BaseTextOverlay):
    """Game over screen class."""

    def __init__(self,
                 current_score: int,
                 high_score: int,
                 size: tuple[int, int],
                 font_size: int = 70) -> None:
        self.current_score = current_score
        self.high_score = high_score if high_score else "N/A"  # if no high score, display N/A
        lines = ["Game Over!", f"Score: {self.current_score}  High Score: {self.high_score}",
                 "Press ENTER/SPACE to restart"]
        super().__init__(
                text_lines=lines,
                font_sizes=[font_size, font_size // 2, font_size // 2],
                pos=size,
                anchor="center",
                font_color="red",
                line_centering=True
        )


class PauseOverlay(BaseTextOverlay):
    """Pause screen class."""

    def __init__(self,
                 size: tuple[int, int],
                 anchor: str = "center",
                 font_size: int = 70,
                 font_color: str | tuple[int, int, int] = "red") -> None:
        lines = ["PAUSED", "Press any key to resume..."]
        super().__init__(
                text_lines=lines,
                font_sizes=[font_size, font_size // 2],
                pos=size,
                anchor=anchor,
                font_color=font_color,
                line_centering=True
        )
