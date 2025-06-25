import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, ColorClip, TextClip
from PIL import Image, ImageDraw, ImageFilter
import numpy as np


from pathlib import Path

from daily_chronicle.utils_tts import pad_audio_with_silence

# Global video clip + temp file trackers
video_paths = []
temp_audio_files = []
temp_image_files = []

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
BLUR_STRENGTH = 200
OVERLAY_OPACITY = 60
SPACE_AROUND_IMAGE = 100
FONT_PATH = "resources/HelveticaNeueMedium.otf"

# --- Title slide generator ---
def generate_title_slide(month, day, generate_tts_function, image_paths=None):
    title_content = f"The Daily Chronicle"
    subtitle_content = f"{month} {day}"
    narration_text = f"Welcome to the Daily Chronicle. Today, we will explore the historical events that occurred on {month} {day}. Let's find out what happened on this day in history."
    audio_path = generate_tts_function(narration_text, "title_narration.wav")
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

def build_event_segment(event, index, audio_paths, image_path):
    """
    Generate the complete video slides with audio and image.
    Returns the video clip for the event.
    """

    # Defensive check for missing image
    if not image_path or not os.path.exists(image_path):
        raise ValueError(f"❌ Invalid or missing image path for event {index + 1}: {image_path}")
    
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
    output_path = temp_dir / f"event_{index + 1:02d}.mp4"

    if not event.get("is_birthday", False):
        # Define PNG output paths
        png_a = temp_dir / f"event_{index + 1:02d}_A.png"
        png_b = temp_dir / f"event_{index + 1:02d}_B.png"
        temp_image_files.extend([png_a, png_b])

        slide_1.save_frame(str(png_a), t=0)
        slide_2.save_frame(str(png_b), t=0)

        slide_1 = ImageClip(png_a).set_duration(padded_audio_1.duration).set_audio(padded_audio_1)
        slide_2 = ImageClip(png_b).set_duration(padded_audio_2.duration).set_audio(padded_audio_2)

    # --- Combine A → B with crossfade ---
    full_event_clip = concatenate_videoclips(
        [slide_1.crossfadeout(0.6), slide_2.crossfadein(0.6)],
        method="compose"
    )

    # --- Write to .mp4 and return VideoFileClip ---
    full_event_clip.write_videofile(str(output_path), fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)

    print(f"✅ Event clip created — duration {full_event_clip.duration:.2f}s")
    print(f"✅ Event clip saved → {str(output_path)}")

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

def cleanup_temp_files(temp_audio_files, temp_image_files, temp_video_files, temp_json_files):
    def safe_remove(path: str):
        try:
            path_to_del = Path(path)
            if path_to_del.exists():
                path_to_del.unlink()
        except Exception as e:
            print(f"⚠️ Could not delete {path}: {e}")

    print("🧹 Cleaning up temp audio files...")
    for path in temp_audio_files:
        safe_remove(path)

    print("🧹 Cleaning up temp image files...")
    for path in temp_image_files:
        safe_remove(path)

    print("🧹 Cleaning up temp video files...")
    for path in temp_video_files:
        safe_remove(path)

    print("🧹 Cleaning up temp JSON files...")
    for path in temp_json_files:
        safe_remove(path)
