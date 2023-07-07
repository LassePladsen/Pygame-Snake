# todo:
# - settings button.
# - difficulty button on settings menu.
# - volume bars on settings menu.

import pygame as pg

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
        self.image = None
        self.hover_image = None
        self.was_hovered = False  # used to check if the button was hovered last frame


    def is_hovered(self, mouse_pos: tuple[int, int]) -> bool:
        """Returns True if the mouse is hovering over the button."""
        res = self.rect.collidepoint(mouse_pos)
        self.was_hovered = res
        return res

    def hover(self) -> None:
        """Called when the mouse is hovering over the button, brightens the button image."""
        self.rect = self.hover_image.get_rect(center=self.rect.center)

    def unhover(self) -> None:
        """Called when the mouse is no longer hovering over the button, resets the button image."""
        self.rect = self.image.get_rect(center=self.rect.center)


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
        self.image = load_image(self.image_path, self.size)
        self.rect = self.get_rect(pos, anchor)

        # mouse hover button
        self.hover_image = self.image.convert_alpha()
        self.hover_image.fill("white", special_flags=pg.BLEND_RGBA_MULT)

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

