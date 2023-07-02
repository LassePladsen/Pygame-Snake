import pygame as pg

from tools import resource


def get_sound(relative_path: str, volume) -> pg.mixer.Sound | None:
    """Returns a pygame sound file."""
    if not relative_path:
        return
    path = resource.get_resource_path(f"../assets/sounds/{relative_path}")
    sound = pg.mixer.Sound(path)
    sound.set_volume(volume)
    return sound


def play_sound(relative_path: str, volume, loops=0) -> None:
    """Plays a pygame sound file."""
    sound = get_sound(relative_path, volume)
    sound.set_volume(volume)
    sound.play(loops)
