from moviepy.editor import *
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
from Slide_Creation.Slide import Slide
from Slide_Creation.text_shit import make_title_page
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
INTERLINE = 0.2
AUDIO_SPEED = .95
DELAY_BEFORE_SPEECH = 2
PAUSE_AFTER_SPEECH = 3
MIN_LENGTH_OF_CLIP = 5
TIME_BETWEEN_FADE = 6
#Original time was 10
#Testing at 8, 6, and 4
BGM_VOLUME = .2

import subprocess

def ffmpeg_crossfade(clips, output_filename, crossfade_duration=1):
    """
    Apply crossfades between a list of video clips using FFmpeg.
    
    Parameters:
    clips (list): List of file paths to the video clips.
    output_filename (str): The output video file path.
    crossfade_duration (int): Duration of the crossfade in seconds.
    """
    filter_complex = ""
    inputs = []
    last_input = None

    for i, clip in enumerate(clips):
        inputs.append(f"-i {clip}")
        if last_input is None:
            last_input = f"[{i}:v][{i}:a]"
        else:
            filter_complex += f"[{i-1}:v][{i}:v]xfade=transition=fade:duration={crossfade_duration}:offset={i-1}[v{i}];"
            filter_complex += f"[{i-1}:a][{i}:a]acrossfade=d={crossfade_duration}[a{i}];"
            last_input = f"[v{i}][a{i}]"
    
    # Construct the full FFmpeg command
    command = f"ffmpeg {' '.join(inputs)} -filter_complex \"{filter_complex}\" -map \"{last_input}\" {output_filename}"

    # Call FFmpeg
    subprocess.run(command, shell=True)

def combine_videos_with_transition(clips, transition_duration):
    return concatenate_videoclips([
            clip if i == 0 else clip.crossfadein(transition_duration)
            for i, clip in enumerate(clips)
        ],
        padding=-transition_duration, 
        method="compose"
    )

def combine_into(clips, filename, transition):
    temps = make_temp_files(clips)
    ffmpeg_crossfade(temps, filename, transition)
    clean_up_temps(temps)

def make_temp_files(clips):
    import os
    import tempfile
    temp_files = []
    for i, clip in enumerate(clips):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        clip.write_videofile(temp_file, fps=24, codec='libx264')
        temp_files.append(temp_file)
    return temp_files
def clean_up_temps(file_paths):
    import os
    for file_path in file_paths:
        os.remove(file_path)

def clipIntroducing(img_path, dialogue_path=False):
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

    clip = ImageClip(img_path, duration=video_duration)
    clip.audio = dialogue
    return clip

def fadeIncorrect(img_path, duration=TIME_BETWEEN_FADE):
    clip = ImageClip(img_path, duration=duration)
    return clip

def makeClip(title, entry, musicstart):
    partial_path = f'output/{title}/slideImages/{entry}_'
    dialogue_paths = [f"output/{title}/audio/{entry}_{each}.mp3" for each in ["question", "A", "B", "C", "D"]]
    clips = [clipIntroducing(partial_path + "question.png", dialogue_paths[0])]
    for i in range(1, 5):
        clips.append(clipIntroducing(partial_path + f'answer{i}.png', dialogue_paths[i]))
    answerblock = [fadeIncorrect(partial_path+f'incorrect_{i}.png') for i in range(1, 4)]
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
    answer_audio = AudioFileClip(f"output/{title}/audio/{entry}_answer_statement.mp3").fx(vfx.speedx, factor=AUDIO_SPEED)
    twosec = AudioFileClip("resources/15-seconds-of-silence.mp3").subclip(0,6)
    answer_audio = concatenate_audioclips([answer_audio, twosec])
    bgm = concatenate_audioclips([bgm, answer_audio])
    answer_clip = fadeIncorrect(partial_path+f'incorrect_4.png',duration=answer_audio.duration + 6)
    answerblock = combine_videos_with_transition([answerblock, answer_clip], 1.5)
    answerblock.audio = bgm
    clips.append(answerblock)
    clips.append(clipIntroducing(partial_path+"fun.png", f"output/{title}/audio/{entry}_fun fact.mp3" ))
    clip = combine_videos_with_transition(clips, 1.5)
    return clip, musicend

def finish_quiz(title, questions):
    
    try:
        # Process the quiz questions
        questions = [item for elem in questions for item in (elem, ColorClip(size=(1920,1080), color=(0, 0, 0), duration=4.5))]
        
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
        output_path = f'output/{title}/{title}Final.mp4'
        my_clip.write_videofile(output_path, fps=24, threads=8)
        print(f"Successfully created video: {output_path}")
    except Exception as e:
        print(f"Error writing video file: {e}")

def make_directories(title):
    import os
    directories = [
        f"output/{title}/audio",
        f"output/{title}/images",
        f"output/{title}/slideImages",
        f"output/{title}/partial_vids"
        ]
    for each in directories:
        if not os.path.exists(each):
            os.makedirs(each)
            
def preprocess_quiz(title):
        with open(f"output/{title}/{title}.json", "r") as file:
            quiz = json.load(file)
        #make_title_page(title)
        my_title = ImageClip(f"output/{title}/slideImages/title.png", duration=8)
        clips = [my_title]
        music = 0
        for i in range(0, 1):
            print(f"working {i}")
            #Slide(title, i, quiz[i])
            #getAudioFor(title, each)
            question, music= makeClip(title, i, music)
            clips.append(question)
            print(f"I've processed {i}!")
        return clips

    

if __name__ == "__main__":
    # # Cleanup temporary images
    # import os
    # os.remove(blurred_background_path)
    # os.remove(final_image_path)

    # print("running!")
    # title = "Fishing in Alaska"
    # clips = preprocess_quiz(title)
    # finish_quiz(title, clips)
    import time
    clipA = ImageClip('output/Fishing in Alaska/images/1.png', duration=6)
    clipB = ImageClip('output/Fishing in Alaska/images/3.png', duration=6)
    # start_time = time.time()
    # my_clip = combine_videos_with_transition([clipA, clipB], 2)
    # my_clip.write_videofile("output/Fishing in Alaska/help.mp4", fps=24, threads=8)
    # end_time = time.time()
    # print(f"Function1 ran in {end_time - start_time} seconds")
    start_time = time.time()
    temps = make_temp_files([clipA, clipB])
    ffmpeg_crossfade(temps, 'output/AARDVARK.mp4', 2)
    clean_up_temps(temps)
    end_time = time.time()
    print(f"Function2 ran in {end_time - start_time} seconds")

    # makeBackground("output/All About Dogs/0.png")
    # clip=funFact(
    #     "output/testOutput/background.png",
    #     1080 - 2*SPACE_AROUND_IMAGE,
    #     "A wagging tail can mean many things, from excitement to curiosity.",
    #     False
    # )
    # clip.write_videofile("output/testOutput/funfact1.mp4", fps=24)

    # making = "All About Dogs"
    # partial = preprocess_quiz(making)
    # finish_quiz(making, partial)
    # making = "The History of Beer"
    # partial = preprocess_quiz(making)
    # finish_quiz(making, partial)
    # import os
    # os.system("shutdown /s /t 1")

    # from AI.stableFunctions import getPathToImage
    # title="All About Dogs"
    # with open(f"output/{title}/{title}.json", "r") as file:
    #     json_data = json.load(file)
    # for i in [30]:
    #     json_data[i]["id"] = i
    #     print(f"Processing image {i}/{len(json_data)} (This will take a bit)")
    #     path = getPathToImage(title, json_data[i]["prompt"], i, ratio = "1:1")
    #     json_data[i]["image_path"] = path
    #     print("Processed!")
    # with open(f"output/{title}/{title}.json", "w") as file:
    #     json.dump(json_data, file, indent=4)


    # for i in range(0, 30):
    #     json_data[i]["id"] = i
    #     json_data[i]["image_path"] = f"output/{title}/{i}.png"
    # with open(f"output/{title}/{title}.json", "w") as file:
    #     json.dump(json_data, file, indent=4)
