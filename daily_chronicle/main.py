# daily_chronicle/main.py

from daily_chronicle.generator import generate_event_sequence
from daily_chronicle.slide_generation import (
    generate_daily_chronicle_pair,
    generate_title_slide,
    export_final_video,
    video_clips,
    temp_audio_files,
    temp_image_files,
)
from daily_chronicle.audio_generation import generate_audio_tts
import json
import os

from PySide6.QtWidgets import QApplication

def main():
    print("📅 Welcome to the Daily Chronicle Generator!")
    
    # --- Get user input ---
    month = input("Enter month (e.g. May): ").strip()
    day_input = input("Enter day (1-31): ").strip()

    try:
        day = int(day_input)
        if not (1 <= day <= 31):
            raise ValueError()
    except ValueError:
        print("❌ Invalid day. Please enter a number between 1 and 31.")
        return

    num_events = 12  # Default number of events

    # --- Generate events ---
    print("\n🧠 Generating events...")
    events = generate_event_sequence(month, day, num_events)

    if not events or not isinstance(events, list):
        print("❌ No events were generated. Exiting.")
        return

    # --- Save event JSON ---
    os.makedirs("outputs", exist_ok=True)
    json_path = f"outputs/daily_chronicle_{month}_{day}.json"
    with open(json_path, "w") as f:
        json.dump(events, f, indent=2)
    print(f"✅ Saved event JSON to {json_path}")

    # --- Launch Event Review ---
    print("\n📝 Launching EVENT REVIEW window...")
    from daily_chronicle.event_review import EventReviewWindow

    app = QApplication([])
    event_window = EventReviewWindow(json_path)
    event_window.show()
    app.exec()

    print("✅ Event review complete.")

    # --- Reload reviewed JSON ---
    with open(json_path, "r") as f:
        reviewed_events = json.load(f)

    # --- Generate TTS + Images ---
    print("\n🎬 Generating TTS + IMAGES...")

    # Title slide
    title_slide = generate_title_slide(month, day, generate_audio_tts)
    video_clips.append(title_slide)

    # Event slides + image generation
    for idx, event in enumerate(reviewed_events):
        print(f"\n👉 Generating event {idx + 1}/{len(reviewed_events)}...")
        generate_daily_chronicle_pair(event, idx, generate_audio_tts)

    # --- Save image paths for review ---
    os.makedirs("temp", exist_ok=True)
    image_paths_json = f"temp/daily_chronicle_images_{month}_{day}.json"
    with open(image_paths_json, "w") as f:
        json.dump(temp_image_files, f, indent=2)

    print(f"\n✅ Saved image paths JSON to {image_paths_json}")

    # --- Launch Image Review ---
    print("\n🖼️ Launching IMAGE REVIEW window...")
    from daily_chronicle.image_review import ImageReviewWindow

    with open(image_paths_json, "r") as f:
        image_paths = json.load(f)

    image_window = ImageReviewWindow(json_path, image_paths)
    image_window.show()
    app.exec()

    print("✅ Image review complete.")

    # --- Export final video ---
    print("\n🚀 Exporting final video...")
    output_path = export_final_video(video_clips, temp_audio_files, temp_image_files)
    print(f"\n🎉 Done! Video exported to: {output_path}")

if __name__ == "__main__":
    main()
