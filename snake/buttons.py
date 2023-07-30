import pygame as pg
from pygame_widgets.slider import Slider

from sprites import BaseSprite, load_image
from tools import get_resource_path


class Button(BaseSprite):
    """Base button class for inheritance."""

    def __init__(self,
                 size: tuple[int, int],
                 pos: tuple[int, int],
                 button_type: str,
                 anchor: str = "center") -> None:
        super().__init__(size=size, pos=pos, anchor=anchor)
        self.type = button_type
        self.nonhover_image = None
        self.hover_image = None
        # noinspection PyTypeChecker
        self.image = None
        self.was_hovered = False  # used to check if the button was hovered last frame

    def is_hovered(self, mouse_pos: tuple[int, int]) -> bool:
        """Boolean return for if the given mouse position is hovering over the button."""
        return self.rect.collidepoint(mouse_pos)

    def hover(self) -> None:
        """Called when the mouse is hovering over the button, brightens the button image."""
        # stop if the button has no hover image or is already hovered
        if (self.hover_image is None) or self.was_hovered:
            return
        self.image = self.hover_image
        self.rect = self.image.get_rect(center=self.rect.center)
        self.was_hovered = True

    def unhover(self) -> None:
        """Called when the mouse is no longer hovering over the button, resets the button image."""
        if self.hover_image is None:
            return
        self.image = self.nonhover_image
        self.rect = self.image.get_rect(center=self.rect.center)
        self.was_hovered = False


class ImageButton(Button):
    """Base image button class for inheritance."""

    def __init__(self,
                 pos: tuple[int, int],
                 size: tuple[int, int],
                 button_type: str,
                 image_path: str,
                 anchor: str = "center",
                 bg_color: str | tuple[int, int, int] | None = None) -> None:
        super().__init__(size=size, pos=pos, anchor=anchor, button_type=button_type)
        self.size = size
        self.image_path = image_path
        self.bg_color = bg_color
        if bg_color:  # todo?
            raise NotImplementedError("Background color for buttons not yet implemented.")

        # normal button
        self.nonhover_image = load_image(self.image_path, self.size)
        self.image = self.nonhover_image
        self.rect = self.get_rect(pos, anchor)

        # mouse hover button
        self.image_hover_path = self.image_path.replace(".png", "_hover.png")
        self.hover_image = load_image(self.image_hover_path, self.size)


class SettingsButton(ImageButton):
    """Settings button class."""

    def __init__(self,
                 pos: tuple[int, int],
                 size: tuple[int, int],
                 anchor: str = "center",
                 bg_color: str | tuple[int, int, int] | None = None) -> None:
        super().__init__(pos=pos,
                         size=size,
                         image_path=get_resource_path(r"../assets/images/settings.png"),
                         anchor=anchor,
                         bg_color=bg_color,
                         button_type="settings")


class VolumeSlider(Slider):
    """Volume slider class."""

    def __init__(self,
                 surface: pg.Surface,
                 pos: tuple[int, int],
                 size: tuple[int, int],
                 step: int = 1) -> None:
        """'pos' is the position of the top left corner. """
        super().__init__(win=surface,
                         x=pos[0],
                         y=pos[1],
                         width=size[0],
                         height=size[1],
                         min=0,
                         max=100,
                         step=step,
                         initial=100  # todo get initial from saved config.ini
                         )
