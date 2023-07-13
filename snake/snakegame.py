import logging
import sys
import os
import configparser

from dotenv import load_dotenv
import pygame as pg

import sprites
import textoverlays
import menus
import buttons
from queue_handler import Queue
import tools

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

    CONFIG_PATH = tools.get_resource_path(r"../config.ini")

    PROFILES_PATH = tools.get_resource_path(r"../profiles.ini")

    def __init__(self, title: str) -> None:
        pg.init()

        # Get parameters from config.ini
        if not os.path.exists(self.CONFIG_PATH):
            # Create default config values and .ini file if it doesn't exist already.
            screen_size = 640, 480
            difficulty = "medium"
            master_volume = 1
            sfx_volume = 1
            music_volume = 1
            config = configparser.ConfigParser()
            config["SETTINGS"] = {
                "screen_size": f"{screen_size[0]}, {screen_size[1]}",
                "difficulty": difficulty,
                "master_volume": master_volume,
                "sfx_volume": sfx_volume,
                "music_volume": music_volume
            }
            with open(self.CONFIG_PATH, "w") as f:
                config.write(f)
        else:
            screen_size = tools.get_ini_value(self.CONFIG_PATH, "SETTINGS", "screen_size").split(",")
            screen_size = int(screen_size[0]), int(screen_size[1])
            difficulty = tools.get_ini_value(self.CONFIG_PATH, "SETTINGS", "difficulty")
            master_volume = int(tools.get_ini_value(self.CONFIG_PATH, "SETTINGS", "master_volume"))
            sfx_volume = int(tools.get_ini_value(self.CONFIG_PATH, "SETTINGS", "sfx_volume"))
            music_volume = int(tools.get_ini_value(self.CONFIG_PATH, "SETTINGS", "music_volume"))

        # Check valid screen values
        if screen_size[0] > 896 or screen_size[1] > 640:
            raise ValueError("Maximum image size is 896x640.")
        elif screen_size[0] < 290 or screen_size[1] < 290:
            raise ValueError("Minimum image size is 290x290")
        if any((screen_size[i] % sprites.TILE_SIZE[i]) != 0 for i in range(2)):
            raise ValueError(f"Screen sizes must be a multiple of the tile size: '{sprites.TILE_SIZE}'.")

        # Check valid difficulty values
        if difficulty not in ("easy", "medium", "hard"):
            raise ValueError(f"Invalid difficulty value: '{difficulty}'."
                             f" Valid values are 'easy', 'medium', and 'hard'.")

        # Check valid volume values
        if master_volume < 0:
            raise ValueError(f"Invalid master volume value: '{master_volume}'."
                             f"Volumes must be greater than 0.")
        if sfx_volume < 0:
            raise ValueError(f"Invalid sfx volume value: '{sfx_volume}'."
                             f"Volumes must be greater than 0.")
        if music_volume < 0:
            raise ValueError(f"Invalid music volume value: '{music_volume}'."
                             f"Volumes must be greater than 0.")

        # Check valid fps value
        fps = tools.get_ini_value(self.PROFILES_PATH, difficulty, "fps")
        if not fps:
            match difficulty:
                case "easy":
                    fps = 6
                case "medium":
                    fps = 11
                case "hard":
                    fps = 16
            logging.warning(f"Missing fps value for difficulty '{difficulty}'."
                            f" Setting new default '{fps}'.")
        else:
            fps = int(fps)

        # Check valid growth score value
        growth_score = tools.get_ini_value(self.PROFILES_PATH, difficulty, "growth_score")
        if not growth_score:
            match difficulty:
                case "easy":
                    growth_score = 1
                case "medium":
                    growth_score = 10
                case "hard":
                    growth_score = 20
            logging.warning(f"Missing growth_score value for difficulty '{difficulty}'."
                            f" Setting new default '{growth_score}'.")
        else:
            growth_score = int(growth_score)

        # Config attributes
        self.screen_title = title
        self.screen_size = screen_size
        self.difficulty = difficulty
        self._fps = fps
        self._growth_score = growth_score

        # Screen surfaces
        self.screen = pg.display.set_mode((self.screen_size[0], self.screen_size[1] + sprites.TILE_SIZE[1]))
        self.background = pg.image.load(tools.get_resource_path(r"..\assets\images\background.png"))

        # Screen caption and icon
        pg.display.set_caption(self.screen_title)
        pg.display.set_icon(pg.image.load(tools.get_resource_path(r"..\assets\images\icon.png")))

        # Sound volumes and background music
        self.master_volume = master_volume
        self.sfx_volume = self.master_volume * sfx_volume * 0.5
        self.music_volume = self.master_volume * music_volume * 0.15
        self.music_title = "Abstraction - Three Red Hearts - Connected.wav"
        self._music = tools.get_sound(self.music_title, self.music_volume)

        # Scores
        self._current_score = 0
        if not os.path.exists(tools.get_resource_path(r"../.env")):
            tools.create_file(r"..\.env", "HIGH_SCORE=0")  # create default .env file
        load_dotenv(tools.get_resource_path(r"../.env"))

        if (hs := os.getenv("HIGH_SCORE")) is None:
            tools.update_env("HIGH_SCORE", "0")
            hs = 0
        self._high_score = int(hs)

        # Game states
        self._pause = True  # game starts paused until user presses a button
        self._game_over = False  # whether the player is dead
        self._key_pressed = False  # used to prevent multiple key presses per frame
        self._settings_showing = False  # whether the settings menu is showing

        # Initialize sprites
        self._head = None
        self._tail = None
        self._pause_screen = None
        self._food = None
        self._top_menu = None
        self._initialize_sprites()

    def _initialize_sprites(self):
        """Initializes all game sprites and adds it to the sprite group. Also initializes a new Queue instance."""
        # Snake head and tail:
        x, y = self.screen_size[0] // 2 - sprites.TILE_SIZE[0], self.screen_size[1] // 2
        self._tail = sprites.Tail((x - sprites.TILE_SIZE[0], y))
        self._head = sprites.Head((x, y), prev_segment=self._tail)

        # Top menu bar:
        self._top_menu = menus.TopMenuBar(
                current_score=self._current_score,
                high_score=self._high_score,
                size=(self.screen_size[0], sprites.TILE_SIZE[1]),
        )

        # Pause screen:
        self._pause_screen = textoverlays.PauseOverlay((self.screen_size[0] // 2, self.screen_size[1] // 2))

        # Settings button and menu:
        self._settings_button = buttons.SettingsButton(
                pos=(self.screen_size[0], 0),  # positioned top right corner of screen
                size=(sprites.TILE_SIZE[0], sprites.TILE_SIZE[1]),
                anchor="topright"
        )
        settings_menu_size = (self.screen_size[0] // 2, self.screen_size[1] // 2)  # size half the screen
        self._settings_menu = menus.SettingsMenu(
                pos=settings_menu_size,   # positioned middle of the screen
                size=settings_menu_size,
        )

        # Create food sprite at random position no closer than 5 tiles from the snake's head:
        self._max_food_dist = 5
        self._food = sprites.Food(
                screen_size=self.screen_size,
                max_dist=self._max_food_dist,
                head_pos=self._head.pos)

        # Sprite groups
        self._sprite_group = sprites.SpriteGroup()  # sprite group for all currently showing sprites
        self.snake_segments = []  # list of all currently showing snake segment sprites
        self.buttons = {}  # dict mapping currently showing button types to their corresponding showing button sprites

        # Add starting sprites to sprite group and snake_segment list:
        self._add_sprites([self._head, self._tail, self._food, self._top_menu, self._settings_button])

        # Queue for storing moves and key presses:
        self.queue = Queue()

    @property
    def snake_length(self) -> int:
        """Returns the current length of the snake. Has no setter"""
        return len(self.snake_segments)

    @property
    def fps(self) -> int:
        """Returns the game fps. Has no setter"""
        return self._fps

    @property
    def growth_score(self) -> int:
        """Returns the score given when the snake eats and grows. Has no setter"""
        return self._growth_score

    def _add_sprites(self, sprite_list: list[sprites.SnakeSegment | sprites.Food]) -> None:
        """Add given sprites to the sprite group and corresponding list."""
        # noinspection PyTypeChecker
        self._sprite_group.add(sprite_list)
        for sprite in sprite_list:
            if isinstance(sprite, sprites.SnakeSegment):
                self.snake_segments.append(sprite)
            elif isinstance(sprite, buttons.Button):
                self.buttons[sprite.type] = sprite

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
        if not self._game_over:
            logging.info("Pausing game.")
            self._sprite_group.add(self._pause_screen)  # show pause screen

    def unpause(self) -> None:
        """ Unpauses the game."""
        logging.info("unpausing game.")
        self._pause = False
        self._sprite_group.remove(self._pause_screen)

    def game_over(self) -> None:
        """Ends the game."""
        logging.info(f"Game over! Score: {self._current_score}, High score: {self._high_score}")
        self._game_over = True
        self.pause()
        self._music.stop()
        tools.play_sound("death.wav", self.sfx_volume)
        tools.play_sound("Arcade Retro Game Over Sound Effect💤 sounds.wav", self.sfx_volume - 0.2)
        tools.update_env("HIGH_SCORE", str(self._high_score))
        self._show_game_over_screen()  # create game over screen with updated scores

    def _show_game_over_screen(self) -> None:
        """Creates the game over image."""
        # noinspection PyTypeChecker
        self._sprite_group.add(textoverlays.GameOverOverlay(
                self._current_score,
                self._high_score,
                (self.screen_size[0] // 2, self.screen_size[1] // 2)
        ))

    def restart(self) -> None:
        """Restarts the game and resets all values except high score."""
        self._game_over = False
        self._pause = False
        self._current_score = 0
        self._music.play(-1)
        # noinspection PyTypeChecker
        self._initialize_sprites()
        logging.info("Game restarted.")

    def turn(self, direction: str) -> None:
        """Turns the snake's head in a given direction. Is used in self._handle_key_press()."""
        if self._head.direction == direction:
            return
        self._head.direction = direction

    def _handle_events(self) -> None:
        """Handles all pygame events such as quitting, key presses, mouse hovering and clicks."""
        events = pg.event.get()
        mouse_pos = pg.mouse.get_pos()
        for event in events:
            match event.type:
                case pg.QUIT:
                    quit_game()
                case pg.KEYDOWN:
                    self._handle_key_press(event.key)
                case pg.MOUSEBUTTONDOWN:
                    self._handle_mouse_press(mouse_pos)
        self._handle_mouse_hovering(mouse_pos)

    def _handle_key_press(self, key: int) -> None:
        """Handles key presses."""
        if key == pg.K_ESCAPE:  # _pause or resume the game
            self.unpause() if self._pause else self.pause()
        elif key in self.DIRECTION_KEYS:
            frames = 1 if self._key_pressed else 0
            self.queue.add(frames, [(self, f"turn('{self.DIRECTION_KEYS[key]}')")])
            if self._pause:
                self.unpause()
            self._key_pressed = True
        elif key in self.RESTART_KEYS and self._game_over:
            self.restart()
        # unpause for any other key press too
        elif self._pause:
            self.unpause()

    def _handle_mouse_press(self, mouse_pos: tuple[int, int]) -> None:
        """Handles mouse clicks."""
        for button_type, button in self.buttons.items():
            if button.is_hovered(mouse_pos):
                match button_type:
                    case "settings":
                        self._pause = True
                        self._settings_showing = True
                        # noinspection PyTypeChecker
                        self._sprite_group.add(self._settings_menu)
                    case "_":
                        raise NotImplementedError(f"Button type '{button_type}' is not yet implemented.")
            elif button.was_hovered:  # was hovered last frame -> unhover the button this frame
                button.unhover()


    def _handle_mouse_hovering(self, mouse_pos: tuple[int, int]) -> None:
        """Handles mouse hovering."""
        for button_type, button in self.buttons.items():
            if button.is_hovered(mouse_pos):
                button.hover()
            elif button.was_hovered:  # was hovered last frame -> unhover the button this frame
                button.unhover()

    def _update_screen(self) -> None:
        """Updates the screen surface."""
        self.screen.blit(self.background, (0, sprites.TILE_SIZE[1]))
        self._sprite_group.draw(self.screen)
        pg.display.update()

    def handle_collision(self) -> None:
        """Checks any collisions between all the sprites and handle the collision logic.
            Head + (Body or tail)-> Game Over
            Head + Food -> Grow snake and replace with new food at random position."""
        for i, segment in enumerate(self.snake_segments[1:]):  # check for collision with body or tail
            if self._head.rect.colliderect(segment.rect):
                if i == 1:  # should not be possible to turn in towards the second segment
                    self._head.direction = segment.direction
                else:
                    self.game_over()
                    # remove that body part to stop the head from dissapearing
                    self._sprite_group.remove(self.snake_segments[i + 1])
                    return
        if self._head.rect.colliderect(self._food.rect):
            self.eat()

    def update_scores(self, amount: int = 1) -> None:
        """Updates the current score, and the high score if the current is higher."""
        self._current_score += amount*self.growth_score
        self._top_menu.current_score = self._current_score
        if self._current_score > self._high_score:
            self._high_score = self._current_score
            self._top_menu.high_score = self._high_score
        self._top_menu.update_rect()

    def eat(self) -> None:
        """Grows the snake by one body part and replaces the food with a new one."""
        self.grow()
        self.update_scores()
        # noinspection PyTypeChecker
        self._sprite_group.remove(self._food)
        while self._food.pos in [sprite.pos for sprite in self._sprite_group]:  # make sure the food is not on the snake
            self._food = sprites.Food(screen_size=self.screen_size,
                                      max_dist=self._max_food_dist,
                                      head_pos=self._head.pos)
        self._add_sprites([self._food])
        tools.play_sound("eat.wav", self.sfx_volume)

    def run(self) -> None:
        """Runs the game loop"""
        clock = pg.time.Clock()
        self._music.play(-1)
        while True:
            clock.tick(self.fps)
            self._key_pressed = False
            self._handle_events()
            if not self._pause and not self._game_over:
                self.queue.handle()
                self.queue.update()
                self._head.move()
                self.handle_collision()
            self._update_screen()
