import pygame as pg

from textoverlays import BaseTextOverlay, FONT_PATH

BACKGROUND_COLOR = 5, 142, 32

# TODO: settings menu


class TopBarMenu(BaseTextOverlay):
    """Bar at the top of the screen with score and high score text."""

    def __init__(self,
                 current_score: int,
                 high_score: int,
                 size: tuple[int, int]) -> None:
        self.current_score = current_score
        self.high_score = high_score if high_score else "N/A"  # if no high score, display N/A
        super().__init__(
                text_lines=[f"Score: {self.current_score}  High Score: {self.high_score}"],
                font_sizes=[30],
                pos=(0, 0),
                anchor="topleft",
                font_color="black",
                bg_color=BACKGROUND_COLOR,
                bg_size=size,
                line_centering=True
        )

    def update_rect(self):
        self.__init__(
                current_score=self.current_score,
                high_score=self.high_score,
                size=self.rect.size
        )

class SettingsMenu(BaseTextOverlay):
    """Menu for changing settings."""

    def __init__(self,
                 size: tuple[int, int],
                 anchor: str = "center",
                 title_font_size: int = 70,
                 settings_font_size: int = 50,
                 font_color: str | tuple[int, int, int] = "black",
                 bg_color: str | tuple[int, int, int] = "gray") -> None:
        pass

