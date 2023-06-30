import pygame as pg

from tools.resource import get_resource_path
from tools.tile import get_center_tile_pos, get_random_tile_pos

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
        """Move all sprites in the group by one tile size in the direction the sprite is facing."""
        for sprite in self.sprites():
            if not isinstance(sprite, SnakeSegment):  # dont move the food
                continue
            sprite.move()


class BaseSprite(pg.sprite.Sprite):
    """Base sprite class for inheritance."""
    image: pg.surface.Surface = pg.Surface((0, 0))  # placeholder image surface
    rect: pg.rect.Rect = pg.Rect(0, 0, 0, 0)  # placeholder rect

    def __init__(self,
                 size: tuple[int, int],
                 pos: tuple[int, int],
                 anchor: str = "center") -> None:
        pg.sprite.Sprite.__init__(self)
        self._anchor = anchor
        self.image = pg.transform.scale(self.image, size)
        self.pos = get_center_tile_pos(pos, TILE_SIZE)
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
        self.rect = self.get_rect(self._pos, self._anchor)

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
        # move next snake segment
        if self.prev_segment is not None:
            self.prev_segment.move()
            self.prev_segment.pos = x, y

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
        """Rotates the sprite a given degree. Positive degrees is clockwise, negative is counter-clockwise."""
        self.image = pg.transform.rotate(self.image, degrees)
        self.rect = self.get_rect(self.pos, self._anchor)


class Head(SnakeSegment):
    """Snake head sprite class."""

    def __init__(self,
                 pos: tuple[int, int],
                 anchor: str = "center",
                 direction: str = "right",
                 prev_segment: SnakeSegment = None) -> None:
        super().__init__(pos=pos,
                         anchor=anchor,
                         direction=direction,
                         prev_segment=prev_segment)
        self.image = load_image(get_resource_path(r"..\assets\images\head.png"), TILE_SIZE)
        self.rect = self.image.get_rect()


class Tail(SnakeSegment):
    """Snake tail sprite class."""

    def __init__(self,
                 pos: tuple[int, int],
                 anchor: str = "center",
                 direction: str = "right",
                 next_segment: SnakeSegment = None) -> None:
        self.image = load_image(get_resource_path(r"..\assets\images\tail.png"), TILE_SIZE)
        self.rect = self.image.get_rect()
        super().__init__(pos=pos,
                         anchor=anchor,
                         direction=direction,
                         prev_segment=None)
        self.next_segment = next_segment

    def move(self) -> None:
        """Move the tail sprite in the direction it is facing by one tile size,
         and then rotate its direction to the next segments direction such that the next move follows it."""
        if self.next_segment is None:
            return
        super().move()
        self.direction = self.next_segment.direction


class Body(SnakeSegment):
    """Snake body sprite class."""

    def __init__(self,
                 pos: tuple[int, int],
                 anchor: str = "center",
                 direction: str = "right",
                 prev_segment: SnakeSegment = None) -> None:
        super().__init__(pos=pos,
                         anchor=anchor,
                         direction=direction,
                         prev_segment=prev_segment)
        self.image = pg.Surface(TILE_SIZE)
        self.image.fill(SNAKE_COLOR)
        self.rect = self.image.get_rect()

    def rotate(self, degrees: any) -> None:
        """No rotation needed for the body as it is a colored square sprite."""
        pass


class Food(BaseSprite):
    """Food sprite class."""

    def __init__(self,
                 screen_size: tuple[int, int],
                 max_dist: int,
                 head_pos: tuple[int, int]) -> None:
        pos = get_random_tile_pos(screen_size,
                                  TILE_SIZE,
                                  max_dist,
                                  head_pos)
        super().__init__(size=FOOD_SIZE,
                         pos=pos)
        self.image = load_image(get_resource_path(r"..\assets\images\food.png"), TILE_SIZE)
        self.rect = self.image.get_rect()
