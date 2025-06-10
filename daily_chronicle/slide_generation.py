import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, ColorClip, TextClip
from moviepy.audio.AudioClip import AudioArrayClip, CompositeAudioClip
from PIL import Image
from io import BytesIO
import numpy as np

from daily_chronicle.genai_client import client, IMAGE_MODEL_ID

# Global video clip + temp file trackers
video_clips = []
temp_audio_files = []
temp_image_files = []

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

# --- Title slide generator ---
def generate_title_slide(month, day, generate_audio_function):
    text_content = f"What happened on {month} {day}? Let’s find out!!"
    narration_text = text_content
    audio_path = generate_audio_function(narration_text, "title_narration.wav")

    clip_audio = AudioFileClip(audio_path)

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


# --- Generate Event Pair ---
def generate_daily_chronicle_pair(event, index, generate_audio_function):
    from moviepy.editor import AudioFileClip, ImageClip
    import os

    clip1_text = f"{event['date_string']} {event['description']} {event['detail_1']}"
    clip2_text = event["detail_2"]

    print(f"🎙️ TTS: \"{clip1_text}\"")
    audio_path_1 = generate_audio_function(clip1_text, f"audio_{index + 1}_1.wav")
    print(f"🎙️ TTS: \"{clip2_text}\"")
    audio_path_2 = generate_audio_function(clip2_text, f"audio_{index + 1}_2.wav")
    temp_audio_files.extend([audio_path_1, audio_path_2])

    raw_clip_1 = AudioFileClip(audio_path_1)
    raw_clip_2 = AudioFileClip(audio_path_2)

    clip_1 = pad_audio_with_silence(raw_clip_1, pre_duration=1.0, post_duration=2.0)
    clip_2 = pad_audio_with_silence(raw_clip_2, pre_duration=1.0, post_duration=2.0)

    # --- Image Generation ---
    prompt = event["image_prompt"]
    print(f"🖼️ Generating image: \"{prompt}\"")

    result = client.models.generate_images(
        model=IMAGE_MODEL_ID,
        prompt=prompt,
        config={
            "number_of_images": 1,
            "output_mime_type": "image/jpeg",
            "aspect_ratio": "1:1",
            "safety_filter_level": "BLOCK_ONLY_HIGH",
            "person_generation": "ALLOW_ADULT"
        }
    )

    try:
        if not result.generated_images:
            raise ValueError("No images were generated.")

        image = Image.open(BytesIO(result.generated_images[0].image.image_bytes))

        image_out_path = f"temp/temp_image_files/event_image_{index + 1}.jpg"
        os.makedirs(os.path.dirname(image_out_path), exist_ok=True)
        image.save(image_out_path, format="JPEG")
        temp_image_files.append(image_out_path)

        print(f"✅ Image saved: {image_out_path}")

    except Exception as e:
        print("❌ Image generation failed:", e)

        # Add placeholder image path to maintain index alignment
        placeholder_path = "resources/image_fail_placeholder.jpg"
        if not os.path.exists(placeholder_path):
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new("RGB", (1080, 1080), color=(255, 255, 255))
            d = ImageDraw.Draw(img)
            d.text((100, 500), "No image generated", fill=(0, 0, 0))
            os.makedirs("resources", exist_ok=True)
            img.save(placeholder_path)

        temp_image_files.append(placeholder_path)
        return

    # --- Slide A (image left, text right) ---
    img_np = np.array(image)
    image_clip_left = (
        ImageClip(img_np)
        .set_duration(clip_1.duration)
        .resize(width=960)
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

    # --- Slide B (text left, image right) ---
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

    # --- Combine A → B with crossfade ---
    full_event_clip = concatenate_videoclips(
        [slide_1.crossfadeout(0.6), slide_2.crossfadein(0.6)],
        method="compose"
    )

    video_clips.append(full_event_clip)

    print(f"✅ Event clip created — duration {full_event_clip.duration:.2f}s")



# --- Export Final Video ---
def export_final_video(video_clips, temp_audio_files, temp_image_files):
    output_path = "output/daily_chronicle_final_video.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print(f"🎞️ Concatenating {len(video_clips)} video clips...")

    final_video = concatenate_videoclips(video_clips, method="compose")
    final_video.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")

    print("🧹 Cleaning up temp files...")
    # Optional: cleanup code here if needed

    return output_path
