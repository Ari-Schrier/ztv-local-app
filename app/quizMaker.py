from moviepy.editor import *
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
from PIL import Image, ImageFilter, ImageDraw
from AI.aiFunctions import getSpeech
import json
from videoFunctions import *
from random import shuffle

BLUR_STRENGTH = 200
OVERLAY_OPACITY = 60
SPACE_AROUND_IMAGE = 100
FONT = "resources/HelveticaNeueMedium.otf"
QUESTION_SIZE = 72
ANSWER_SIZE = 54
LEFT_MARGIN = 85
AUDIO_SPEED = .9
DELAY_BEFORE_SPEECH = 2
PAUSE_AFTER_SPEECH = 3
MIN_LENGTH_OF_CLIP = 5
TIME_BETWEEN_FADE = 7
BGM_VOLUME = .2

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

def clipIntroducing(bg_path, image_size, lines, currently_on, dialogue_path=False):
    """Makes a clip introducing a question or possible answer"""
    #Build the dialogue out and determine how long the video will be
    if dialogue_path:
        dialogue = AudioFileClip(dialogue_path)
        dialogue = dialogue.fx(vfx.speedx, factor=AUDIO_SPEED)
        before_speech = AudioFileClip("resources/5-seconds-of-silence.mp3").subclip(0, DELAY_BEFORE_SPEECH)
        dialogue = concatenate_audioclips([before_speech, dialogue])
        video_duration = max(dialogue.duration + PAUSE_AFTER_SPEECH, MIN_LENGTH_OF_CLIP)
        dialogue = concatenate_audioclips([dialogue, AudioFileClip("resources/15-seconds-of-silence.mp3")]).subclip(0, video_duration)
    else:
        dialogue = AudioFileClip("resources/15-seconds-of-silence.mp3").subclip(0, MIN_LENGTH_OF_CLIP)
        video_duration = MIN_LENGTH_OF_CLIP
    
    bg = ImageClip(bg_path, duration=video_duration)
    question_text = TextClip(
        lines[0], 
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

    clips = [bg, question_text]

    i = 1
    while i <= currently_on:
        new_text = TextClip(
            lines[i], 
            font=FONT, 
            method="caption", 
            align="west", 
            fontsize=ANSWER_SIZE, 
            color='white', 
            kerning=0, 
            interline=1.3,
            size=(1920 - image_size - 2*SPACE_AROUND_IMAGE, None)
        ).set_duration(video_duration).set_pos((LEFT_MARGIN, new_line))
        
        new_line += (new_text.size[1] + 48)
        clips.append(new_text)
        i+=1

    clip = CompositeVideoClip(clips)
    clip.audio = dialogue

    return clip

def fadeIncorrect(bg_path, image_size, lines, faded, duration=TIME_BETWEEN_FADE):
    video_duration = duration
    bg = ImageClip(bg_path, duration=video_duration)
    question_text = TextClip(
        lines[0], 
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

    clips = [bg, question_text]

    i = 1
    while i <= 4:
        
        new_text = TextClip(
            lines[i], 
            font=FONT, 
            method="caption", 
            align="west", 
            fontsize=ANSWER_SIZE, 
            color='white', 
            kerning=0, 
            interline=1.3,
            size=(1920 - image_size - 2*SPACE_AROUND_IMAGE, None)
        ).set_duration(video_duration).set_pos((LEFT_MARGIN, new_line))
        if i in faded:
            new_text = new_text.set_opacity(.2)
        
        new_line += (new_text.size[1] + 48)
        clips.append(new_text)
        i+=1

    clip = CompositeVideoClip(clips)

    return clip


def makeClip(title, entry, musicstart):
    image_path = entry["image_path"]
    final_image_path, image_size = makeBackground(image_path)
    dialogue_paths = [f"output/{title}/{entry['id']}_{each}.mp3" for each in ["question", "A", "B", "C", "D"]]

    answers = [
        entry["question"],
        entry["A"],
        entry["B"],
        entry["C"],
        entry["D"]
    ]
    clips =[]
    incorrect = [1, 2, 3, 4]
    random.shuffle(incorrect)
    incorrect.remove(entry["answer"])

    answerblock = []
    for i in range(0, 5):
        clips.append(clipIntroducing(final_image_path, image_size, answers, i, dialogue_paths[i]))
    for i in range(1, 4):
        answerblock.append(fadeIncorrect(final_image_path, image_size, answers, incorrect[0:i]))
    answerblock = combine_videos_with_transition(answerblock, 1.5)
    time_to_answer = answerblock.duration
    bgm = AudioFileClip("resources/thinking-time.mp3").volumex(BGM_VOLUME)
    musicend = musicstart + time_to_answer + 2
    if musicend > bgm.duration:
        musicstart = 0
        musicend = musicstart + time_to_answer + 2
    bgm = bgm.subclip(musicstart, musicend)
    bgm = audio_fadein(bgm, 2)
    bgm = audio_fadeout(bgm, 2)

    answer_audio = AudioFileClip(f"output/{title}/{entry['id']}_answer.mp3").fx(vfx.speedx, factor=AUDIO_SPEED)
    twosec = AudioFileClip("resources/15-seconds-of-silence.mp3").subclip(0,6)
    answer_audio = concatenate_audioclips([answer_audio, twosec])
    answer_clip = fadeIncorrect(final_image_path, image_size, answers, incorrect, duration=answer_audio.duration + 6)
    bgm = concatenate_audioclips([bgm, answer_audio])
    answerblock = combine_videos_with_transition([answerblock, answer_clip], 1.5)
    answerblock.audio = bgm
    clips.append(answerblock)
    clip = combine_videos_with_transition(clips, 1.5)
    clip = addLogo(clip)
    return clip, musicend

def finish_quiz(title, clipLocations):
    
    try:
        # Process the quiz questions
        questions = [VideoFileClip(each) for each in clipLocations]
        
        # Combine questions with transitions
        my_clip = combine_videos_with_transition(questions, 1)
    except Exception as e:
        print(f"Error combining videos: {e}")
        return

    try:
        # Add logo
        my_clip = addLogo(my_clip)
    except Exception as e:
        print(f"Error adding logo: {e}")
        return
        
    try:
        # Add end card
        end_card = VideoFileClip("resources/endcredits.m4v").resize(my_clip.size)
        my_clip = combine_videos_with_transition([my_clip, end_card], 1)
    except Exception as e:
        print(f"Error adding end card: {e}")
        return
        
    try:
        # Write final video file
        output_path = f'output/{title}/{title}_complete.mp4'
        my_clip.write_videofile(output_path, fps=24, threads=8)
        print(f"Successfully created video: {output_path}")
    except Exception as e:
        print(f"Error writing video file: {e}")

def preprocess_quiz(title):
        with open(f"output/{title}/{title}.json", "r") as file:
            quiz = json.load(file)
        #my_title = makeTitle(title, (1920, 1080))
        title_path = f"output/{title}/title.mp4"
        #my_title.write_videofile(title_path, fps=24, threads=8)
        clips = [title_path]
        for each in range(0, 12):
            clips.append(f'output/{title}/{each}_partial.mp4')
        music = 0
        print(clips)
        for each in quiz[12:]:
            getAudioFor(title, each)
            question, music= makeClip(title, each, music)
            output_path = f'output/{title}/{each["id"]}_partial.mp4'
            question.write_videofile(output_path, fps=24, threads=8)
            clips.append(output_path)
            print(f"I've processed {each['id']}!")
        return clips

    

if __name__ == "__main__":
    # # Cleanup temporary images
    # import os
    # os.remove(blurred_background_path)
    # os.remove(final_image_path)

    print("running!")

    making = "All About Dogs"
    partial = preprocess_quiz(making)
    finish_quiz(making, partial)
    import os
    os.system("shutdown /s /t 1")

    # from AI.stableFunctions import getPathToImage
    # title="Fishing in Alaska"
    # with open(f"output/{title}/{title}.json", "r") as file:
    #     json_data = json.load(file)
    # for i in [23]:
    #     json_data[i]["id"] = i
    #     print(f"Processing image {i+1}/{len(json_data)} (This will take a bit)")
    #     path = getPathToImage(title, json_data[i]["prompt"], i, ratio = "1:1")
    #     json_data[i]["image_path"] = path
    #     print("Processed!")


    # for i in range(0, 30):
    #     json_data[i]["id"] = i
    #     json_data[i]["image_path"] = f"output/{title}/{i}.png"
    # with open(f"output/{title}/{title}.json", "w") as file:
    #     json.dump(json_data, file, indent=4)