from random import randint


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
