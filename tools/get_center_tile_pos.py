def get_center_tile_pos(pos: tuple[int, int], tile_size: tuple[int, int]) -> tuple[int, int]:
    """Returns the center position of the nearest tile with given size."""
    x, y = pos
    width, height = tile_size
    # Calculate the nearest tile center
    center_x = round(x / width) * width + width // 2
    center_y = round(y / height) * height + height // 2
    return center_x, center_y
