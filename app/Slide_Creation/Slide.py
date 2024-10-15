from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np

BLUR_STRENGTH = 200
OVERLAY_OPACITY = 60
SPACE_AROUND_IMAGE = 100
FONT = "resources/HelveticaNeueMedium.otf"
QUESTION_SIZE = 72
ANSWER_SIZE = 54
LEFT_MARGIN = 85
INTERLINE = 0.2
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

        # Save the final composed image temporarily
        final_image_path = 'output/tmp/background.png'
        final_background.save(final_image_path)


myslide = {
        "id": 0,
        "question": "What type of fish is often caught in Alaska?",
        "A": "Salmon",
        "B": "Trout",
        "C": "Goldfish",
        "D": "Tuna",
        "answer": 1,
        "answer_statement": "The correct answer is Salmon. Alaska is famous for its wild salmon, which is a common catch for fishermen.",
        "fun fact": "Alaska is home to five species of salmon, including king salmon, which is the largest of the Pacific salmon species.",
        "prompt": "A large salmon",
        "image_path": "output/Fishing in Alaska/2.png"
}

process_background(myslide["image_path"])
