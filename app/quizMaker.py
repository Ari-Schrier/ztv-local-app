from moviepy.editor import *
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
from Slide_Creation.Slide import Slide
from Slide_Creation.text_shit import make_title_page
from PIL import Image, ImageFilter, ImageDraw
from AI.aiFunctions import getSpeech
import json
from videoFunctions import *
from random import shuffle
from ffmpeg import merge_crossfade_ffmpeg as ffmpeg_crossfade

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

def combine_videos_with_transition(clips, transition_duration):
    return concatenate_videoclips([
            clip if i == 0 else clip.crossfadein(transition_duration)
            for i, clip in enumerate(clips)
        ],
        padding=-transition_duration, 
        method="compose"
    )

def combine_into(clips, filename, transition, black=False):
    temps = make_temp_files(clips)
    if black:
        temps.append("resources\\blackspace.mp4")
    ffmpeg_crossfade(temps, filename, transition)
    if black:
        temps.remove("resources\\blackspace.mp4")
    clean_up_temps(temps)

# def make_temp_files(clips):
#     files = []
#     for i, clip in enumerate(clips):
#         filename = f"output/testOutput/tempvids/makeTemp{i}.mp4"
#         clip.write_videofile(filename, fps=24, codec='libx264')
#         files.append(filename)
#     return files

def make_temp_files(clips):
    import tempfile
    temp_files = []
    for i, clip in enumerate(clips):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        clip.write_videofile(temp_file, fps=24, codec='libx264', logger=None)
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
        dialogue = concatenate_audioclips([dialogue, AudioFileClip("resources/30-seconds-of-silence.mp3")]).subclip(0, video_duration)
    else:
        dialogue = AudioFileClip("resources/30-seconds-of-silence.mp3").subclip(0, MIN_LENGTH_OF_CLIP)
        video_duration = MIN_LENGTH_OF_CLIP

    clip = ImageClip(img_path, duration=video_duration)
    clip.audio = dialogue
    return clip

def fadeIncorrect(img_path, aud_duration=TIME_BETWEEN_FADE):
    clip = ImageClip(img_path, duration=aud_duration)
    aud = AudioFileClip("resources/30-seconds-of-silence.mp3").subclip(0, aud_duration)
    clip.audio = aud
    return clip

def makeClip(title, entry, musicstart):
    partial_path = f'output/{title}/slideImages/{entry}_'
    dialogue_paths = [f"output/{title}/audio/{entry}_{each}.mp3" for each in ["question", "A", "B", "C", "D"]]
    clips = [clipIntroducing(partial_path + "question.png", dialogue_paths[0])]
    for i in range(1, 5):
        clips.append(clipIntroducing(partial_path + f'answer{i}.png', dialogue_paths[i]))
    answerblock = [fadeIncorrect(partial_path+f'incorrect_{i}.png') for i in range(1, 4)]
    #time_to_answer = answerblock[0].duration - (len(answerblock)-1)*1.5
    time_to_answer = 1.5
    for each in answerblock:
        time_to_answer += each.duration - 1.5
    bgm = AudioFileClip("resources/thinking-time.mp3").volumex(BGM_VOLUME)
    musicend = musicstart + time_to_answer + 2
    if musicend > bgm.duration:
        musicstart = 0
        musicend = musicstart + time_to_answer + 2
    bgm = bgm.subclip(musicstart, musicend)
    bgm = audio_fadein(bgm, 2)
    bgm = audio_fadeout(bgm, 2)
    answer_audio = AudioFileClip(f"output/{title}/audio/{entry}_answer_statement.mp3").fx(vfx.speedx, factor=AUDIO_SPEED)
    twosec = AudioFileClip("resources/15-seconds-of-silence.mp3").subclip(0,3)
    answer_audio = concatenate_audioclips([answer_audio, twosec])
    bgm = concatenate_audioclips([bgm, answer_audio])
    answer_clip = fadeIncorrect(partial_path+f'incorrect_4.png',aud_duration=answer_audio.duration + 3)
    block_name = f"output/{title}/tempVids/answers{entry}.mp4"
    answerblock.append(answer_clip)
    combine_into(answerblock, block_name, 1.5)
    answerblock = VideoFileClip(block_name)
    answerblock.audio = bgm
    clips.append(answerblock)
    clips.append(clipIntroducing(partial_path+"fun.png", f"output/{title}/audio/{entry}_fun fact.mp3" ))
    final_name = f"output/{title}/tempVids/slide{entry}.mp4"
    combine_into (clips, final_name, 1.5, black=True)
    return final_name, musicend

def split_list(list, n):
    k,m = divmod(len(list), n)
    return [list[i*k+min(i,m):(i+1)*k + min(i+1, m)] for i in range(n)]

def finish_quiz(title, questions):
    # Add the ending credits
    # questions.append("resources/endcredits_silent.mp4")

    # splitUp = split_list(questions, 5)
    # final_parts = []
    # for i, each in enumerate(splitUp):
    #     mid_output = f'output/{title}/{title}FinalPt{i}.mp4'
    #     ffmpeg_crossfade(each, mid_output, 1.5)
    #     final_parts.append(mid_output)

    # Write final video file
    # output_path = f'output/{title}/{title}NoAudio.mp4'
    # process_video_ffmpeg(questions, output_path, 1.5)
    output_path = f'output/{title}/{title}.mp4'
    #process_audio_ffmpeg(questions, output_path, 1.5)
    ffmpeg_crossfade(questions, output_path, 1.5)
    print(f"Successfully created video: {output_path}")

def make_directories(title):
    import os
    directories = [
        f"output/{title}/audio",
        f"output/{title}/images",
        f"output/{title}/slideImages",
        f"output/{title}/tempVids"
        ]
    for each in directories:
        if not os.path.exists(each):
            os.makedirs(each)
            
def preprocess_quiz(title):
        with open(f"output/{title}/{title}.json", "r") as file:
            quiz = json.load(file)
        title_name = f"output/{title}/tempVids/title.mp4"
        clips = [title_name]
        music = 0

        for i in range(0, len(quiz)):
            print(f"Working slide {i}")
            Slide(title, i, quiz[i])
            getAudioFor(title, quiz[i])
            question, music= makeClip(title, i, music)
            clips.append(question)

        # for entry in range(0, len(quiz)):
        #      clips.append(f"output/{title}/tempVids/slide{entry}.mp4")

        firstclip = clips [0:2]
        otherclips = clips[2:]
        random.shuffle(otherclips)
        clips = firstclip + otherclips

        make_title_page(title, f"output/{title}/slideImages/0_background.png")
        my_title = fadeIncorrect(f"output/{title}/slideImages/title.png", 8)
        my_title.write_videofile(title_name, fps=24, logger=None)
        return clips

def set_all_answer_to(title, choice):
    with open(f"output/{title}/{title}.json", "r") as file:
            my_json = json.load(file)
    for each in my_json:
        each["answer"] = choice
    with open(f"output/{title}/{title}.json", "w") as file:
        json.dump(my_json, file, indent=4)

def scramble_answers(title):
    abcd = ["Zombocom", "A", "B", "C", "D"]
    with open(f"output/{title}/{title}.json", "r") as file:
            my_json = json.load(file)
    for each in my_json:
        new_answer = random.randint(1, 4)
        old_answer = each["answer"]
        if new_answer != old_answer:
            each[abcd[old_answer]], each[abcd[new_answer]] = each[abcd[new_answer]], each[abcd[old_answer]]
            each["answer"] = new_answer
    with open(f"output/{title}/{title}.json", "w") as file:
        json.dump(my_json, file, indent=4)

if __name__ == "__main__":

    # make_directories("The_History_of_Beer")

    import time
    start_time=time.time()
    print("running!")
    title =  "Name_That_Sea_Animal"
    clips = preprocess_quiz(title)
    finish_quiz(title, clips)
    total_time = time.strftime('%H:%M:%S', time.gmtime(time.time() - start_time))
    print(f"The video processed in {total_time}")
    
    # os.system("shutdown /s /t 1")


    # with open(f"output/Flags_Of_The_World/Flags_Of_The_World.json", "r") as file:
    #         my_json = json.load(file)
    # with open(f"output/Flags_Of_The_World/Flags_Of_The_World.json", "w") as file:
    #     json.dump(my_json, file, indent=4)

    # from AI.stableFunctions import getPathToImage
    # title="Name_That_Sea_Animal"
    # with open(f"output/{title}/{title}.json", "r") as file:
    #     json_data = json.load(file)
    # # for i in range(0, len(json_data)):
    # for i in [0, 5, 10, 11, 12, 15, 23, 29, 31]:
    #     json_data[i]["id"] = i
    #     print(f"Processing image {i}/{len(json_data)-1} (This will take a bit)")
    #     path = getPathToImage(title, json_data[i]["prompt"], i, ratio = "1:1")
    #     path = f"output/{title}/images/{i}.png"
    #     json_data[i]["image_path"] = path
    #     print("Processed!")
    # with open(f"output/{title}/{title}.json", "w") as file:
    #     json.dump(json_data, file, indent=4)


    # for i in range(0, 30):
    #     json_data[i]["id"] = i
    #     json_data[i]["image_path"] = f"output/{title}/{i}.png"
    # with open(f"output/{title}/{title}.json", "w") as file:
    #     json.dump(json_data, file, indent=4)
