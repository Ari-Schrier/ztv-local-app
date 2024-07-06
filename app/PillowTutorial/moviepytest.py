from moviepy.editor import *
import json

def combine_videos_with_transition(clips, transition_duration):
    return concatenate_videoclips([
            clip if i == 0 else clip.crossfadein(transition_duration)
            for i, clip in enumerate(clips)
        ],
        padding=-transition_duration, 
        method="compose"
    )

def ken_burns_effect(image_path, duration, zoom_start=1.0, zoom_end=1.1):
    clip = ImageClip(image_path)
    w, h = clip.size
    
    def make_frame(t):
        zoom = zoom_start + (zoom_end - zoom_start) * (t / duration)
        return clip.crop(x_center=w/2, y_center=h/2, width=w/zoom, height=h/zoom).resize((w, h)).get_frame(t)
    
    return VideoClip(make_frame, duration=duration)

def add_caption(clip, text, fontsize=72, font='Arial-Bold', position='bottom', bg_opacity=0.6):
    # Create the text clip
    txt_clip = TextClip(text, fontsize=fontsize, color='white', font=font).set_duration(clip.duration)
    
    # Create the background clip
    txt_bg = ColorClip(size=(txt_clip.w + 20, txt_clip.h + 10), color=(0, 0, 0)).set_duration(clip.duration)
    txt_bg = txt_bg.set_opacity(bg_opacity)
    
    # Position the text over the background
    txt_clip = txt_clip.set_position(('center', position))
    txt_bg = txt_bg.set_position(('center', position))
    
    # Composite the text and background
    txt_composite = CompositeVideoClip([txt_bg, txt_clip])
    
    # Composite the text with the main clip
    final_clip = CompositeVideoClip([clip, txt_composite.set_position(('center', position))])
    
    return final_clip

filename = "output/Adorable Kittens/Adorable Kittens.json"
with open(filename, 'r') as file:
    data = json.load(file)

clips = []
for slide in data:
    newClip =  ken_burns_effect(slide["photo"], 10)
    newClip = add_caption(newClip, slide["title"][0])
    clips.append(newClip)

concat_clip = combine_videos_with_transition(clips,1)

# Load the background music
audio = AudioFileClip("resources/gymno.mp3")

# Set the audio duration to match the video duration
audio = audio.set_duration(concat_clip.duration)

# Set the audio to the concatenated video clip
concat_clip = concat_clip.set_audio(audio)

concat_clip.write_videofile("output/kittens.mp4", fps=24)