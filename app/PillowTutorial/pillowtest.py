from PIL import Image, ImageDraw, ImageFont

with Image.open("output/Sample Title/thing2.png") as im:

    draw = ImageDraw.Draw(im)

    font = ImageFont.truetype("arial.ttf", 85)

    canvas_width, canvas_height = im.size
    offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
    for dx, dy in offsets:
        draw.text((15 + dx, canvas_height - 100 + dy), "Hello There",  font=font, fill=(0, 0, 0, 128))
    draw.text((15, canvas_height - 100), "Hello There",  font=font, fill=(255, 255, 255, 128))
    
    # write to stdout
    im.show()