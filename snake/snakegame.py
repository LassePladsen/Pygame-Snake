import logging
import sys

import pygame as pg

import sprites
from tools.resource import get_resource_path

logging.basicConfig(level=logging.DEBUG)


def quit_game() -> None:
    """Quits the game."""
    pg.quit()
    sys.exit()


class SnakeGame:
    """Class containing snake game logic and data."""

    DIRECTIONS = {  # Mapping key presses to directions
        pg.K_UP: "up",
        pg.K_DOWN: "down",
        pg.K_LEFT: "left",
        pg.K_RIGHT: "right",
        pg.K_w: "up",
        pg.K_s: "down",
        pg.K_a: "left",
        pg.K_d: "right"
    }

    def __init__(self,
                 screen_size: tuple[int, int],
                 screen_title: str,
                 fps: int) -> None:
        pg.init()
        self.screen_size = screen_size
        self.screen_title = screen_title
        self.fps = fps
        self._pause = True  # game starts paused until user presses a button
        pg.display.set_caption(self.screen_title)
        pg.display.set_icon(pg.image.load(get_resource_path(r"..\assets\images\icon.png")))

        x, y = int(screen_size[0] / 2) - 1 * sprites.TILE_SIZE[0], int(screen_size[1] / 2)
        self._tail = sprites.Tail((x - sprites.TILE_SIZE[0], y))
        self._head = sprites.Head((x, y), prev_segment=self._tail)
        self.snake_segments = []
        # self.snake_length gets set as a property of the above lists length

        # Create food sprite at random position no closer than 8 tiles from the snake's head.
        self._food = sprites.Food(screen_size=self.screen_size,
                                  max_dist=8,
                                  head_pos=self._head.pos)
        self._sprite_group = sprites.SpriteGroup()
        self._add_sprites([self._head, self._tail, self._food])  # add to sprite group and snake_segment list

    @property
    def snake_length(self) -> int:
        """Returns the length of the snake."""
        return len(self.snake_segments)

    def _add_sprites(self, sprite_list: list[sprites.SnakeSegment | sprites.Food]) -> None:
        """Add given sprites to the sprite group and list."""
        # noinspection PyTypeChecker
        self._sprite_group.add(sprite_list)
        # dont add food to snake_segment list
        self.snake_segments += [sprite for sprite in sprite_list if isinstance(sprite, sprites.SnakeSegment)]

    def grow(self, amount: int) -> None:
        """Grows the snake by a given amount of tile sizes."""
        # noinspection PyPropertyAccess
        if amount == 0:
            return
        if amount < 0:
            raise ValueError("Growing amount must be greater than 0.")
        x, y = self._tail.pos
        size = sprites.TILE_SIZE
        tail = self.snake_segments.pop()
        new_sprites = []
        prev_segment = tail
        movement_values = {
            "right": (-amount * size[0], 0),
            "left": (amount * size[0], 0),
            "up": (0, amount * size[1]),
            "down": (0, -amount * size[1])
        }
        dx, dy = movement_values[self._head.direction]  # movement steps
        self._move_tail(dx, dy)
        for i in range(-amount + 1, 1):
            prev_segment = sprites.Body((x + i * dx, y + i * dy), prev_segment=prev_segment)
            new_sprites.append(prev_segment)
        self._add_sprites(new_sprites[::-1])  # reverse the list to add the segments in the correct order
        self._head.prev_segment = self.snake_segments[1]
        self.snake_segments.append(tail)

    def _move_tail(self, dx: int = 0, dy: int = 0):
        logging.debug(f"Moving tail by {dx, dy}. Old pos = {self._tail.pos}, New pos ="
                      f" {self._tail.pos[0] + dx, self._tail.pos[1] + dy}.")
        self._tail.pos = self._tail.pos[0] + dx, self._tail.pos[1] + dy

    def pause(self) -> None:
        """Pauses the game."""
        self._pause = True

    def unpause(self) -> None:
        """ Unpauses the game."""
        self._pause = False

    def turn(self, direction: str) -> None:
        """Turns the snake's head in a given direction."""
        if self._head.direction == direction:
            return
        logging.info(f"Attempting to turn snake {direction}.")
        self._head.direction = direction

    def _handle_events(self, events: list[pg.event.Event]) -> None:
        for event in events:
            match event.type:
                case pg.QUIT:
                    pg.quit()
                    exit()
                case pg.KEYDOWN:
                    self._handle_key_press(event.key)

    def _handle_key_press(self, key: int) -> None:
        """Handles key presses."""
        if key == pg.K_ESCAPE:  # pause or resume the game
            self._pause = not self._pause
            # todo: add a pause screen/text overlay
        elif key in self.DIRECTIONS:
            self.turn(self.DIRECTIONS[key])
            self.unpause()

    def _update_screen(self, screen: pg.surface.Surface, background: pg.surface.Surface) -> None:
        """Updates the screen."""
        screen.blit(background, (0, 0))
        self._sprite_group.draw(screen)
        pg.display.update()

    def run(self) -> None:
        """Runs the game loop"""
        screen = pg.display.set_mode(self.screen_size)
        clock = pg.time.Clock()
        background = pg.image.load(get_resource_path(r"..\assets\images\background.png"))
        while True:
            clock.tick(self.fps)
            logging.debug(f"[head.pos, tail.pos] = [{self._head.pos}, {self._tail.pos}]")
            self._handle_events(pg.event.get())
            if not self._pause:
                self._head.move()
            self._update_screen(screen, background)
