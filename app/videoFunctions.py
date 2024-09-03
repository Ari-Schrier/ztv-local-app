from moviepy.editor import *
from AI.aiFunctions import getSpeech
import random

VOICE_ACTOR= "echo"
#All extant voice actors: ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

#Fetches audio via openAI API of the chosen voice actor reading all lines.
def getAudioFor(video_title, question):
    destination = f"output/{video_title}/{question['id']}_"
    for each in ["question", "fun fact"]:
        getSpeech(destination+each+".mp3", question[each], VOICE_ACTOR)
    for each in ["A", "B", "C", "D"]:
        getSpeech(destination+each+".mp3", question[each][2:] +"?", VOICE_ACTOR)
    answer = ["A", "B", "C", "D"][question["answer"]-1]
    getSpeech(destination+"answer.mp3", f"The answer is {answer}: {question[answer][2:]}.")

#Combines multiple video clips with a crossfade effect
def combine_videos_with_transition(clips, transition_duration):
    return concatenate_videoclips([
            clip if i == 0 else clip.crossfadein(transition_duration)
            for i, clip in enumerate(clips)
        ],
        padding=-transition_duration, 
        method="compose"
    )

#Takes a still image, returns a video slowly zooming into the image
def ken_burns_effect(image_path, duration, zoom_start=1.0, zoom_end=1.4):
    clip = ImageClip(image_path)
    w, h = clip.size
    
    # Randomly choose a corner: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    corners = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
    chosen_corner = random.choice(corners)
    
    def get_crop_center(chosen_corner, w, h, zoom):
        if chosen_corner == 'top-left':
            return w / (2 * zoom), h / (2 * zoom)
        elif chosen_corner == 'top-right':
            return w - w / (2 * zoom), h / (2 * zoom)
        elif chosen_corner == 'bottom-left':
            return w / (2 * zoom), h - h / (2 * zoom)
        elif chosen_corner == 'bottom-right':
            return w - w / (2 * zoom), h - h / (2 * zoom)
    
    def make_frame(t):
        zoom = zoom_start + (zoom_end - zoom_start) * (t / duration)
        x_center, y_center = get_crop_center(chosen_corner, w, h, zoom)
        cropped = clip.crop(x_center=x_center, y_center=y_center, width=w/zoom, height=h/zoom)
        return cropped.resize((w, h)).get_frame(t)
    
    return VideoClip(make_frame, duration=duration)

#Adds a caption to a clip
def add_caption(clip, text, fontsize=75, font='Arial', margin=120, y_offset=50):
    
    # Create the text clip with a fixed font size and wrapping
    txt_clip = TextClip(text, fontsize=fontsize, bg_color='black', color='white', font=font, method='caption', interline=10, size=(clip.w - 2 * margin, None)).set_duration(clip.duration)
    
    # Determine the position for the text and background
    txt_clip = txt_clip.set_position(('center', 'bottom'))

    # Make the clip partially transparent
    txt_clip = txt_clip.set_opacity(.7)
    
    # Move the clip up by y_offset pixels
    final_clip = CompositeVideoClip([clip, txt_clip.set_position(('center', clip.h - txt_clip.h - y_offset))])
    
    return final_clip

#Plops the zinnia watermark on a videoclip
def addLogo(video):

    # Load the watermark image
    watermark = ImageClip("resources/logo.png")

    # Resize the watermark if needed
    watermark = watermark.resize(height=50)  # Adjust the height to your needs

    # Set the position of the watermark (top-left corner)
    watermark = watermark.set_position((70, 85))

    watermark = watermark.set_opacity(.5)

    # Set the duration of the watermark to match the video duration
    watermark = watermark.set_duration(video.duration)

    # Composite the video and the watermark
    final_video = CompositeVideoClip([video, watermark])

    return final_video

#Creates the title-clip for a video
def makeTitle(text, size, duration=8):
    bg = ColorClip(size=size, color=(0, 0, 0), duration=duration)

    # Create a text clip with the desired caption, specify the width for wrapping
    caption = text
    title_text = TextClip(caption, font="resources/HelveticaNeueBold.otf", method="caption", align="west", fontsize=160, color='white', size=(size[0] - 800, None))
    title_text = title_text.set_duration(duration)

    # Calculate the position: centered on y-axis and 150 pixels from the left edge
    x_pos = 120
    y_pos = (1080 - title_text.size[1]) / 2

    # Apply the calculated position to the text clip
    title_text = title_text.set_pos((x_pos, y_pos))

    # Composite the text clip on top of the black screen
    return CompositeVideoClip(clips=[bg, title_text])

#Adds a specified background music to a video at a specified volume level
def addBGM(video, music, volume):
    bgm = (AudioFileClip(each) for each in music)
    audio = concatenate_audioclips(bgm)

    # Set the audio duration to match the video duration
    bg_audio = audio.set_duration(video.duration)
    bg_audio = bg_audio.volumex(volume)

    original_audio = video.audio

    mixed_audio = CompositeAudioClip([bg_audio, original_audio])

    # Set the audio to the concatenated video clip
    return video.set_audio(mixed_audio)