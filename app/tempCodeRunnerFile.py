from moviepy.editor import *
from PIL import Image, ImageFilter, ImageDraw
from videoFunctions import addLogo

BLUR_STRENGTH = 200
OVERLAY_OPACITY = 60
SPACE_AROUND_IMAGE = 100
FONT = "resources/HelveticaNeueMedium.otf"
QUESTION_SIZE = 72
ANSWER_SIZE = 54
LEFT_MARGIN = 85
AUDIO_SPEED = .9

def combine_videos_with_transition(clips, transition_duration):
    return concatenate_videoclips([
            clip if i == 0 else clip.crossfadein(transition_duration)
            for i, clip in enumerate(clips)
        ],
        padding=-transition_duration, 
        method="compose"
    )

def makeBackground(image_path):
    video_width, video_height = 1920, 1080  # 16:9 aspect ratio dimensions
    # Load and process the image
    image = Image.open(image_path)

    # Calculate the aspect ratios
    image_ratio = image.width / image.height
    target_ratio = video_width / video_height

    # Crop and zoom the image to fill 16:9 frame
    if image_ratio > target_ratio:
        # Image is wider than 16:9, crop the width
        new_width = int(image.height * target_ratio)
        offset = (image.width - new_width) // 2
        image = image.crop((offset, 0, offset + new_width, image.height))
    else:
        # Image is taller than 16:9, crop the height
        new_height = int(image.width / target_ratio)
        offset = (image.height - new_height) // 2
        image = image.crop((0, offset, image.width, offset + new_height))

    # Resize to video dimensions
    image = image.resize((video_width, video_height), Image.LANCZOS)

    # Apply a black opacity scrim
    overlay = int((OVERLAY_OPACITY/100)*255)
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 255//overlay))
    image_with_scrim = Image.alpha_composite(image.convert('RGBA'), overlay)

    # Apply a heavy blur to the image (this will serve as the background)
    blurred_image_with_scrim = image_with_scrim.filter(ImageFilter.GaussianBlur(radius=BLUR_STRENGTH))

    # Save the blurred background temporarily
    blurred_background_path = 'temp_blurred_background.png'
    blurred_image_with_scrim.save(blurred_background_path)

    # Load the original image again for overlay (ensure it's square for rounded edges)
    image = Image.open(image_path)
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
    final_background = Image.open(blurred_background_path)
    image_position = (video_width - image_with_rounded_corners.width - SPACE_AROUND_IMAGE, SPACE_AROUND_IMAGE)  # Adjust positioning as necessary
    final_background.paste(image_with_rounded_corners, image_position, image_with_rounded_corners)

    # Save the final composed image temporarily
    final_image_path = 'output/testOutput/background.png'
    final_background.save(final_image_path)
    return final_image_path, image_size

def makeQuestionClip(bg_path, image_size, question, options, i):
    choices = ["question", "A", "B", "C", "D", "None"]
    current_voiceover = choices[i]
    if current_voiceover != "None":
        dialogue = AudioFileClip(f"output/testOutput/speech{current_voiceover}.mp3")
        dialogue = dialogue.fx(vfx.speedx, factor=AUDIO_SPEED)
        #dialogue = concatenate_audioclips([AudioFileClip("resources/5-seconds-of-silence.mp3"), dialogue])
        print("Found dialogue!")
    else:
        print("No Dialogue!")
        dialogue = AudioFileClip("resources/5-seconds-of-silence.mp3")
        

    video_duration = max(5, dialogue.duration + 2)  # Duration of the video in seconds

    dialogue = concatenate_audioclips([dialogue, AudioFileClip("resources/15-seconds-of-silence.mp3")])

    dialogue = dialogue.subclip(0, video_duration)
    dialogue.write_audiofile("output/testOutput/pleasework.mp3")

    print(f"Video duration: {video_duration}")

    print(f"Dialogue duration: {dialogue.duration}")

    clip = ImageClip(bg_path, duration=video_duration)
    question_text = TextClip(
        question, 
        font=FONT, 
        method="caption", 
        align="west", 
        fontsize=QUESTION_SIZE, 
        color="white", 
        kerning=0, 
        interline=1.4,
        size=(1920 - image_size - 2*SPACE_AROUND_IMAGE, None)
    ).set_pos((LEFT_MARGIN, 207)).set_duration(video_duration)

    new_line = 207 + question_text.size[1] + 72

    clips = [clip, question_text]

    j = 1
    for answer in options:
        new_text = TextClip(
            answer, 
            font=FONT, 
            method="caption", 
            align="west", 
            fontsize=ANSWER_SIZE, 
            color='white', 
            kerning=0, 
            interline=1.3,
            size=(1920 - image_size - 2*SPACE_AROUND_IMAGE, None)
        ).set_duration(video_duration).set_pos((LEFT_MARGIN, new_line))

        if j == 5:
            j=0

        if j <= i:
            new_text = new_text.set_opacity(.2)
        
        new_line += (new_text.size[1] + 48)
        clips.append(new_text)
        j+=1

    # Set the output video properties
    clip = clip.set_duration(video_duration)
    clip = clip.set_fps(24)

    clip = CompositeVideoClip(clips)
    clip.audio = dialogue

    return clip


def makeClip():
    question = "What do robots do on their day off?"
    option_a = "They recharge by the beach."
    option_b = "They have a 'bit' of fun."
    option_c = "They go out for a 'byte' to eat."
    option_d = "They watch reruns of The Jetsons."

    image_path = "output/testOutput/testbot.png"
    final_image_path, image_size = makeBackground(image_path)
    output_video_path = 'output/testOutput/audiotest2.mp4'

    answers = [option_a, option_b, option_c, option_d]
    clips =[]

    for i in range(0, 6):
        clips.append(makeQuestionClip(final_image_path, image_size, question, answers, i))
    clip = combine_videos_with_transition(clips, 1.5)
    clip = addLogo(clip)
    clip.write_videofile(output_video_path, fps=24)

if __name__ == "__main__":
    makeClip()

    # # Cleanup temporary images
    # import os
    # os.remove(blurred_background_path)
    # os.remove(final_image_path)