from daily_chronicle.slide_generation import build_event_segment
from daily_chronicle.audio_generation import generate_tts_gemini
import os

from daily_chronicle.utils_tts import pad_audio_with_silence

# Sample event
event = {
    "date_string": "On June 12, 1967: ",
    "header_title": "Supreme Court Rules on Interracial Marriage",
    "description": "The Supreme Court rules in Loving v. Virginia that state bans on interracial marriage are unconstitutional.",
    "detail_1": "This landmark case was decided unanimously by the Supreme Court.",
    "detail_2": "This landmark civil rights decision invalidated laws in 16 U.S. states.",
    "image_prompt": "Supreme Court interracial marriage ruling"
}

# Provide a real image path
image_path = "daily_chronicle/temp/temp_image_files/regen_image_1.jpg"

audio_path_1 = 'daily_chronicle/temp/temp_audio_files/title_narration.wav'
audio_path_2 = 'daily_chronicle/temp/temp_audio_files/title_narration.wav'

# Call the function
clip = build_event_segment(event, 0, [audio_path_1, audio_path_2], image_path)

# Or export to file
clip.without_audio().write_videofile("test_event_segment.mp4", fps=30, codec="libx264", audio_codec="aac")
