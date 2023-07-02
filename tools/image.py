from PIL import Image


def png_to_ico(png_file, ico_file=None):
    if ico_file is None:
        ico_file = png_file.replace(".png", ".ico")
    Image.open(png_file).save(ico_file)
