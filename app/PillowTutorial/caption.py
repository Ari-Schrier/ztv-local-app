from PIL import Image, ImageDraw, ImageFont

def caption(image, output, text):
    with Image.open(image) as im:

        draw = ImageDraw.Draw(im)

        font = ImageFont.truetype("arial.ttf", 85)

        image_width, image_height = im.size
        text_width = draw.textlength(text, font=font)

        offsets = [(-4, -4), (-4, 4), (4, -4), (4, 4)]
        for dx, dy in offsets:
            draw.text(((image_width-text_width)/2 + dx, image_height - 100 + dy), text,  font=font, fill=(0, 0, 0, 128))
        draw.text(((image_width-text_width)/2, image_height - 100), text,  font=font, fill=(255, 255, 255, 128))
        
        # write to stdout
        im.save(output)

if __name__ == "__main__":
    caption("output/Sample Title/thing1.png", "output/Sample Title/test2.png", "This is a HORSE")