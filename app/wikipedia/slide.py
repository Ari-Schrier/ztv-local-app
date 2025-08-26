from PIL import Image, ImageDraw, ImageFilter
from text_shit import create_text_image, make_title_page
import json
import os


BLUR_STRENGTH = 200
OVERLAY_OPACITY = 60
SPACE_AROUND_IMAGE = 100
FONT = "resources/HelveticaNeueMedium.otf"
QUESTION_SIZE = 72
ANSWER_SIZE = 54
LEFT_MARGIN = 85
INTERLINE = 1.2
AUDIO_SPEED = .95
DELAY_BEFORE_SPEECH = 2
PAUSE_AFTER_SPEECH = 3
MIN_LENGTH_OF_CLIP = 5
TIME_BETWEEN_FADE = 6
#Original time was 10
#Testing at 8, 6, and 4
BGM_VOLUME = .2
VIDEO_WIDTH=1920
VIDEO_HEIGHT=1080

def make_slide(background_location:str, text:str, y, answer=True):
    img, top =create_text_image(
        background=background_location, 
        text=text, 
        font_path=FONT, 
        initial_font_size=ANSWER_SIZE if answer else QUESTION_SIZE, 
        interline_factor=INTERLINE, 
        max_width=1920 - 1080 -85, 
        max_height=1920 - 1080 -85, 
        left_margin=LEFT_MARGIN, 
        y_position=y
    )
    return img, top+48

def process_background(image_path):
    with Image.open(image_path) as image:
        image_ratio = image.width / image.height
        target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT
        # Crop and zoom the image to fill 16:9 frame
        if image_ratio > target_ratio:
            # Image is wider than 16:9, crop the width
            new_width = int(image.height * target_ratio)
            offset = (image.width - new_width) // 2
            cropped_image = image.crop((offset, 0, offset + new_width, image.height))
        else:
            # Image is taller than 16:9, crop the height
            new_height = int(image.width / target_ratio)
            offset = (image.height - new_height) // 2
            cropped_image = image.crop((0, offset, image.width, offset + new_height))
        resized_image = cropped_image.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)

        # Apply a black opacity scrim
        overlay = int((OVERLAY_OPACITY/100)*255)
        overlay = Image.new('RGBA', resized_image.size, (0, 0, 0, 255//overlay))
        image_with_scrim = Image.alpha_composite(resized_image.convert('RGBA'), overlay)

        # Apply a heavy blur to the image (this will serve as the background)
        final_background = image_with_scrim.filter(ImageFilter.GaussianBlur(radius=BLUR_STRENGTH))

        # Ensure image is square with rounded edges
        image_size = 1080 - 2*SPACE_AROUND_IMAGE
        image = image.resize((image_size, image_size), Image.LANCZOS)

        # Create a mask for rounded corners
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, image_size, image_size], radius=50, fill=255)

        # Apply the rounded mask to the image
        image_with_rounded_corners = Image.new('RGBA', image.size)
        image_with_rounded_corners.paste(image, (0, 0), mask=mask)

        # Position the image on the right-hand side of the video frame
        image_position = (VIDEO_WIDTH - image_with_rounded_corners.width - SPACE_AROUND_IMAGE, SPACE_AROUND_IMAGE)  # Adjust positioning as necessary
        final_background.paste(image_with_rounded_corners, image_position, image_with_rounded_corners)

        watermark = Image.open("resources/logo_small.png")
        final_background.paste(watermark, (70, 85), watermark)
        # Save the final composed image temporarily
        final_image_path = f'output/testCase/background.png'
        final_background.save(final_image_path)
    
def makeSlidesForFolder(folderPath, titleText=""):
    with open(folderPath+"/script.json", "r", encoding="utf-8") as f:
        script = json.load(f)

    script = script[0]
    
    imgPath = ""
    print(f"Checking for images in {folderPath+'/processedImages'}")
    for each in os.listdir(folderPath+"/processedImages"):
        ending= each[-4:]
        if ending in [".jpg", "jpeg", ".png"]:
            imgPath = folderPath+"/processedImages/"+each
    process_background(imgPath)

    if titleText != "":
        make_title_page(titleText, "output/testCase/background.png", folderPath+"/bg.png")

    for each in ["SlideOne", "SlideTwo"]:
        completed, chaff = make_slide("output/testCase/background.png", script[each], 207, False)
        completed.save(f"{folderPath}/{each}.png")

if __name__ == "__main__":
    myslide = {
        "topic": "Emma Nutt",
        "Introduction": "On September 1, 1878 Emma Nutt began work in Boston as the world's first female telephone operator for the Boston Telephone Dispatch Company.",
        "BodyOne": "Boys had been operators but their impatience and pranks upset callers, so Emma's soothing, cultured voice and patience won customers and changed hiring.",
        "BodyTwo": "Her sister Stella became the second operator hours later; Emma worked 33-37 years, earned $10 per month for a 54-hour week, and memorized the company directory.",
        "Ending": "She is honored by a synthesized attendant called \"EMMA\" and September 1 is unofficially celebrated as Emma M. Nutt Day."
}
    process_background("output/testCase/emma.jpg")
    for each in ["Introduction", "BodyOne", "BodyTwo", "Ending"]:
        completed, chaff = make_slide("output/testCase/background.png", myslide[each], 207, False)
        completed.save(f"output/testCase/emma{each}.png")
    #make_title_page("All About Dogs", f'output/testoutput_background1.png')