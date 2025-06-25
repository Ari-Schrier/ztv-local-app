# daily_chronicle/pipeline.py

import json
from pathlib import Path
from dotenv import load_dotenv

from daily_chronicle.generator import generate_events
from daily_chronicle.utils_img import generate_event_image
from daily_chronicle.slide_generation import build_event_segment, generate_title_slide, cleanup_temp_files
from daily_chronicle.audio_generation import generate_event_audio
from daily_chronicle.utils_logging import emoji
from daily_chronicle.utils_video import export_final_video_ffmpeg

# --- STEP 1: Initialization ---
def initialize_pipeline(logger):
    load_dotenv()
    logger(f"{emoji('calendar')} Welcome to the Daily Chronicle Generator!")

# --- STEP 2: Generate Events ---
def generate_and_save_events(month, day, event_func, output_dir, logger, num_events):
    logger(f"\n{emoji('brain')} Generating events...")
    events = generate_events(month, day, num_events, event_func)
    if not events or not isinstance(events, list):
        logger(f"{emoji('cross_mark')} No events were generated. Exiting.")
        return None, None

    event_json_path = output_dir / f"{month}_{day}_events.json"
    with event_json_path.open("w") as f:
        json.dump(events, f, indent=2)
    logger(f"{emoji('check')} Saved event JSON to {event_json_path}")

    return events, event_json_path

# --- STEP 3: Load Reviewed Events ---
def load_reviewed_events(event_json_path, logger):
    logger(f"\n{emoji('inbox')} Loading reviewed events...")
    with event_json_path.open("r") as f:
        return json.load(f)

# --- STEP 4: Generate Assets ---
def generate_assets(events, image_func, tts_func, temp_dir, month, day, logger):
    temp_event_assets = []
    for idx, event in enumerate(events):
        logger(f"\n{emoji('frame')} Generating assets for event {idx + 1}/{len(events)}...")
        image_path = generate_event_image(event, idx, image_func)
        audio_path_1, audio_path_2 = generate_event_audio(event, idx, tts_func)
        temp_event_assets.append({
            "event_index": idx,
            "image_path": image_path,
            "audio_path_1": audio_path_1,
            "audio_path_2": audio_path_2
        })

    asset_path = temp_dir / f"{month}_{day}_assets.json"
    with asset_path.open("w") as f:
        json.dump(temp_event_assets, f, indent=2)

    logger(f"{emoji('check')} Saved event assets to {asset_path}")
    return temp_event_assets, asset_path

# --- STEP 5: Load Reviewed Assets ---
def load_reviewed_assets(asset_path, logger):
    logger(f"\n{emoji('inbox')} Loading reviewed assets...")
    with asset_path.open("r") as f:
        return json.load(f)

# --- STEP 6: Build Video Slides ---
def build_video_segments(month, day, reviewed_events, reviewed_assets, tts_func, temp_dir, logger):
    from daily_chronicle.slide_generation import video_paths, temp_audio_files, temp_image_files, temp_json_files
    video_paths.clear()
    temp_audio_files.clear()
    temp_image_files.clear()
    temp_json_files.clear()

    title_slide = generate_title_slide(
        month, day, tts_func,
        [asset["image_path"] for asset in reviewed_assets[:1] if "image_path" in asset]
    )
    title_path = temp_dir / "temp_video_files" / "title_slide.mp4"
    title_path.parent.mkdir(parents=True, exist_ok=True)
    title_slide.write_videofile(str(title_path), fps=24, codec="libx264", audio_codec="aac", verbose=False, logger=None)
    video_paths.append(str(title_path))

    for asset in reviewed_assets:
        idx = asset["event_index"]
        event = reviewed_events[idx]
        video_path = build_event_segment(event, idx, (asset["audio_path_1"], asset["audio_path_2"]), asset["image_path"])
        video_paths.append(video_path)

    return video_paths

# --- STEP 7: Export Final Video ---
def export_final_output(video_paths, month, day, logger):
    logger(f"\n{emoji('rocket')} Exporting final video...")
    final_path = export_final_video_ffmpeg(video_paths, month, day)
    logger(f"\n{emoji('tada')} Done! Video exported to: {final_path}")
    return final_path

# --- STEP 8: Cleanup ---
def cleanup(logger):
    from daily_chronicle.slide_generation import temp_audio_files, temp_image_files, video_paths, temp_json_files
    logger(f"\n{emoji('broom')} Cleaning up temporary files...")
    cleanup_temp_files(temp_audio_files, temp_image_files, video_paths, temp_json_files)
    logger(f"{emoji('check')} Temporary files cleaned up.")
