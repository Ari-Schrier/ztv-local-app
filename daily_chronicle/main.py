# daily_chronicle/main.py

from daily_chronicle.generator import generate_event_sequence
from daily_chronicle.slide_generation import *
from daily_chronicle.audio_generation import generate_audio_tts
from daily_chronicle.event_review import EventReviewWindow
import json
import os

from PySide6.QtWidgets import QApplication

NUM_EVENTS = 12  # Number of events to generate

def main():
    print("📅 Welcome to the Daily Chronicle Generator!")
    
    # --- Step 1: Get user input ---
    month = input("Enter month (e.g. May): ").strip()
    day_input = input("Enter day (1-31): ").strip()

    try:
        day = int(day_input)
        if not (1 <= day <= 31):
            raise ValueError()
    except ValueError:
        print("❌ Invalid day. Please enter a number between 1 and 31.")
        return

    # --- Step 2: Generate events ---
    print("\n🧠 Generating events...")
    events = generate_event_sequence(month, day, NUM_EVENTS)

    if not events or not isinstance(events, list):
        print("❌ No events were generated. Exiting.")
        return

    # --- Save event JSON ---
    os.makedirs("outputs", exist_ok=True)
    event_json_filepath = f"outputs/daily_chronicle_{month}_{day}.json"
    with open(event_json_filepath, "w") as f:
        json.dump(events, f, indent=2)
    print(f"✅ Saved event JSON to {event_json_filepath}")

    # --- Step 3: Launch Event Review ---
    print("\n📝 Launching EVENT REVIEW window...")

    app = QApplication([])
    event_window = EventReviewWindow(event_json_filepath)
    event_window.show()
    app.exec()
    print("✅ Event review complete.")

    # --- Step 4: Load reviewed events ---
    with open(event_json_filepath, "r") as f:
        reviewed_events = json.load(f)

    # --- Step 5: Generate image + audio assets + save paths ---
    os.makedirs("daily_chronicle/temp", exist_ok=True)
    temp_event_assets = []
    for idx, event in enumerate(reviewed_events):
        print(f"\n🖼️ Generating assets for event {idx + 1}/{len(reviewed_events)}...")
        image_path = generate_event_image(event, idx)
        audio_path_1, audio_path_2 = generate_event_audio(event, idx, generate_audio_tts)
        temp_event_assets.append({
            "event_index": idx,
            "image_path": image_path,
            "audio_path_1": audio_path_1,
            "audio_path_2": audio_path_2
        })
    
    temp_event_assets_filepath = f"daily_chronicle/temp/daily_chronicle_assets_{month}_{day}.json"
    with open(temp_event_assets_filepath, "w") as f:
        json.dump(temp_event_assets, f, indent=2)
    
    print(f"✅ Saved event assets to {temp_event_assets_filepath}")

    # --- Step 6: Launch Image Review ---

    print("\n🖼️ Launching IMAGE REVIEW window...")
    from daily_chronicle.image_review import ImageReviewWindow

    image_window = ImageReviewWindow(event_json_filepath, temp_event_assets_filepath)
    image_window.show()
    app.exec()
    print("✅ Image review complete.")

    # --- Step 7: Load review image/audio paths ---
    with open(temp_event_assets_filepath, "r") as f:
        reviewed_assets = json.load(f)

    # --- Step 8: Generate video slides ---
    print("\n🎬 Assembling final video...")

    title_slide = generate_title_slide(month, day, generate_audio_tts)
    video_clips.append(title_slide)

    for asset in reviewed_assets:
        idx = asset["event_index"]
        event = reviewed_events[idx]
        print(f"\n🎥 Building video slide for event {idx + 1}...")

        audio_paths = (asset["audio_path_1"], asset["audio_path_2"])
        image_path = asset["image_path"]

        event_segment = build_event_segment(event, idx, audio_paths, image_path)
        video_clips.append(event_segment)

    # --- Step 9: Export final video ---
    print("\n🚀 Exporting final video...")
    try:
        output_path = export_final_video(video_clips)
        print(f"\n🎉 Done! Video exported to: {output_path}")
    finally:
        print("\n🧹 Cleaning up temporary files...")
        cleanup_temp_files(temp_audio_files, temp_image_files)
        print("✅ Temporary files cleaned up.")
        print("\n🎬 Daily Chronicle completed successfully!")

if __name__ == "__main__":
    main()
