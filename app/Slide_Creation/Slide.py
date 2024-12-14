from PIL import Image, ImageDraw, ImageFilter
from Slide_Creation.text_shit import create_text_image, make_title_page
import random


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
class Slide:
    def __init__(self, name, number, lib):
        self.name=name
        self.number=number
        self.lib=lib
        self.process_background(lib["image_path"])
        question_presented, self.answer_1_top = self.make_slide(
            f'output/{self.name}/slideImages/{self.number}_background.png',
            lib["question"],
            207,
            False
        )
        q_name = f'output/{self.name}/slideImages/{self.number}_question.png'
        question_presented.save(q_name)
        self.answer_1_top += 30
        answer_1_shown, self.answer_2_top=self.make_slide(
            q_name,
            "A: " + lib["A"],
            self.answer_1_top
        )
        a1_name = f'output/{self.name}/slideImages/{self.number}_answer1.png'
        answer_1_shown.save(a1_name)
        answer_2_shown, self.answer_3_top=self.make_slide(
            a1_name,
            "B: " + lib["B"],
            self.answer_2_top
        )
        a2_name = f'output/{self.name}/slideImages/{self.number}_answer2.png'
        answer_2_shown.save(a2_name)
        answer_3_shown, self.answer_4_top=self.make_slide(
            a2_name,
            "C: " + lib["C"],
            self.answer_3_top
        )
        a3_name = f'output/{self.name}/slideImages/{self.number}_answer3.png'
        answer_3_shown.save(a3_name)
        
        incorrect = [1, 2, 3]
        random.shuffle(incorrect)
        incorrect.remove(lib["answer"])
        for i in range(0, 3):
            self.makeSlideWithout(incorrect[0:i], f"incorrect_{i+1}")
        
        funfact = create_text_image(
            f'output/{self.name}/slideImages/{self.number}_background.png',
            lib["fun_fact"],
            font_path=FONT, 
            initial_font_size= QUESTION_SIZE, 
            interline_factor=INTERLINE, 
            max_width=1920 - 1080 -85, 
            max_height=500, 
            left_margin=LEFT_MARGIN, 
            y_position=290
            )
        funfact[0].save(f'output/{self.name}/slideImages/{self.number}_fun.png')

    def makeSlideWithout(self, answers, piece_name):
        #answer should be a list of numbers. If answer is [2, 3], then the second and third answers will be excluded
        part_name = f'output/{self.name}/slideImages/{self.number}_{piece_name}.png'
        current_state, foo = self.make_slide(
            f'output/{self.name}/slideImages/{self.number}_background.png',
            self.lib["question"],
            207,
            False
        )
        current_state.save(part_name)
        if 1 not in answers:
            current_state, foo=self.make_slide(
            part_name,
            "A: " + self.lib["A"],
            self.answer_1_top
            )
            current_state.save(part_name)
        if 2 not in answers:
            current_state, foo=self.make_slide(
            part_name,
            "B: " + self.lib["B"],
            self.answer_2_top
            )
            current_state.save(part_name)
        if 3 not in answers:
            current_state, foo=self.make_slide(
            part_name,
            "C: " + self.lib["C"],
            self.answer_3_top
            )
            current_state.save(part_name)
        

    def make_slide(self, background, text, y, answer=True):
        img, top =create_text_image(
            background=background, 
            text=text, 
            font_path=FONT, 
            initial_font_size=ANSWER_SIZE if answer else QUESTION_SIZE, 
            interline_factor=INTERLINE, 
            max_width=1920 - 1080 -85, 
            max_height=145 if answer else 291, 
            left_margin=LEFT_MARGIN, 
            y_position=y
        )
        return img, top+48

    def process_background(self, image_path):
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
            final_image_path = f'output/{self.name}/slideImages/{self.number}_background.png'
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

if __name__ == "__main__":
    process_backgroundz("output/All About Dogs/0.png")
    make_title_page("All About Dogs", f'output/testoutput_background1.png')