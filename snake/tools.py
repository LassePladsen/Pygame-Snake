import configparser
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


def get_random_tile_pos(screen_size: tuple[tuple[int, int], tuple[int, int]],
                        tile_size: tuple[int, int],
                        max_dist: int,
                        reference_pos: tuple[int, int]) -> tuple[int, int]:
    """Returns a random position within the given distance from the snake head."""
    ref_x, ref_y = reference_pos
    x, y = ref_x, ref_y
    while abs(x - ref_x) < max_dist * tile_size[0] and abs(y - ref_y) < max_dist * tile_size[1]:
        x = randint(screen_size[0][0], screen_size[0][1])
        y = randint(screen_size[1][0], screen_size[1][1])
    return x, y


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

def create_file(file_path: str, content: str) -> None:
    """Creates a file with the given content."""
    with open(file_path, "w") as f:
        f.write(content)

def update_env(key: str, value: str) -> None:
    """Updates the value of a key in the .env file."""
    if not os.path.exists(r"..\.env"):
        create_file(r"..\.env", "HIGH_SCORE=0")  # create default .env file
    with open(r"..\.env", "r") as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.startswith(key):
            lines[i] = f"{key}={value}\n"
            break
    if not lines:  # empty
        lines.append(f"{key}={value}\n")
    with open(r"..\.env", "w") as f:
        f.writelines(lines)

def get_ini_value(filepath: str, header: str, key: str) -> str | None:
    """Returns the value of a key in the given .ini file. Returns None if not found.
    Is case-insensitive."""
    if not os.path.exists(filepath):  # file not found
        return
    config = configparser.ConfigParser()
    config.read(filepath)
    try:
        return config[header.upper()][key.lower()]
    except KeyError:  # header or key not found
        return
