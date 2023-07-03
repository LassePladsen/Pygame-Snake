import os
import sys
from random import randint

import pygame as pg
from PIL import Image


def png_to_ico(png_file, ico_file=None):
    if ico_file is None:
        ico_file = png_file.replace(".png", ".ico")
    Image.open(png_file).save(ico_file)


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller --onefile."""
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.abspath(os.path.join(base_path, relative_path))


def get_sound(relative_path: str, volume) -> pg.mixer.Sound | None:
    """Returns a pygame sound file."""
    if not relative_path:
        return
    path = get_resource_path(f"../assets/sounds/{relative_path}")
    sound = pg.mixer.Sound(path)
    sound.set_volume(volume)
    return sound


def play_sound(relative_path: str, volume, loops=0) -> None:
    """Plays a pygame sound file."""
    sound = get_sound(relative_path, volume)
    sound.set_volume(volume)
    sound.play(loops)


def get_random_tile_pos(screen_size: tuple[int, int],
                        tile_size: tuple[int, int],
                        max_dist: int,
                        head_pos: tuple[int, int]) -> tuple[int, int]:
    """Returns a random position within the given distance from the snake head."""
    x, y = head_pos
    food_x, food_y = x, y
    while abs(food_x - x) < max_dist * tile_size[0] and abs(food_y - y) < max_dist * tile_size[1]:
        food_x = randint(0, screen_size[0])
        food_y = randint(0, screen_size[1])
    # Check if outside the window
    if food_x < 0:
        food_x = 0
    elif food_x > screen_size[0]:
        food_x = screen_size[0]
    if food_y < 0:
        food_y = 0
    elif food_y > screen_size[1]:
        food_y = screen_size[1]
    return food_x, food_y


def get_center_tile_pos(pos: tuple[int, int], tile_size: tuple[int, int]) -> tuple[int, int]:
    """Returns the center position of the nearest tile with given size."""
    x, y = pos
    center_x, center_y = x, y  # default value
    width, height = tile_size
    # Calculate the nearest tile center
    if (x + width / 2) % width != 0:
        center_x = round(x / width) * width + width // 2
    if (y + height / 2) % height != 0:
        center_y = round(y / height) * height + height // 2
    return center_x, center_y
