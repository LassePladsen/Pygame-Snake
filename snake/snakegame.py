import logging
import pygame as pg

import sprites
from tools.resource import get_resource_path

logging.basicConfig(level=logging.DEBUG)


def quit_game() -> None:
    """Quits the game."""
    pg.quit()
    exit(0)


class SnakeGame:
    """Class containing snake game logic and data."""

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
        self._head = sprites.Head((x, y), next_segment=self._tail)
        self.snake_segments: list[sprites.SnakeSegment | sprites.Food] = [self._head, self._tail]
        # self.snake_length gets set as a property of the above lists length

        # Create food sprite at random position no closer than 8 tiles from the snake's head.
        self._food = sprites.Food(screen_size=self.screen_size,
                                  max_dist=8,
                                  head_pos=self._head.pos)
        self._sprite_group = sprites.SpriteGroup()
        self._add_sprites([self._head, self._tail, self._food])

    @property
    def snake_length(self) -> int:
        """Returns the length of the snake."""
        return len(self.snake_segments)

    def _add_sprites(self, sprite_list: list[sprites.SnakeSegment | sprites.Food]) -> None:
        """Add given sprites to the sprite group and list."""
        # noinspection PyTypeChecker
        self._sprite_group.add(sprite_list)
        self.snake_segments += sprite_list

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
        match self._head.direction:
            case "right":
                self._move_tail(x=-amount * size[0])
                for i in range(-amount+1, 1):
                    prev_segment = sprites.Body((x + i * size[0], y), prev_segment=prev_segment)
                    new_sprites.append(prev_segment)
            case "left":
                self._move_tail(x=amount * size[0])
                for i in range(-amount+1, 0):
                    prev_segment = sprites.Body((x - i * size[0], y), prev_segment=prev_segment)
                    new_sprites.append(prev_segment)
            case "up":
                self._move_tail(y=amount * size[1])
                for i in range(-amount+1, 0):
                    prev_segment = sprites.Body((x, y - i * size[1]), prev_segment=prev_segment)
                    new_sprites.append(prev_segment)
            case "down":
                self._move_tail(y=-amount * size[0])
                for i in range(-amount+1, 0):
                    prev_segment = sprites.Body((x, y + i * size[1]), prev_segment=prev_segment)
                    new_sprites.append(prev_segment)
        self._add_sprites(new_sprites)
        self.snake_segments.append(tail)

    def _move_tail(self, x: int = 0, y: int = 0):
        logging.debug(f"Moving tail by {x, y}. Old pos = {self._tail.pos}, New pos ="
                      f" {self._tail.pos[0] + x, self._tail.pos[1] + y}.")
        self._tail.pos = self._tail.pos[0] + x, self._tail.pos[1] + y

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
        logging.debug(f"Turning snake {direction}.")
        self._head.turn(direction)

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
        match key:
            case pg.K_ESCAPE:  # _pause or resume the game
                self._pause = not self._pause
                # todo: add a pause screen/text overlay
                return
            case pg.K_UP | pg.K_w:
                self.turn("up")
            case pg.K_DOWN | pg.K_s:
                self.turn("down")
            case pg.K_LEFT | pg.K_a:
                self.turn("left")
            case pg.K_RIGHT | pg.K_d:
                self.turn("right")
        self.unpause()

    def run(self) -> None:
        """Runs the game loop"""
        screen = pg.display.set_mode(self.screen_size)
        clock = pg.time.Clock()
        background = pg.image.load(get_resource_path(r"..\assets\images\background.png"))
        while True:
            clock.tick(self.fps)
            logging.debug(f"[head.pos, tail.pos] = [{self._head.pos}, {self._tail.pos}]")
            screen.blit(background, (0, 0))
            self._handle_events(pg.event.get())
            if not self._pause:
                self._head.move()
            self._sprite_group.draw(screen)
            pg.display.update()
