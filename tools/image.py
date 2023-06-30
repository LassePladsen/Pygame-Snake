from PIL import Image

from tools.resource import get_resource_path

def png_to_ico(png_file, ico_file=None):
    if ico_file is None:
        ico_file = png_file.replace(".png", ".ico")
    Image.open(png_file).save(ico_file)

if __name__ == "__main__":
    # png_to_ico(get_resource_path(r"..\assets\images\icon.png"))
    pass
