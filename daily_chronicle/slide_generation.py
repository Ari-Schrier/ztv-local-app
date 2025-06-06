# daily_chronicle/video_generation.py

import os
import numpy as np
from io import BytesIO
from PIL import Image
import time
from base64 import b64encode
from IPython.display import display, HTML
import subprocess

from moviepy.editor import (
    TextClip, CompositeVideoClip, ColorClip, ImageClip, AudioFileClip,
    AudioClip, CompositeAudioClip, concatenate_videoclips
)
from moviepy.audio.AudioClip import AudioArrayClip

from daily_chronicle.genai_client import client, IMAGE_MODEL_ID
from daily_chronicle.audio_generation import generate_audio_live

# --- Tracking lists ---
temp_audio_files = []
temp_image_files = []
video_clips = []

# --- Padding helper ---
def pad_audio_with_silence(audio_clip, pre_duration=1.0, post_duration=2.0):
    pre_samples = int(audio_clip.fps * pre_duration)
    post_samples = int(audio_clip.fps * post_duration)
    silence_pre = np.zeros((pre_samples, audio_clip.nchannels), dtype=np.float32)
    silence_post = np.zeros((post_samples, audio_clip.nchannels), dtype=np.float32)

    pre_clip = AudioArrayClip(silence_pre, fps=audio_clip.fps)
    post_clip = AudioArrayClip(silence_post, fps=audio_clip.fps)

    full_clip = CompositeAudioClip([
        pre_clip.set_start(0),
        audio_clip.set_start(pre_duration),
        post_clip.set_start(pre_duration + audio_clip.duration)
    ])

    return full_clip.set_duration(pre_duration + audio_clip.duration + post_duration)

# --- Core function: generate video pair ---
# --- Core function: generate video pair ---
def generate_daily_chronicle_pair(event, index, generate_audio_function):
    print(f"\n🎞️ Generating slides for: {event['date_string']}")

    # --- Image Generation ---
    prompt = event["image_prompt"]
    result = client.models.generate_images(
        model=IMAGE_MODEL_ID,
        prompt=prompt,
        config={
            "number_of_images": 1,
            "output_mime_type": "image/jpeg",
            "aspect_ratio": "1:1"
        }
    )

    try:
        if not result.generated_images:
            raise ValueError("No images were generated.")
        image = Image.open(BytesIO(result.generated_images[0].image.image_bytes))
    except Exception as e:
        print("❌ Image generation failed:", e)
        return

    image_path = f"image_{index}.png"
    image.save(image_path)
    temp_image_files.append(image_path)

    # --- Audio Generation ---
    clip1_text = f"{event['date_string']} {event['description']} {event['detail_1']}"
    clip2_text = event["detail_2"]

    audio_path_1 = generate_audio_function(clip1_text, f"audio_{index}_1.wav")
    audio_path_2 = generate_audio_function(clip2_text, f"audio_{index}_2.wav")
    temp_audio_files.extend([audio_path_1, audio_path_2])

    raw_clip_1 = AudioFileClip(audio_path_1)
    raw_clip_2 = AudioFileClip(audio_path_2)

    clip_1 = pad_audio_with_silence(raw_clip_1, pre_duration=1.0, post_duration=3.0)
    clip_2 = pad_audio_with_silence(raw_clip_2, pre_duration=1.0, post_duration=3.0)

    # --- Slide A ---
    img_np = np.array(image)
    image_clip_left = (
        ImageClip(img_np)
        .set_duration(clip_1.duration)
        .resize(width=960)  # Half of 1920
        .set_position(("left", "center"))
    )

    text_slide_1 = TextClip(
        clip1_text,
        fontsize=36,  
        color='black',
        size=(960, 1080),
        method='caption'
    ).set_duration(clip_1.duration).set_position(("right", "center"))

    slide_1 = CompositeVideoClip(
        [
            ColorClip(size=(1920, 1080), color=(255, 255, 255)).set_duration(clip_1.duration),
            image_clip_left,
            text_slide_1
        ],
        size=(1920, 1080)
    ).set_audio(clip_1)

    # --- Slide B ---
    image_clip_right = (
        ImageClip(img_np)
        .set_duration(clip_2.duration)
        .resize(width=960)
        .set_position(("right", "center"))
    )

    text_slide_2 = TextClip(
        clip2_text,
        fontsize=36,
        color='black',
        size=(960, 1080),
        method='caption'
    ).set_duration(clip_2.duration).set_position(("left", "center"))

    slide_2 = CompositeVideoClip(
        [
            ColorClip(size=(1920, 1080), color=(255, 255, 255)).set_duration(clip_2.duration),
            image_clip_right,
            text_slide_2
        ],
        size=(1920, 1080)
    ).set_audio(clip_2)


    # --- Combine A → B ---
    full_event_clip = concatenate_videoclips(
        [slide_1.crossfadeout(0.6), slide_2.crossfadein(0.6)],
        method="compose"
    )

    video_clips.append(full_event_clip)

def save_slide_as_png_audio(slide_clip, audio_path, base_name):

    temp_video_dir = os.path.join("daily_chronicle", "temp_video_files")
    os.makedirs(temp_video_dir, exist_ok=True)

    # Step 1 — Save single PNG frame
    png_path = os.path.join(temp_video_dir, f"{base_name}.png")
    slide_clip.save_frame(png_path, t=0)

    # Step 2 — Combine PNG + audio → mp4
    mp4_path = os.path.join(temp_video_dir, f"{base_name}.mp4")

    cmd = [
        "ffmpeg",
        "-y",  # Overwrite
        "-loop", "1",
        "-i", png_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        mp4_path
    ]

    print(f"🎥 Saving slide → {mp4_path}")
    subprocess.run(cmd, check=True)

    return mp4_path

def run_crossfade_for_pair(slideA_path, slideB_path, output_path, fade_duration=0.6):
    import subprocess

    cmd = [
        "ffmpeg",
        "-y",
        "-i", slideA_path,
        "-i", slideB_path,
        "-filter_complex",
        f"""
        [0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset=0[v];
        [0:a][1:a]acrossfade=d={fade_duration}[a]
        """,
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-crf", "18",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]

    # Flatten multiline filter
    cmd = [arg.strip() if isinstance(arg, str) else arg for arg in cmd]

    print(f"⚡ Crossfading → {output_path}")
    subprocess.run(cmd, check=True)

    return output_path


# --- Batch runner ---
def run_generation_batches(events_list, batch_size=3):
    for i in range(0, len(events_list), batch_size):
        batch_events = events_list[i:i + batch_size]
        print(f"\nProcessing batch {i//batch_size + 1}/{(len(events_list) + batch_size - 1) // batch_size}...")
        for idx, event in enumerate(batch_events):
            generate_daily_chronicle_pair(event, i + idx)

def save_title_slide_as_png_audio(month, day, generate_audio_function, output_prefix="title"):
    text_content = f"What happened on {month} {day}? Let’s find out!!"
    narration_text = text_content
    audio_path = generate_audio_function(narration_text, "title_narration.wav")

    clip_audio = AudioFileClip(audio_path)
    temp_audio_files.append(audio_path)

    # ✅ NEW: Pad the audio
    padded_audio = pad_audio_with_silence(clip_audio)

    # ✅ NEW: Save padded audio to WAV
    padded_audio_path = os.path.join("daily_chronicle", "temp_video_files", f"{output_prefix}_padded.wav")
    padded_audio.write_audiofile(padded_audio_path, fps=44100)
    temp_audio_files.append(padded_audio_path)

    # Background
    background = ColorClip(size=(1920, 1080), color=(255, 255, 255)).set_duration(padded_audio.duration)

    # Left-side text
    title_text = TextClip(
        text_content.replace("? ", "?\n\n"),
        fontsize=50,
        color='black',
        size=(960, 1080),
        method='caption'
    ).set_duration(padded_audio.duration).set_position(("left", "center"))

    # Right-side icon
    icon_bg = ColorClip(size=(960, 1080), color=(230, 230, 255)).set_duration(padded_audio.duration)
    question_mark = TextClip(
        "?",
        fontsize=120,
        color='black',
        size=(960, 1080),
        method='caption'
    ).set_duration(padded_audio.duration).set_position("center")
    icon = CompositeVideoClip([icon_bg, question_mark])

    # Final title clip
    title_slide_clip = CompositeVideoClip(
        [background, title_text, icon.set_position(("right", "center"))],
        size=(1920, 1080)
    ).set_audio(padded_audio).fadein(0.5).fadeout(0.5)

    # ✅ Pass padded_audio_path to save_slide_as_png_audio
    title_mp4_path = save_slide_as_png_audio(title_slide_clip, padded_audio_path, output_prefix)

    return title_mp4_path


# --- Title slide generator ---
def generate_title_slide(month, day, generate_audio_function):
    text_content = f"What happened on {month} {day}? Let’s find out!!"
    narration_text = text_content
    audio_path = generate_audio_function(narration_text, "title_narration.wav")

    clip_audio = AudioFileClip(audio_path)
    temp_audio_files.append(audio_path)

    # Add silence (prepend and extend)
    padded_audio = pad_audio_with_silence(clip_audio)

    # Background
    background = ColorClip(size=(1920, 1080), color=(255, 255, 255)).set_duration(padded_audio.duration)

    # Left-side text
    title_text = TextClip(
        text_content.replace("? ", "?\n\n"),
        fontsize=50,
        color='black',
        size=(960, 1080),
        method='caption'
    ).set_duration(padded_audio.duration).set_position(("left", "center"))

    # Right-side icon
    icon_bg = ColorClip(size=(960, 1080), color=(230, 230, 255)).set_duration(padded_audio.duration)
    question_mark = TextClip(
        "?",
        fontsize=120,
        color='black',
        size=(960, 1080),
        method='caption'
    ).set_duration(padded_audio.duration).set_position("center")
    icon = CompositeVideoClip([icon_bg, question_mark])

    # Combine everything
    title_slide = CompositeVideoClip(
        [background, title_text, icon.set_position(("right", "center"))],
        size=(1920, 1080)
    ).set_audio(padded_audio).fadein(0.5).fadeout(0.5)

    return title_slide

def export_final_video(video_clips, temp_audio_files, temp_image_files, output_dir="outputs"):
    # Make sure output dir exists
    os.makedirs(output_dir, exist_ok=True)

    # Concatenate all clips
    final_video = concatenate_videoclips(video_clips)
    timestamp = int(time.time())
    output_filename = os.path.join(output_dir, f"{timestamp}_output_video.mp4")

    print(f"🎬 Writing final video to {output_filename} ...")
    final_video.write_videofile(output_filename, logger=None, fps=24, audio_codec='aac')

    # Display in notebook (optional — safe to skip if running in CLI)
    try:
        display(show_video(output_filename))
    except Exception:
        pass

    # Cleanup: close video clips and remove temp files
    final_video.close()
    for clip in video_clips:
        clip.close()

    for file in temp_audio_files + temp_image_files:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass

    print("✅ Cleanup done.")
    return output_filename

# Optional: notebook display helper
def show_video(video_path):
    """Display video in notebook"""
    with open(video_path, "rb") as video_file:
        video_bytes = video_file.read()
    video_b64 = b64encode(video_bytes).decode()
    video_tag = f'<video width="720" height="720" controls><source src="data:video/mp4;base64,{video_b64}" type="video/mp4"></video>'
    return HTML(video_tag)

def export_final_video_ffmpeg(video_clips, temp_audio_files, temp_image_files, output_dir="outputs"):
    import subprocess
    import os
    import time

    os.makedirs(output_dir, exist_ok=True)

    # Use your temp_video_files folder
    temp_video_dir = os.path.join("daily_chronicle", "temp", "temp_video_files")
    os.makedirs(temp_video_dir, exist_ok=True)

    concat_list_path = os.path.join(output_dir, "concat.txt")
    with open(concat_list_path, "w") as f:
        for idx, clip in enumerate(video_clips):
            temp_slide_path = os.path.abspath(os.path.join(temp_video_dir, f"temp_slide_{idx}.mp4"))
            clip.write_videofile(temp_slide_path, fps=24, audio_codec='aac')
            clip.close()
            f.write(f"file '{temp_slide_path}'\n")

    timestamp = int(time.time())
    output_filename = os.path.join(output_dir, f"{timestamp}_output_video.mp4")

    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        output_filename
    ]

    print(f"🚀 Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    print("✅ Cleaning up temp files...")
    for file in temp_audio_files + temp_image_files:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass

    print(f"🎉 Done! Final video: {output_filename}")
    return output_filename

def export_final_video_ffmpeg_v2(video_clips, output_dir="outputs"):
    import subprocess
    import os
    import time

    os.makedirs(output_dir, exist_ok=True)

    concat_list_path = os.path.join(output_dir, "concat.txt")
    with open(concat_list_path, "w") as f:
        for clip_path in video_clips:
            abs_path = os.path.abspath(clip_path)
            f.write(f"file '{abs_path}'\n")

    timestamp = int(time.time())
    output_filename = os.path.join(output_dir, f"{timestamp}_output_video.mp4")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        "-movflags", "+faststart",
        output_filename
    ]

    print(f"🚀 Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    print(f"🎉 Done! Final video: {output_filename}")
    return output_filename
