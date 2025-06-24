# daily_chronicle/main.py

from pathlib import Path
from daily_chronicle.generator import generate_events, generate_events_gemini, generate_events_openai
from daily_chronicle.slide_generation import *
from daily_chronicle.audio_generation import generate_tts_gemini, generate_tts_openai
from daily_chronicle.event_review import EventReviewWindow
from daily_chronicle.image_review import ImageReviewWindow

import json
from dotenv import load_dotenv

from PySide6.QtWidgets import QApplication

NUM_EVENTS = 3  # Number of events to generate

IMAGE_FUNCTION = generate_image_gemini
TTS_FUNCTION = generate_tts_gemini
EVENT_FUNCTION = generate_events_gemini

def main():
    
    load_dotenv()

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
    events = generate_events(month, day, NUM_EVENTS, EVENT_FUNCTION)

    if not events or not isinstance(events, list):
        print("❌ No events were generated. Exiting.")
        return

    # --- Save event JSON ---
    OUTPUT_DIR = Path(__file__).parent / "outputs"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    event_json_filepath = OUTPUT_DIR / f"{month}_{day}_events.json"
    with event_json_filepath.open("w") as f:
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
    
    TEMP_DIR = Path(__file__).parent / "temp"
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


    temp_event_assets = []
    for idx, event in enumerate(reviewed_events):
        print(f"\n🖼️ Generating assets for event {idx + 1}/{len(reviewed_events)}...")
        image_path = generate_event_image(event, idx, IMAGE_FUNCTION)
        audio_path_1, audio_path_2 = generate_event_audio(event, idx, TTS_FUNCTION)
        temp_event_assets.append({
            "event_index": idx,
            "image_path": image_path,
            "audio_path_1": audio_path_1,
            "audio_path_2": audio_path_2
        })
    
    temp_event_assets_filepath = TEMP_DIR / f"{month}_{day}_assets.json"
    temp_json_files = [str(temp_event_assets_filepath)]
    with temp_event_assets_filepath.open("w") as f:
        json.dump(temp_event_assets, f, indent=2)
    
    print(f"✅ Saved event assets to {temp_event_assets_filepath}")

    # --- Step 6: Launch Image Review ---

    print("\n🖼️ Launching IMAGE REVIEW window...")

    image_window = ImageReviewWindow(event_json_filepath, temp_event_assets_filepath)
    image_window.show()
    app.exec()
    print("✅ Image review complete.")

    # --- Step 7: Load review image/audio paths ---
    with temp_event_assets_filepath.open("r") as f:
        reviewed_assets = json.load(f)

    # Extract the first image path from the reviewed assets
    first_image_path = [
        event["image_path"]
        for event in reviewed_assets[:1]  # Get the first event
        if "image_path" in event and event["image_path"]  # Ensure the key exists and is not empty
    ]

    # --- Step 8: Generate video slides ---
    print("\n🎬 Assembling final video...")

    title_slide = generate_title_slide(month, day, TTS_FUNCTION, first_image_path)
    title_path = TEMP_DIR / "temp_video_files" / "title_slide.mp4"
    title_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    title_slide.write_videofile(str(title_path), fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    video_paths.append(str(title_path))

    for asset in reviewed_assets:
        idx = asset["event_index"]
        event = reviewed_events[idx]
        print(f"\n🎥 Building video slide for event {idx + 1}...")

        audio_paths = (asset["audio_path_1"], asset["audio_path_2"])
        image_path = asset["image_path"]

        event_video_path = build_event_segment(event, idx, audio_paths, image_path)
        video_paths.append(event_video_path)

    # --- Step 9: Export final video ---
    print("\n🚀 Exporting final video...")
    try:
        final_vid_path = export_final_video_ffmpeg(video_paths, month, day)
        print(f"\n🎉 Done! Video exported to: {str(final_vid_path)}")
    finally:
        print("\n🧹 Cleaning up temporary files...")
        cleanup_temp_files(temp_audio_files, temp_image_files, video_paths, temp_json_files)
        print("✅ Temporary files cleaned up.")
        print("\n🎬 Daily Chronicle completed successfully!")

if __name__ == "__main__":
    main()
