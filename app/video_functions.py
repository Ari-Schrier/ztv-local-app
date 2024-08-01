from moviepy.editor import *
import random

SIZE = (1920, 1080)

def combine_videos_with_transition(clips, transition_duration):
    return concatenate_videoclips([
            clip if i == 0 else clip.crossfadein(transition_duration)
            for i, clip in enumerate(clips)
        ],
        padding=-transition_duration, 
        method="compose"
    )

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

def make_video(title, location, data, question=None):

    clips = []

    title_text = makeTitle(title, SIZE)

    clips.append(title_text)

    for slide in data:
        newClip = ken_burns_effect(f"output/{location}/{slide['id']}.png", duration=21)
        newClip = add_caption(newClip, slide["text"])
        voice_over = AudioFileClip(f"output/{location}/{slide['id']}_text.mp3")
        silent_audio = AudioFileClip("resources/5-seconds-of-silence.mp3")
        if question:
            question = AudioFileClip(f"output/{location}/{slide['id']}_question.mp3")
            combined_voice_over = concatenate_audioclips([silent_audio, voice_over, silent_audio, question])
        else:
            combined_voice_over = concatenate_audioclips([silent_audio, voice_over])


        newClip = newClip.set_audio(combined_voice_over)
        clips.append(newClip.resize(SIZE))

    concat_clip = combine_videos_with_transition(clips,1)
    concat_clip = addLogo(concat_clip)
    end_card = VideoFileClip("resources/endcredits.m4v").resize(SIZE)
    concat_clip = combine_videos_with_transition([concat_clip, end_card],1)

    # Load the background music
    audio1 = AudioFileClip(f"output/{location}/{location}1.mp3")
    audio2 = AudioFileClip(f"output/{location}/{location}2.mp3")
    audio3 = AudioFileClip(f"output/{location}/{location}3.mp3")
    audio4 = AudioFileClip(f"output/{location}/{location}4.mp3")
    audio = concatenate_audioclips([audio1, audio2, audio3, audio4])

    # Set the audio duration to match the video duration
    bg_audio = audio.set_duration(concat_clip.duration)
    bg_audio = bg_audio.volumex(0.3)


    concat_audio = concat_clip.audio

    mixed_audio = CompositeAudioClip([bg_audio, concat_audio])

    # Set the audio to the concatenated video clip
    concat_clip = concat_clip.set_audio(mixed_audio)

    concat_clip.write_videofile(f"output/{title}.mp4", fps=24)

