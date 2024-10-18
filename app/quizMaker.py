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
    Apply crossfades between a list of video clips using FFmpeg, with conditional audio handling.
    
    Parameters:
    clips (list): List of file paths to the video clips.
    output_filename (str): The output video file path.
    crossfade_duration (int): Duration of the crossfade in seconds.
    """
    filter_complex = ""
    inputs = []
    last_video = None
    last_audio = None

    for i, clip in enumerate(clips):
        inputs.append(f"-i {clip}")
        
        if last_video is None:
            # First video, no crossfade yet
            last_video = f"[{i}:v]"
            last_audio = f"[{i}:a]"
        else:
            # Add video crossfade
            filter_complex += f"[{i-1}:v][{i}:v]xfade=transition=fade:duration={crossfade_duration}:offset=0[v{i}];"
            last_video = f"[v{i}]"
            filter_complex += f"[{i-1}:a][{i}:a]acrossfade=d={crossfade_duration}[a{i}];"
            last_audio = f"[a{i}]"

    # Use the final filter output for the video
    final_video = f"[v{len(clips)-1}]"
    
    # Construct the full FFmpeg command
    command = f"ffmpeg {' '.join(inputs)} -filter_complex \"{filter_complex}\" -map {final_video}"
    
    # Map audio if it was present and handled
    if last_audio:
        final_audio = f"[a{len(clips)-1}]"
        command += f" -map {final_audio}"
    
    command += f" {output_filename}"

    # Call FFmpeg
    print(command)
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
    time_to_answer = answerblock[0].duration - (len(answerblock)-1)*1.5
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
    block_name = f"output/{title}/tempVids/answers{entry}.mp4"
    answerblock.append(answer_clip)
    print(answerblock)
    combine_into(answerblock, block_name, 1.5)
    answerblock = VideoFileClip(block_name)
    answerblock.audio = bgm
    clips.append(answerblock)
    clips.append(clipIntroducing(partial_path+"fun.png", f"output/{title}/audio/{entry}_fun fact.mp3" ))
    final_name = f"output/{title}/tempVids/slide{entry}.mp4"
    combine_into (clips, final_name, 1.5)
    return final_name, musicend

def finish_quiz(title, questions):

    # Process the quiz questions
    questions = [item for elem in questions for item in (elem, "resources/blackspace.mp4")]
    questions.append("resources/endcredits.mp4")
    # Write final video file
    output_path = f'output/{title}/{title}Final.mp4'
    ffmpeg_crossfade(questions, output_path, 1.5)
    print(f"Successfully created video: {output_path}")

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
        title_name = f"output/{title}/tempVids/title.mp4"
        #my_title.write_videofile(title_name, fps=24)
        clips = [title_name]
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
    # clips = preprocess_quiz(title)s
    # finish_quiz(title, clips)

    vid1 = "output/testOutput/tempVids/vid1.mp4"
    vid2 = "output/testOutput/tempVids/vid2.mp4"
    # audio = AudioFileClip("resources/15-seconds-of-silence.mp3")
    # audio = audio.set_duration(vid1.duration)
    # vid1.set_audio(audio)
    # vid2.set_audio(audio)
    
    # vid1.write_videofile("output/testOutput/tempVids/vid1.mp4", fps=24)
    # vid2.write_videofile("output/testOutput/tempVids/vid2.mp4", fps=24)
    ffmpeg_crossfade([vid1, vid2], "output/testOutput/tempVids/vid3.mp4", 1.5)
    
    # making = "All About Dogs"0a
    # partial = preprocess_quiz(making)
    # finish_quiz(making, partial)
    # making = "The History of Beer"0a
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
