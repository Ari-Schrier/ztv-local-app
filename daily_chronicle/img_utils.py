import os
from PIL import Image

def crop_center(img: Image.Image) -> Image.Image:
    """Crops the image to a square based on the shortest side."""
    width, height = img.size
    min_side = min(width, height)
    left = (width - min_side) / 2
    top = (height - min_side) / 2
    right = (width + min_side) / 2
    bottom = (height + min_side) / 2
    return img.crop((left, top, right, bottom))