import pygame as pg

from tools import tile, resource

# Constants:
TILE_SIZE = 32, 32
SNAKE_COLOR = 224, 164, 54
FOOD_SIZE = TILE_SIZE


def load_image(path: str, size: tuple[int, int]) -> pg.surface.Surface:
    """Load an image from the given path and scale it to the given size."""
    image = pg.image.load(path)
    return pg.transform.scale(image, size)


class SpriteGroup(pg.sprite.Group):
    """Sprite group class."""

    def __init__(self):
        super().__init__()

    def move(self):
        """NOT CURRENTLY USED. Move all sprites in the group by one tile size in the direction the sprite is facing."""
        for sprite in self.sprites():
            if not isinstance(sprite, SnakeSegment):  # dont move the food
                continue
            sprite.move()


class BaseTextOverlay(pg.sprite.Sprite):
    """Base class for text overlays for inheritance."""
    def __init__(self,
                 text_lines: list[str],
                 font_sizes: list[int],
                 size: tuple[int, int],
                 anchor: str = "center",
                 font_color: str | tuple[int, int, int] = "red") -> None:
        super().__init__()
        self.size = size
        self.pos = size
        self.text_lines = text_lines
        self.font_sizes = font_sizes

        # Create text surface
        fonts = [
            pg.font.Font(resource.get_resource_path("../assets/fonts/ThaleahFat.ttf"), size)
            for size in font_sizes
        ]
        rendered_lines = [font.render(line, True, font_color) for font, line in zip(fonts, text_lines)]
        width = max(rendered_line.get_width() for rendered_line in rendered_lines)
        font_pad = fonts[0].get_height() // 5
        height = sum(rendered_line.get_height() for rendered_line in rendered_lines) + 2 * font_pad
        self.image = pg.Surface((width, height), pg.SRCALPHA)
        for i, rendered_line in enumerate(rendered_lines):
            x = (width - rendered_line.get_width()) // 2
            y = i * (rendered_line.get_height() + font_pad)
            self.image.blit(rendered_line, (x, y))
        self.rect = self.get_rect(self.pos, anchor)

    def get_rect(self,
                 pos: tuple[int, int],
                 anchor: str = "center") -> pg.rect.Rect:
        """Returns a sprite rect at a given position."""
        anchor_positions = {
            "topleft": self.image.get_rect(topleft=pos),
            "topright": self.image.get_rect(topright=pos),
            "bottomleft": self.image.get_rect(bottomleft=pos),
            "bottomright": self.image.get_rect(bottomright=pos),
            "center": self.image.get_rect(center=pos),
        }
        return anchor_positions.get(anchor, self.image.get_rect(center=pos))  # defaults to anchor center


class GameOverScreen(BaseTextOverlay):
    """Game over screen class."""
    def __init__(self,
                 current_score: int,
                 high_score: int,
                 size: tuple[int, int],
                 anchor: str = "center",
                 font_size: int = 70,
                 font_color: str | tuple[int, int, int] = "red") -> None:
        self.current_score = current_score
        self.high_score = high_score if high_score else "N/A"
        super().__init__(
                text_lines=["Game Over!", f"Score: {self.current_score}, High Score: {self.high_score}",
                            "Press ENTER/SPACE to restart"],
                font_sizes=[font_size, font_size // 2, font_size // 2],
                size=size,
                anchor=anchor,
                font_color=font_color
        )


class PauseScreen(BaseTextOverlay):
    """Pause screen class."""
    def __init__(self,
                 size: tuple[int, int],
                 anchor: str = "center",
                 font_size: int = 70,
                 font_color: str | tuple[int, int, int] = "red") -> None:
        super().__init__(
                text_lines=["PAUSED", "Press any key to resume..."],
                font_sizes=[font_size, font_size // 2],
                size=size,
                anchor=anchor,
                font_color=font_color
        )

def get_rect(self,
             pos: tuple[int, int],
             anchor: str = "center") -> pg.rect.Rect:
    """Returns a sprite rect at a given position."""
    anchor_positions = {
        "topleft": self.image.get_rect(topleft=pos),
        "topright": self.image.get_rect(topright=pos),
        "bottomleft": self.image.get_rect(bottomleft=pos),
        "bottomright": self.image.get_rect(bottomright=pos),
        "center": self.image.get_rect(center=pos),
    }
    return anchor_positions.get(anchor, self.image.get_rect(center=pos))  # defaults to anchor center


class BaseSprite(pg.sprite.Sprite):
    """Base sprite class for inheritance."""
    image: pg.surface.Surface = pg.Surface((0, 0))  # placeholder image surface
    rect: pg.rect.Rect = pg.Rect(0, 0, 0, 0)  # placeholder rect

    def __init__(self,
                 size: tuple[int, int],
                 pos: tuple[int, int],
                 anchor: str = "center") -> None:
        super().__init__()
        self._anchor = anchor
        self.image = pg.transform.scale(self.image, size)
        self.pos = tile.get_center_tile_pos(pos, TILE_SIZE)
        # self.rect gets set in the pos setter

    @property
    def pos(self) -> tuple[int, int]:
        """Returns the sprites position."""
        return self._pos

    @pos.setter
    def pos(self, new_pos: tuple[int, int]) -> None:
        """Sets the position attribute to the center of the nearest tile center,
         and also updates the sprites rect position with this new position."""
        self._pos = new_pos
        self.rect = self.get_rect(new_pos, self._anchor)

    def get_rect(self,
                 pos: tuple[int, int],
                 anchor: str = "center") -> pg.rect.Rect:
        """Returns a sprite rect at a given position."""
        anchor_positions = {
            "topleft": self.image.get_rect(topleft=pos),
            "topright": self.image.get_rect(topright=pos),
            "bottomleft": self.image.get_rect(bottomleft=pos),
            "bottomright": self.image.get_rect(bottomright=pos),
            "center": self.image.get_rect(center=pos),
        }
        return anchor_positions.get(anchor, self.image.get_rect(center=pos))  # defaults to anchor center

    def move(self) -> None:
        """Placeholder move method for inheritance."""
        pass


class SnakeSegment(BaseSprite):
    """Base snake body part sprite class for inheritance."""

    def __init__(self,
                 pos: tuple[int, int],
                 anchor: str = "center",
                 direction: str = "right",
                 prev_segment: BaseSprite = None) -> None:
        match direction.lower():
            case "up" | "down" | "left" | "right":
                self._direction = direction
            case _:
                raise ValueError(f"Invalid direction: '{direction}'.")
        super().__init__(size=TILE_SIZE,
                         pos=pos,
                         anchor=anchor)
        self.prev_segment = prev_segment

    def move(self) -> None:
        """Move the snake sprite in the direction it is facing by one tile size."""
        x, y = self.pos
        match self._direction.lower():
            case "up":
                self.pos = (x, y - TILE_SIZE[1])
            case "down":
                self.pos = (x, y + TILE_SIZE[1])
            case "left":
                self.pos = (x - TILE_SIZE[0], y)
            case "right":
                self.pos = (x + TILE_SIZE[0], y)
            case _:
                raise ValueError(f"Invalid direction: '{self._direction}'.")
        # check if outside the image
        self._handle_outside_bounds()
        # move next snake segment
        if self.prev_segment is not None:
            self.prev_segment.move()
            self.prev_segment.pos = x, y
            self.prev_segment.direction = self.direction  # turn the previous segment to face this segment

    def _handle_outside_bounds(self) -> None:
        """Check if the snake sprite is outside the image and move it to the opposite side if it is."""
        x, y = self.pos
        new_x, new_y = x, y
        screen_w, screen_h = pg.display.get_surface().get_size()
        tile_w, tile_h = TILE_SIZE
        if x - tile_w / 2 < 0:
            new_x = screen_w - tile_w / 2
        elif x > screen_w:
            new_x = tile_w / 2
        if y - tile_h / 2 < 0:
            new_y = screen_h - tile_h / 2
        elif y > screen_h:
            new_y = tile_h / 2
        self.pos = new_x, new_y

    @property
    def direction(self) -> str:
        """Returns the direction the snake sprite is facing."""
        return self._direction

    @direction.setter
    def direction(self, direction: str) -> None:
        """Turn the snake sprite to face the given direction. Prevents the snake from doing a u-turn."""
        allowed_turns = {  # initial key is current self.direction, nested key is desired given direction.
            "up": {"left": 90, "right": -90},
            "down": {"left": -90, "right": 90},
            "left": {"up": -90, "down": 90},
            "right": {"up": 90, "down": -90},
        }
        rotation_angle = allowed_turns.get(self._direction).get(direction)
        if rotation_angle is not None:
            self.rotate(rotation_angle)
            self._direction = direction

    def rotate(self, degrees: int) -> None:
        """Rotates the sprite a given degree. Positive degrees is counter-clockwise, negative is clockwise."""
        self.image = pg.transform.rotate(self.image, degrees)
        self.rect = self.get_rect(self.pos, self._anchor)


class Head(SnakeSegment):
    """Snake head sprite class."""

    def __init__(self,
                 pos: tuple[int, int],
                 anchor: str = "center",
                 direction: str = "right",
                 prev_segment: SnakeSegment = None) -> None:
        self.image = load_image(resource.get_resource_path(r"..\assets\images\head.png"), TILE_SIZE)
        super().__init__(pos=pos,
                         anchor=anchor,
                         direction=direction,
                         prev_segment=prev_segment)


class Tail(SnakeSegment):
    """Snake tail sprite class."""

    def __init__(self,
                 pos: tuple[int, int],
                 anchor: str = "center",
                 direction: str = "right") -> None:
        self.image = load_image(resource.get_resource_path(r"..\assets\images\tail.png"), TILE_SIZE)
        super().__init__(pos=pos,
                         anchor=anchor,
                         direction=direction,
                         prev_segment=None)


class Body(SnakeSegment):
    """Snake body sprite class."""

    def __init__(self,
                 pos: tuple[int, int],
                 anchor: str = "center",
                 direction: str = "right",
                 prev_segment: SnakeSegment = None) -> None:
        self.image = pg.Surface(TILE_SIZE)
        self.image.fill(SNAKE_COLOR)
        super().__init__(pos=pos,
                         anchor=anchor,
                         direction=direction,
                         prev_segment=prev_segment)

    def rotate(self, degrees: any) -> None:
        """No rotation needed for the body as it is a colored square sprite."""
        pass


class Food(BaseSprite):
    """Food sprite class."""

    def __init__(self,
                 screen_size: tuple[int, int],
                 max_dist: int,
                 head_pos: tuple[int, int]) -> None:
        pos = tile.get_random_tile_pos((screen_size[0] - TILE_SIZE[0], screen_size[1] - TILE_SIZE[1]),
                                       TILE_SIZE,
                                       max_dist,
                                       head_pos)
        self.image = load_image(resource.get_resource_path(r"..\assets\images\food.png"), TILE_SIZE)
        super().__init__(size=FOOD_SIZE,
                         pos=pos)
