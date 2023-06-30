import pygame as pg

from tools.resource import get_resource_path
from tools.tile import get_center_tile_pos, get_random_tile_pos

# Constants:
TILE_SIZE = 32, 32
SNAKE_COLOR = 224, 164, 54
FOOD_SIZE = TILE_SIZE


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
                 sprite_type: str,
                 size: tuple[int, int],
                 pos: tuple[int, int],
                 anchor: str = "center") -> None:
        pg.sprite.Sprite.__init__(self)
        self._anchor = anchor
        self.type = sprite_type
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
        match anchor:
            case "topleft":
                return self.image.get_rect(topleft=pos)
            case "topright":
                return self.image.get_rect(topright=pos)
            case "bottomleft":
                return self.image.get_rect(bottomleft=pos)
            case "bottomright":
                return self.image.get_rect(bottomright=pos)
            case "center" | _:
                return self.image.get_rect(center=pos)

    def move(self) -> None:
        """Placeholder move method for inheritance."""
        pass


class SnakeSegment(BaseSprite):
    """Base snake body part sprite class for inheritance."""

    def __init__(self,
                 sprite_type: str,
                 pos: tuple[int, int],
                 anchor: str = "center",
                 direction: str = "right",
                 next_segment: BaseSprite = None) -> None:
        match direction.lower():
            case "up" | "down" | "left" | "right":
                self.direction = direction
            case _:
                raise ValueError(f"Invalid direction: '{direction}'.")
        self.next_segment = next_segment
        super().__init__(sprite_type=sprite_type,
                         size=TILE_SIZE,
                         pos=pos,
                         anchor=anchor)

    def move(self) -> None:
        """Move the snake sprite in the direction it is facing by one tile size."""
        previous_pos = self.pos
        match self.direction.lower():
            case "up":
                self.pos = (self.rect.x, self.rect.y - TILE_SIZE[1])
            case "down":
                self.pos = (self.rect.x, self.rect.y + TILE_SIZE[1])
            case "left":
                self.pos = (self.rect.x - TILE_SIZE[0], self.rect.y)
            case "right":
                self.pos = (self.rect.x + TILE_SIZE[0], self.rect.y)
            case _:
                raise ValueError(f"Invalid direction: '{self.direction}'.")
        # move next segment
        if self.next_segment is not None:
            self.next_segment.move()
            self.next_segment.pos = previous_pos

    def turn(self, direction: str) -> None:
        """Turn the snake sprite to face the given direction. Prevents the snake from doing a u-turn."""
        match direction, self.direction:
            case "up", "left":
                self.rotate(-90)
            case "up", "right":
                self.rotate(90)
            case "down", "left":
                self.rotate(90)
            case "down", "right":
                self.rotate(-90)
            case "left", "up":
                self.rotate(90)
            case "left", "down":
                self.rotate(-90)
            case "right", "up":
                self.rotate(-90)
            case "right", "down":
                self.rotate(90)
            case _, _:
                return
        self.direction = direction

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
                 next_segment: SnakeSegment = None) -> None:
        img_path = get_resource_path(r"..\assets\images\head.png")
        self.image = pg.image.load(img_path)
        self.rect = self.image.get_rect()
        super().__init__(sprite_type="head",
                         pos=pos,
                         anchor=anchor,
                         direction=direction,
                         next_segment=next_segment)


class Tail(SnakeSegment):
    """Snake tail sprite class."""

    def __init__(self,
                 pos: tuple[int, int],
                 anchor: str = "center",
                 direction: str = "right",
                 next_segment: SnakeSegment = None) -> None:
        img_path = get_resource_path(r"..\assets\images\tail.png")
        self.image = pg.image.load(img_path)
        self.rect = self.image.get_rect()
        super().__init__(sprite_type="tail",
                         pos=pos,
                         anchor=anchor,
                         direction=direction,
                         next_segment=next_segment)


class Body(SnakeSegment):
    """Snake body sprite class."""

    def __init__(self,
                 pos: tuple[int, int],
                 anchor: str = "center",
                 direction: str = "right",
                 prev_segment: SnakeSegment = None) -> None:
        self.image = pg.Surface(TILE_SIZE)
        self.image.fill(SNAKE_COLOR)
        self.rect = self.image.get_rect()
        super().__init__(sprite_type="body",
                         pos=pos,
                         anchor=anchor,
                         direction=direction,
                         next_segment=prev_segment)


class Food(BaseSprite):
    """Food sprite class."""

    def __init__(self,
                 screen_size: tuple[int, int],
                 max_dist: int,
                 head_pos: tuple[int, int]) -> None:
        img_path = get_resource_path(r"..\assets\images\food.png")
        self.image = pg.image.load(img_path)
        self.rect = self.image.get_rect()
        pos = get_random_tile_pos(screen_size,
                                  TILE_SIZE,
                                  max_dist,
                                  head_pos)
        super().__init__(sprite_type="food",
                         size=FOOD_SIZE,
                         pos=pos)
