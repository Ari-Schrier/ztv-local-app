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

    num_events = 3  # Default

    # --- Generate events ---
    print("\n🧠 Generating events...")
    events = generate_event_sequence(month, day, num_events)

    if not events or not isinstance(events, list):
        print("❌ No events were generated. Exiting.")
        return

    # --- Save JSON ---
    os.makedirs("outputs", exist_ok=True)
    json_path = f"outputs/daily_chronicle_{month}_{day}.json"
    with open(json_path, "w") as f:
        json.dump(events, f, indent=2)
    print(f"✅ Saved event JSON to {json_path}")

    # --- Build video slides ---
    print("\n🎬 Building video slides...")

    # Title slide
    title_slide = generate_title_slide(month, day, generate_audio_tts)
    video_clips.append(title_slide)

    # Event slides
    for idx, event in enumerate(events):
        print(f"\n👉 Generating event {idx + 1}/{len(events)}...")
        generate_daily_chronicle_pair(event, idx, generate_audio_tts)

    # --- Export final video ---
    print("\n🚀 Exporting final video...")
    output_path = export_final_video(video_clips, temp_audio_files, temp_image_files)
    print(f"\n🎉 Done! Video exported to: {output_path}")

if __name__ == "__main__":
    main()
