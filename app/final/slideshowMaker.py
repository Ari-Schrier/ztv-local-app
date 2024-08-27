from videoFunctions import *
from moviepy.editor import *
from AI.aiFunctions import getSpeech
import json

def make_slide(title, slide):
    clip = ken_burns_effect(slide['image_path'], duration=21)
    clip = add_caption(clip, slide["funFact"])
    voice_over = AudioFileClip(f"output/{title}/{slide['id']}_text.mp3")
    silent_audio = AudioFileClip("resources/5-seconds-of-silence.mp3")
    silent_15 = AudioFileClip("resources/15-seconds-of-silence.mp3")
    combined_voice_over = concatenate_audioclips([silent_audio, voice_over, silent_15, silent_15])
    combined_voice_over = combined_voice_over.set_duration(clip.duration)
    clip = clip.set_audio(combined_voice_over)
    return clip

def preprocess_slideshow(title):
    with open(f"output/{title}/{title}.json", "r") as file:
        slides = json.load(file)
    my_title = makeTitle(title, (1920, 1080))
    title_path = f"output/{title}/title.mp4"
    my_title.write_videofile(title_path, fps=24)
    clips = [title_path]
    for each in slides:
        getSpeech(f"output/{title}/{each['id']}_text.mp3", each["funFact"], "echo")
        slide = make_slide(title, each)
        output_path = f'output/{title}/{each["id"]}_partial.mp4'
        slide.write_videofile(output_path, fps=24)
        clips.append(output_path)
    return clips

def make_video(title, location, data):

    clips = []

    SIZE = (1920,1080)

    title_text = makeTitle(title, (SIZE))

    clips.append(title_text)

    for slide in data:
        newClip = ken_burns_effect(f"output/{location}/{slide['id']}.png", duration=21)
        newClip = add_caption(newClip, slide["text"])
        voice_over = AudioFileClip(f"output/{location}/{slide['id']}_text.mp3")
        silent_audio = AudioFileClip("resources/5-seconds-of-silence.mp3")
        silent_15 = AudioFileClip("resources/15-seconds-of-silence.mp3")
        combined_voice_over = concatenate_audioclips([silent_audio, voice_over, silent_15, silent_15])
        newClip = newClip.set_audio(combined_voice_over)
        clips.append(newClip.resize(SIZE))

    concat_clip = combine_videos_with_transition(clips,1)
    concat_clip = addLogo(concat_clip)
    end_card = VideoFileClip("resources/endcredits.m4v").resize(SIZE)
    concat_clip = combine_videos_with_transition([concat_clip, end_card],1)

    concat_clip.write_videofile(f"output/{title}.mp4", fps=24)

if __name__ == "__main__":
    from quizMaker import finish_quiz
    bees = preprocess_slideshow("Flamingos")
    finish_quiz("Flamingos", bees)