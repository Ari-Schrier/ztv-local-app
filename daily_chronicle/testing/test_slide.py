from daily_chronicle.slide_generation import generate_title_slide, pad_audio_with_silence
from daily_chronicle.audio_generation import generate_tts_gemini  # or your TTS function
from moviepy.editor import VideoFileClip
import os

# Dummy values for test
month = "June"
day = "12"
test_image_paths = [
    "daily_chronicle/temp/temp_image_files/manual_image_1.jpg",
    "daily_chronicle/temp/temp_image_files/manual_image_3.jpg",
    "daily_chronicle/temp/temp_image_files/manual_image_4.jpg",
]

# Make sure paths exist — fallback if needed
test_image_paths = [p for p in test_image_paths if os.path.exists(p)]

# Generate title slide clip
title_slide = generate_title_slide(month, day, generate_tts_gemini, test_image_paths)

title_slide.without_audio().write_videofile("daily_chronicle/temp/test_title_slide.mp4", fps=15)

