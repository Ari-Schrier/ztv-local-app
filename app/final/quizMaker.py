from moviepy.editor import *
from AI.aiFunctions import getSpeech
import json
from videoFunctions import *

def makeQuizChunk(title, question, current_answer):
    size = (1920, 1080)
    vertical_padding = 7
    answers = ["A", "B", "C", "D"]
    duration = 4
    audio = None
    if current_answer is not None:
        try:
            audio_path = f"output/{title}/{question['id']}_{current_answer}.mp3"
            audio = AudioFileClip(audio_path)
            silence = AudioFileClip("resources/15-seconds-of-silence.mp3")
            duration = max(6, (audio.duration + 4))
            audio = concatenate_audioclips([silence.subclip(0, 1), audio, silence])
        except OSError as e:
            print(f"Error loading audio file: {e}")
            audio = None
    
    bg = ColorClip(size=size, color=(0, 0, 0), duration=duration)
    question_text = TextClip(
        question['question'], 
        font="resources/HelveticaNeueBold.otf", 
        method="caption", 
        align="west", 
        fontsize=80, 
        color='white', 
        kerning=5, 
        size=(size[0] - 800, None)
    ).set_pos((120, 200)).set_duration(duration)
    
    clips = [bg, question_text]
    new_line = 220 + question_text.size[1]
    
    for answer in answers:
        text_color = "black" if answer == current_answer else "white"
        bg_color = "red" if answer == current_answer else "transparent"
        
        # Create a background color clip for the margin
        margin_bg = ColorClip(
            size=(size[0] - 800, 75 + vertical_padding), 
            color=(255, 0, 0) if answer == current_answer else (0, 0, 0, 0),
            duration=duration
        ).set_pos((150, new_line - vertical_padding))
        
        new_text = TextClip(
            question[answer], 
            font="resources/HelveticaNeueThin.otf", 
            method="caption", 
            align="west", 
            fontsize=75, 
            color=text_color, 
            kerning=5, 
            size=(size[0] - 800, None)
        ).set_duration(duration).set_pos((150, new_line))
        
        new_line += (vertical_padding + new_text.size[1] + 25)
        clips.append(margin_bg)
        clips.append(new_text)
    
    fullClip = CompositeVideoClip(clips).set_duration(duration)  # Ensure fullClip duration is set to DURATION

    if audio:
        audio = audio.set_duration(fullClip.duration)
        fullClip = fullClip.set_audio(audio)

    return fullClip

def makeQuizQuestion(title, question):
    chunks = ["question", "A", "B", "C", "D", "answer"]  # Adjust chunks as needed
    processed = [makeQuizChunk(title, question, each) for each in chunks]

    duration = 7
    audio = None
    try:
        audio_path = f"output/{title}/{question['id']}_fun fact.mp3"
        audio = AudioFileClip(audio_path)
        duration = max(8, audio.duration+5)
        silence = AudioFileClip("resources/15-seconds-of-silence.mp3")
        audio = concatenate_audioclips([silence.subclip(0, 1), audio, silence])
    except OSError as e:
        print(f"Error loading audio file: {e}")
        audio = None
    image = ken_burns_effect(f"output/{title}/{question['id']}.png", duration)
    if audio:
        audio = audio.set_duration(image.duration)
        image = image.set_audio(audio)
    processed.append(image)

    return combine_videos_with_transition(processed, 1)

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
        my_clip.write_videofile(output_path, fps=24)
        print(f"Successfully created video: {output_path}")
    except Exception as e:
        print(f"Error writing video file: {e}")

def preprocess_quiz(title):
    with open(f"output/{title}/{title}.json", "r") as file:
        quiz = json.load(file)
    my_title = makeTitle(title, (1920, 1080))
    title_path = f"output/{title}/title.mp4"
    my_title.write_videofile(title_path, fps=24)
    clips = [title_path]
    for each in quiz:
        getAudioFor(title, each)
        question = makeQuizQuestion(title, each)
        output_path = f'output/{title}/{each["id"]}_partial.mp4'
        question.write_videofile(output_path, fps=24)
        clips.append(output_path)
    return clips

if __name__ == "__main__":
    making = "Osamu Tezuka"
    partial = preprocess_quiz(making)
    finish_quiz(making, partial)
