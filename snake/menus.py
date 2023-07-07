from textoverlays import TextOverlay

BACKGROUND_COLOR = 5, 142, 32


class TopMenuBar(TextOverlay):
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


class SettingsMenu(TextOverlay):
    """Menu for changing settings."""

    def __init__(self,
                 pos: tuple[int, int],
                 size: tuple[int, int],
                 title_font_size: int = 70,
                 settings_font_size: int = 20,
                 font_color: str | tuple[int, int, int] = "black",
                 bg_color: str | tuple[int, int, int] = "gray") -> None:
        lines = [" SETTINGS", "Difficulty:", "Master volume:", "Sound fx volume:", "Music volume:"]
        length = len(lines) - 1
        super().__init__(
                text_lines=lines,
                font_sizes=[title_font_size] + [settings_font_size] * length,
                font_color=font_color,
                pos=pos,
                bg_color=bg_color,
                bg_size=size,
                line_centering=False,
                line_padding=[25]*length,
                border_color="black",
                border_size_pad=10
        )

