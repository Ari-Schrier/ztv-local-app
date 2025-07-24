import os
import subprocess
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, TextClip
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from daily_chronicle.utils_logging import emoji


from pathlib import Path

from daily_chronicle.utils_tts import pad_audio_with_silence

# Global video clip + temp file trackers
video_paths = []
temp_audio_files = []
temp_image_files = []
temp_json_files = []

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
BLUR_STRENGTH = 200
OVERLAY_OPACITY = 60
SPACE_AROUND_IMAGE = 100
FONT_PATH = "resources/HelveticaNeueMedium.otf"

# --- Title slide generator ---
def generate_title_slide(month, day, generate_tts_function, image_paths=None):
    title_content = "The Daily Chronicle"
    subtitle_content = f"{month} {day}"
    narration_text = f"Welcome to the Daily Chronicle. Today, we will explore the historical events that occurred on {month} {day}. Let's find out what happened on this day in history."
    audio_path = str(generate_tts_function(narration_text, "title_narration.wav"))
    temp_audio_files.append(audio_path)

    clip_audio = AudioFileClip(audio_path)

    # Add silence (prepend and extend)
    padded_audio = pad_audio_with_silence(clip_audio)

    if image_paths and os.path.exists(image_paths[0]):
        first_image_path = image_paths[0]

    # Background
    background_image_left_logo = create_beautiful_background(first_image_path, image_pos="right", logo_pos=(70, 85))
    background_clip_left_logo = ImageClip(np.array(background_image_left_logo))

    # Left-side title
    title_text = TextClip(
        title_content,
        fontsize=90,
        font=FONT_PATH,
        color='white',
        method='label'
    ).set_duration(padded_audio.duration).set_position((70, 200))
    
    # Left-side subtitle
    subtitle_text = TextClip(
        subtitle_content,
        fontsize=85,
        font=FONT_PATH,
        color='white',
        method='label'
    ).set_duration(padded_audio.duration).set_position((70, 400))

    # Combine everything
    title_slide = CompositeVideoClip(
        [background_clip_left_logo, title_text, subtitle_text],
        size=(1920, 1080)
    ).set_duration(padded_audio.duration)
    
    title_slide = title_slide.set_audio(padded_audio).fadein(0.6).fadeout(0.6)

    return title_slide

def build_event_segment(event, index, audio_paths, image_path, logger=print):
    """
    Generate the complete video slides with audio and image.
    Returns the video clip for the event.
    """

    # Defensive check for missing image
    if not image_path or not os.path.exists(image_path):
        raise ValueError(f"{emoji('cross_mark')} Invalid or missing image path for event {index + 1}: {image_path}")

    # Texts for Slides
    clip1_toptext = f"{event['date_string']} {event['header_title']}"
    clip1_centertext = f"{event['description']} {event['detail_1']}"
    clip2_text = event["detail_2"]

    if audio_paths:
        # Load audio clips
        raw_clip_1 = AudioFileClip(audio_paths[0])
        raw_clip_2 = AudioFileClip(audio_paths[1])

        # Pad audio clips
        padded_audio_1 = pad_audio_with_silence(raw_clip_1)
        padded_audio_2 = pad_audio_with_silence(raw_clip_2)

    # Create background
    background_image_left_logo = create_beautiful_background(image_path, image_pos="right", logo_pos=(70, 85))
    background_image_right_logo = create_beautiful_background(image_path, image_pos="left", logo_pos=(1644, 85))

    # Convert PIL Image to MoviePy ImageClip
    background_clip_left_logo = ImageClip(np.array(background_image_left_logo))
    background_clip_right_logo = ImageClip(np.array(background_image_right_logo))

    # --- Slide A (image left, text right) ---
    text_slide_1_top = TextClip(
        clip1_toptext,
        fontsize=60,
        font=FONT_PATH,
        color='white',
        size=(770, None),
        method='caption'
    ).set_duration(padded_audio_1.duration).set_position((70, 200))
    
    text_slide_1_center = TextClip(
        clip1_centertext,
        fontsize=48,
        font=FONT_PATH,
        color='white',
        size=(770, None),
        method='caption'
    ).set_duration(padded_audio_1.duration).set_position((70, 500))

    slide_1 = CompositeVideoClip(
        [
            background_clip_left_logo,
            text_slide_1_top,
            text_slide_1_center
        ],
        size=(1920, 1080)
    ).set_audio(padded_audio_1).set_duration(padded_audio_1.duration)

    # --- Slide B (text left, image right) ---
    text_slide_2 = TextClip(
        clip2_text,
        fontsize=48,
        font=FONT_PATH,
        color='white',
        size=(770, None),
        method='caption'
    ).set_duration(padded_audio_2.duration).set_position((1080, 400))

    slide_2 = CompositeVideoClip(
        [
            background_clip_right_logo,
            text_slide_2
        ],
        size=(1920, 1080)
    ).set_audio(padded_audio_2).set_duration(padded_audio_2.duration)

    # --- Folder + Output path ---
    temp_dir = Path("daily_chronicle") / "temp" / "temp_video_files"
    temp_dir.mkdir(parents=True, exist_ok=True)
    output_path = temp_dir / f"event_{index + 1}.mp4"

    logger(f"\n{emoji('frame')} Building clip for event {index + 1}...")

    if not event.get("is_birthday", False):
        # Define PNG output paths
        png_a = temp_dir / f"event_{index + 1:02d}_A.png"
        png_b = temp_dir / f"event_{index + 1:02d}_B.png"
        temp_image_files.extend([png_a, png_b])

        slide_1.save_frame(str(png_a), t=0)
        slide_2.save_frame(str(png_b), t=0)

        slide_1 = ImageClip(str(png_a)).set_duration(padded_audio_1.duration).set_audio(padded_audio_1)
        slide_2 = ImageClip(str(png_b)).set_duration(padded_audio_2.duration).set_audio(padded_audio_2)

    # --- Combine A → B with crossfade ---
    full_event_clip = concatenate_videoclips(
        [slide_1.crossfadeout(0.6), slide_2.crossfadein(0.6)],
        method="compose"
    )

    # --- Write to .mp4 and return VideoFileClip ---
    full_event_clip.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)

    logger(f"{emoji('check')} Event clip created — duration {full_event_clip.duration:.2f}s")
    logger(f"{emoji('check')} Event clip saved → {str(output_path)}")

    return str(output_path)

def build_event_segment_ffmpeg(event, index, audio_paths, image_path, logger=print):
    if not image_path or not Path(image_path).exists():
        raise ValueError(f"{emoji('cross_mark')} Invalid or missing image path for event {index + 1}: {image_path}")

    clip1_toptext = f"{event['date_string']} {event['header_title']}"
    clip1_centertext = f"{event['description']} {event['detail_1']}"
    clip2_text = event["detail_2"]

    # Load and pad audio
    padded_audio_1 = pad_audio_with_silence(AudioFileClip(audio_paths[0]))
    padded_audio_2 = pad_audio_with_silence(AudioFileClip(audio_paths[1]))

    temp_dir = Path("daily_chronicle") / "temp" / "temp_video_files"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Paths
    png_a = temp_dir / f"event_{index + 1:02d}_A.png"
    png_b = temp_dir / f"event_{index + 1:02d}_B.png"
    wav_a = temp_dir / f"event_{index + 1:02d}_A.wav"
    wav_b = temp_dir / f"event_{index + 1:02d}_B.wav"
    mp4_a = temp_dir / f"event_{index + 1:02d}_A.mp4"
    mp4_b = temp_dir / f"event_{index + 1:02d}_B.mp4"
    output_path = temp_dir / f"event_{index + 1}.mp4"

    # Slide A
    bg_a = create_beautiful_background(image_path, image_pos="right", logo_pos=(70, 85))
    img_clip_a = ImageClip(np.array(bg_a)).set_duration(padded_audio_1.duration)
    text_top = TextClip(clip1_toptext, fontsize=60, font=FONT_PATH, color='white', size=(770, None), method='caption').set_position((70, 200))
    text_center = TextClip(clip1_centertext, fontsize=48, font=FONT_PATH, color='white', size=(770, None), method='caption').set_position((70, 500))
    slide_a = CompositeVideoClip([img_clip_a, text_top.set_duration(img_clip_a.duration), text_center.set_duration(img_clip_a.duration)], size=(1920, 1080))
    slide_a.save_frame(str(png_a), t=0)

    # Slide B
    bg_b = create_beautiful_background(image_path, image_pos="left", logo_pos=(1644, 85))
    img_clip_b = ImageClip(np.array(bg_b)).set_duration(padded_audio_2.duration)
    text_right = TextClip(clip2_text, fontsize=48, font=FONT_PATH, color='white', size=(770, None), method='caption').set_position((1080, 400))
    slide_b = CompositeVideoClip([img_clip_b, text_right.set_duration(img_clip_b.duration)], size=(1920, 1080))
    slide_b.save_frame(str(png_b), t=0)

    temp_image_files.extend([png_a, png_b])

    # Export audio
    padded_audio_1.write_audiofile(str(wav_a), fps=44100, logger=None, verbose=False)
    padded_audio_2.write_audiofile(str(wav_b), fps=44100, logger=None, verbose=False)

    dur1 = round(padded_audio_1.duration, 3)
    dur2 = round(padded_audio_2.duration, 3)

    # Create slide A video
    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1", "-r", "24", "-i", str(png_a),
        "-i", str(wav_a),
        "-t", str(dur1),
        "-vf", "format=yuv420p",
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        str(mp4_a)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Create slide B video
    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1", "-r", "24", "-i", str(png_b),
        "-i", str(wav_b),
        "-t", str(dur2),
        "-vf", "format=yuv420p",
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "192k",
        str(mp4_b)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # FFmpeg crossfade: calculate when to start

    crossfade = 0.6
    xfade_start = dur1 - crossfade

    # Crossfade filter
    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(mp4_a),
        "-i", str(mp4_b),
        "-filter_complex",
        f"[0:v][1:v]xfade=transition=fade:duration={crossfade}:offset={xfade_start},format=yuv420p[v];"
        f"[0:a]aresample=async=1:first_pts=0[a0];"
        f"[1:a]aresample=async=1:first_pts=0[a1];"
        f"[a0][a1]acrossfade=d={crossfade}[a]",
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-ac", "2",
        "-ar", "44100",
        str(output_path)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    logger(f"{emoji('check')} Event clip created — duration ≈ {dur1 + dur2 - crossfade:.2f}s")
    logger(f"{emoji('check')} Event clip saved → {output_path}")

    return str(output_path)

def build_event_segment_ffmpeg_edited(event, index, audio_paths, image_path, logger=print):
    if not image_path or not Path(image_path).exists():
        raise ValueError(f"{emoji('cross_mark')} Invalid or missing image path for event {index + 1}: {image_path}")

    clip1_toptext = f"{event['date_string']} {event['header_title']}"
    clip1_centertext = f"{event['description']} {event['detail_1']}"
    clip1_bottomtext = event["detail_2"]

    # Load and pad audio
    padded_audio_1 = pad_audio_with_silence(AudioFileClip(audio_paths[0]), pre_duration=2.5, post_duration=2)
    padded_audio_2 = pad_audio_with_silence(AudioFileClip(audio_paths[1]), pre_duration=2.5, post_duration=3)
    padded_audio_3 = pad_audio_with_silence(AudioFileClip(audio_paths[2]), pre_duration=2.5, post_duration=5)

    temp_dir = Path("daily_chronicle") / "temp" / "temp_video_files"
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Paths
    png_a = temp_dir / f"event_{index + 1:02d}_A.png"
    png_b = temp_dir / f"event_{index + 1:02d}_B.png"
    png_c = temp_dir / f"event_{index + 1:02d}_C.png"
    png_d = temp_dir / f"event_{index + 1:02d}_D.png"
    wav_b = temp_dir / f"event_{index + 1:02d}_B.wav"
    wav_c = temp_dir / f"event_{index + 1:02d}_C.wav"
    wav_d = temp_dir / f"event_{index + 1:02d}_D.wav"
    mp4_a = temp_dir / f"event_{index + 1:02d}_A.mp4"
    mp4_b = temp_dir / f"event_{index + 1:02d}_B.mp4"
    mp4_c = temp_dir / f"event_{index + 1:02d}_C.mp4"
    mp4_d = temp_dir / f"event_{index + 1:02d}_D.mp4"
    output_path = temp_dir / f"event_{index + 1}.mp4"

    # Slide A
    bg_a = create_beautiful_background(image_path, image_pos="right", logo_pos=(70, 85))
    img_clip_a = ImageClip(np.array(bg_a))
    text_top = TextClip(clip1_toptext, fontsize=60, font=FONT_PATH, color='white', size=(770, None), method='caption').set_position((70, 200))
    text_center = TextClip(clip1_centertext, fontsize=48, font=FONT_PATH, color='white', size=(770, None), method='caption').set_position((70, 500))
    text_bottom = TextClip(clip1_bottomtext, fontsize=48, font=FONT_PATH, color='white', size=(770, None), method='caption').set_position((70, 800))
    
    slide_a = CompositeVideoClip([img_clip_a], size=(1920, 1080))
    slide_a.save_frame(str(png_a), t=0)
    slide_b = CompositeVideoClip([img_clip_a, text_top.set_duration(padded_audio_1.duration)], size=(1920, 1080))
    slide_b.save_frame(str(png_b), t=0)
    slide_c = CompositeVideoClip([img_clip_a, text_top, text_center.set_duration(padded_audio_2.duration)], size=(1920, 1080))
    slide_c.save_frame(str(png_c), t=0)
    slide_d = CompositeVideoClip([img_clip_a, text_top, text_center, text_bottom.set_duration(padded_audio_3.duration)], size=(1920, 1080))
    slide_d.save_frame(str(png_d), t=0)

    temp_image_files.extend([png_a, png_b, png_c, png_d])

    # Export audio
    padded_audio_1.write_audiofile(str(wav_b), fps=44100, logger=None, verbose=False)
    padded_audio_2.write_audiofile(str(wav_c), fps=44100, logger=None, verbose=False)
    padded_audio_3.write_audiofile(str(wav_d), fps=44100, logger=None, verbose=False)

    dur_b = round(padded_audio_1.duration, 3)
    dur_c = round(padded_audio_2.duration, 3)
    dur_d = round(padded_audio_3.duration, 3)

    crossfade = 1.5

    offset_ab = 1

    dur_a = crossfade + offset_ab
    
    offset_bc = offset_ab + dur_b - crossfade
    offset_cd = offset_bc + dur_c - crossfade
    offset_dblack = offset_cd + dur_d - 2.5

    # Create slide A video
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(png_a),
        "-t", str(dur_a),  # must be at least offset + fade
        "-vf", "format=yuv420p,fade=t=in:st=0:d=1.5",
        "-c:v", "libx264", "-r", "24", str(mp4_a)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Slides B, C, D (no fade, just static durations)
    for i, (png, mp4, dur) in enumerate(zip(
        [png_b, png_c, png_d],
        [mp4_b, mp4_c, mp4_d],
        [dur_b, dur_c, dur_d]
    )):
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(png),
            "-t", str(dur), "-vf", "format=yuv420p",
            "-c:v", "libx264", "-r", "24", str(mp4)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # FFmpeg crossfade: calculate when to start
    subprocess.run([
    "ffmpeg", "-y",
    "-i", str(mp4_a),
    "-i", str(mp4_b),
    "-i", str(mp4_c),
    "-i", str(mp4_d),
    "-i", "resources/black_nologo.mp4",
    "-i", str(wav_b),
    "-i", str(wav_c),
    "-i", str(wav_d),
    "-filter_complex",
    f"""
    [0:v][1:v]xfade=transition=fade:duration={crossfade}:offset={offset_ab}[v1];
    [v1][2:v]xfade=transition=fade:duration={crossfade}:offset={offset_bc}[v2];
    [v2][3:v]xfade=transition=fade:duration={crossfade}:offset={offset_cd}[v3];
    [v3][4:v]xfade=transition=fade:duration={crossfade}:offset={offset_dblack}[vout];

    [5:a][6:a]acrossfade=d=1.5[a01];
    [a01][7:a]acrossfade=d=1.5[aout]
    """.replace("\n", "").strip(),
    "-map", "[vout]",
    "-map", "[aout]",
    "-c:v", "libx264",
    "-c:a", "aac",
    "-ac", "2",
    "-ar", "44100",
    "-pix_fmt", "yuv420p",
    "-shortest",
    str(output_path)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    logger(f"{emoji('check')} Event clip created — duration ≈ {dur_b + dur_c + dur_d - (3 * crossfade):.2f}s")
    logger(f"{emoji('check')} Event clip saved → {output_path}")

    return str(output_path)

def create_beautiful_background(image_path, logo_pos=(70, 85), image_pos="left"):
    with Image.open(image_path) as image:
        # Adjust aspect ratio
        image_ratio = image.width / image.height
        target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT
        if image_ratio > target_ratio:
            new_width = int(image.height * target_ratio)
            offset = (image.width - new_width) // 2
            cropped_image = image.crop((offset, 0, offset + new_width, image.height))
        else:
            new_height = int(image.width / target_ratio)
            offset = (image.height - new_height) // 2
            cropped_image = image.crop((0, offset, image.width, offset + new_height))

        # Resize to 1920x1080
        resized_image = cropped_image.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)

        # Add scrim overlay
        overlay = Image.new('RGBA', resized_image.size, (0, 0, 0, int((OVERLAY_OPACITY / 100) * 255)))
        image_with_scrim = Image.alpha_composite(resized_image.convert('RGBA'), overlay)

        # Apply blur
        final_background = image_with_scrim.filter(ImageFilter.GaussianBlur(radius=BLUR_STRENGTH))

        # Ensure image is square with rounded edges
        image_size = 1080 - 2*SPACE_AROUND_IMAGE
        image = image.resize((image_size, image_size), Image.LANCZOS)

        # Create a mask for rounded corners
        mask = Image.new('L', image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, image_size, image_size], radius=50, fill=255)

        # Apply the rounded mask to the image
        image_with_rounded_corners = Image.new('RGBA', image.size)
        image_with_rounded_corners.paste(image, (0, 0), mask=mask)

        # Position the image on the appropriate side of the video frame
        if image_pos == "right":
            image_position = (VIDEO_WIDTH - image_with_rounded_corners.width - SPACE_AROUND_IMAGE, SPACE_AROUND_IMAGE)  # Adjust positioning as necessary
        else:
            image_position = (SPACE_AROUND_IMAGE, SPACE_AROUND_IMAGE)

        final_background.paste(image_with_rounded_corners, image_position, image_with_rounded_corners)

        # Add watermark
        watermark = Image.open("resources/logo_small.png")
        final_background.paste(watermark, logo_pos, watermark)

        return final_background

def cleanup_temp_files(temp_audio_files, temp_image_files, temp_video_files, temp_json_files, logger=print):
    def safe_remove(path: str):
        try:
            path_to_del = Path(path)
            if path_to_del.exists():
                path_to_del.unlink()
        except Exception as e:
            logger(f"{emoji('cross_mark')} Could not delete {path}: {e}")

    logger(f"{emoji('broom')} Cleaning up temp audio files...")
    for path in temp_audio_files:
        safe_remove(path)

    logger(f"{emoji('broom')} Cleaning up temp image files...")
    for path in temp_image_files:
        safe_remove(path)

    logger(f"{emoji('broom')} Cleaning up temp video files...")
    for path in temp_video_files:
        safe_remove(path)

    logger(f"{emoji('broom')} Cleaning up temp JSON files...")
    for path in temp_json_files:
        safe_remove(path)