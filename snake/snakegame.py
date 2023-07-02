import logging
import sys

import pygame as pg

import sprites
from queue_ import Queue
from tools import resource, sound

logging.basicConfig(level=logging.INFO)


def quit_game() -> None:
    """Quits the pygame and the program."""
    pg.quit()
    sys.exit()


class SnakeGame:
    """Class containing snake game logic and data."""

    DIRECTION_KEYS = {  # Mapping key presses to directions
        pg.K_UP: "up",
        pg.K_DOWN: "down",
        pg.K_LEFT: "left",
        pg.K_RIGHT: "right",
        pg.K_w: "up",
        pg.K_s: "down",
        pg.K_a: "left",
        pg.K_d: "right"
    }

    RESTART_KEYS = {  # Mapping key presses to restart
        pg.K_RETURN: True,
        pg.K_SPACE: True
    }

    def __init__(self,
                 screen_size: tuple[int, int],
                 title: str,
                 fps: int) -> None:
        pg.init()
        if screen_size[0] > 896 or screen_size[1] > 640:
            raise ValueError("Maximum image size is 896x640.")
        elif screen_size[0] < 290 or screen_size[1] < 290:
            raise ValueError("Minimum image size is 290x290")
        if any((screen_size[i] % sprites.TILE_SIZE[i]) != 0 for i in range(2)):
            raise ValueError(f"Screen size must be a multiple of the tile size: '{sprites.TILE_SIZE}'.")
        self.screen_size = screen_size
        self.screen_title = title
        self.fps = fps
        self._current_score = 0
        self._high_score = 0  # todo get high score from a saved data file
        self._pause = True  # game starts paused until user presses a button
        self._game_over = False
        self._key_pressed = False  # used to prevent multiple key presses per frame
        pg.display.set_caption(self.screen_title)
        pg.display.set_icon(pg.image.load(resource.get_resource_path(r"..\assets\images\icon.png")))

        # sound volumes and background music
        self.sound_volume = 0.5
        self.music_volume = 0.15
        self._background_music = sound.get_sound(
                "Abstraction - Three Red Hearts - Connected.wav",
                self.music_volume
        )

        self._tail, self._head, self._food = None, None, None
        self._initialize_sprites()

    def _initialize_sprites(self):
        x, y = self.screen_size[0] // 2 - sprites.TILE_SIZE[0], self.screen_size[1] // 2
        self._tail = sprites.Tail((x - sprites.TILE_SIZE[0], y))
        self._head = sprites.Head((x, y), prev_segment=self._tail)
        self.snake_segments = []

        # Create food sprite at random position no closer than 5 tiles from the snake's head.
        self._max_food_dist = 5
        self._food = sprites.Food(
                screen_size=self.screen_size,
                max_dist=self._max_food_dist,
                head_pos=self._head.pos)
        self._sprite_group = sprites.SpriteGroup()
        self._add_sprites([self._head, self._tail, self._food])  # add to sprite group and snake_segment list
        self.queue = Queue()  # queue for storing moves and key presses

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

    def grow(self, amount: int = 1) -> None:
        """Grows the snake by a given amount of body parts."""
        # noinspection PyPropertyAccess
        if amount < 0:
            raise ValueError("Growing amount must be greater than 0.")
        if amount == 0:
            return
        size = sprites.TILE_SIZE

        # move the tail
        self._tail = self.snake_segments.pop()
        movement_values = {
            "right": (-amount * size[0], 0),
            "left": (amount * size[0], 0),
            "up": (0, amount * size[1]),
            "down": (0, -amount * size[1])
        }
        dx, dy = movement_values[self._tail.direction]  # movement steps for tail
        self._move_tail(dx, dy)

        # Add new body parts
        x, y = self._tail.pos
        new_sprites = []
        for i in range(-amount + 1, 1):
            logging.debug(f"Adding body at ({x - dx}, {y - dy}), new snake length = {self.snake_length}")
            new_sprites.append(sprites.Body(pos=(x - dx, y - dy)))
            x, y = new_sprites[-1].pos
            dx, dy = movement_values[new_sprites[-1].direction]
        new_sprites.reverse()  # reverse the list to add the segments in the correct order
        self._add_sprites(new_sprites)
        self.snake_segments.append(self._tail)

        direction_fixes = {  # maps change in x or y position to a new direction fix
            (0, -1): "up",
            (0, 1): "down",
            (-1, 0): "left",
            (1, 0): "right"
        }
        # set prev_segment and fix directions for all snake parts except tail:
        for i in range(0, len(self.snake_segments) - 1):
            self.snake_segments[i].prev_segment = self.snake_segments[i + 1]
            dx = self.snake_segments[i].pos[0] - self.snake_segments[i + 1].pos[0]
            dy = self.snake_segments[i].pos[1] - self.snake_segments[i + 1].pos[1]
            dx = 1 if dx else 0  # normalize the values
            dy = 1 if dy else 0
            direction = direction_fixes.get((dx, dy))
            if direction is None:
                raise ValueError(f"Got no new part direction {self.snake_segments[i]} for (dx, dy) = {dx, dy}.")
            self.snake_segments[i].direction = direction
        self.snake_segments[1].direction = self._head.direction

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

    def game_over(self) -> None:
        """Ends the game."""
        logging.info(f"Game over! Score: {self._current_score}, High score: {self._high_score}")
        self._game_over = True
        self.pause()
        self._background_music.stop()
        sound.play_sound("death.wav", self.sound_volume)
        sound.play_sound("Arcade Retro Game Over Sound Effect💤 sounds.wav", self.sound_volume - 0.2)
        self._show_game_over_screen()

    def _show_game_over_screen(self) -> None:
        """Creates the game over image."""
        # noinspection PyTypeChecker
        self._sprite_group.add(sprites.GameOverScreen(
                self._current_score,
                self._high_score,
                (self.screen_size[0] // 2, self.screen_size[1] // 2)
        ))
        # todo
        pass

    def restart(self) -> None:
        """Restarts the game and resets all values except high score."""
        self._game_over = False
        self._background_music.play(-1)
        # noinspection PyTypeChecker
        self._initialize_sprites()
        logging.info("Game restarted.")

    def turn(self, direction: str) -> None:
        """Turns the snake's head in a given direction. Is used in self._handle_key_press()."""
        if self._head.direction == direction:
            return
        self._head.direction = direction

    def _handle_events(self, events: list[pg.event.Event]) -> None:
        for event in events:
            match event.type:
                case pg.QUIT:
                    quit_game()
                case pg.KEYDOWN:
                    self._handle_key_press(event.key)

    def _handle_key_press(self, key: int) -> None:
        """Handles key presses."""
        if key == pg.K_ESCAPE:  # _pause or resume the game
            self._pause = not self._pause
            # todo: add a _pause image/text overlay
        elif key in self.DIRECTION_KEYS:
            frames = 1 if self._key_pressed else 0
            self.queue.add(frames, [(self, f"turn('{self.DIRECTION_KEYS[key]}')")])
            self.unpause()
            self._key_pressed = True
        elif key in self.RESTART_KEYS and self._game_over:
            self.restart()


    def _update_screen(self, screen: pg.surface.Surface, background: pg.surface.Surface) -> None:
        """Updates the image."""
        screen.blit(background, (0, 0))
        self._sprite_group.draw(screen)
        pg.display.update()

    def handle_collision(self) -> None:
        """Checks any collisions between all the sprites and handle the collision logic.
            Head + (Body or tail)-> Game Over
            Head + Food -> Grow snake and spawn new food"""
        for i, segment in enumerate(self.snake_segments[1:]):  # check for collision with body or tail
            if self._head.rect.colliderect(segment.rect):
                if i == 1:  # should not be possible to collide with the second segment
                    self._head.direction = segment.direction
                else:
                    self.game_over()
                    return
        if self._head.rect.colliderect(self._food.rect):
            self.eat()

    def eat(self) -> None:
        """Grows the snake by one body part and replaces the food with a new one."""
        self.grow()
        self._current_score += 1
        # noinspection PyTypeChecker
        self._sprite_group.remove(self._food)
        while self._food.pos in [sprite.pos for sprite in self._sprite_group]:  # make sure the food is not on the snake
            self._food = sprites.Food(screen_size=self.screen_size,
                                      max_dist=self._max_food_dist,
                                      head_pos=self._head.pos)
        self._add_sprites([self._food])
        sound.play_sound("eat.wav", self.sound_volume)

    def run(self) -> None:
        """Runs the game loop"""
        screen = pg.display.set_mode(self.screen_size)
        clock = pg.time.Clock()
        background = pg.image.load(resource.get_resource_path(r"..\assets\images\background.png"))
        self._background_music.play(-1)
        while True:
            clock.tick(self.fps)
            self._key_pressed = False
            self._handle_events(pg.event.get())
            if not self._pause and not self._game_over:
                self.queue.handle()
                self.queue.update()
                self._head.move()
                self.handle_collision()
            self._update_screen(screen, background)
