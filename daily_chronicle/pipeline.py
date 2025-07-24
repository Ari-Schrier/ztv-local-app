# daily_chronicle/pipeline.py

import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from daily_chronicle.generator import generate_events
from daily_chronicle.utils_img import generate_event_image
from daily_chronicle.slide_generation import build_event_segment_ffmpeg_edited, generate_title_slide, cleanup_temp_files, video_paths, temp_json_files
from daily_chronicle.audio_generation import generate_event_audio
from daily_chronicle.utils_logging import emoji
from daily_chronicle.utils_video import export_final_video_ffmpeg

# --- STEP 1: Initialization ---
def initialize_pipeline(logger):
    logger(f"{emoji('calendar')} Welcome to the Daily Chronicle Generator!")

# --- STEP 2: Generate Events ---
def generate_and_save_events(month, day, event_func, output_dir, logger, num_events):
    logger(f"\n{emoji('brain')} Generating events...")
    events = generate_events(month, day, num_events, event_func)
    if not events or not isinstance(events, list):
        logger(f"{emoji('cross_mark')} No events were generated. Exiting.")
        return None, None
    
    '''
    # Uncomment this block to enhance image prompts
    for event in events:
        raw_prompt = event.get("image_prompt", "")
        event["image_prompt"] = enhance_image_prompt(raw_prompt, logger)
    '''
        
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
        image_path = generate_event_image(event, idx, image_func, logger)
        audio_path_1, audio_path_2 = generate_event_audio(event, idx, tts_func, logger)
        temp_event_assets.append({
            "event_index": idx,
            "image_path": str(image_path),
            "audio_path_1": str(audio_path_1),
            "audio_path_2": str(audio_path_2)
        })

    asset_path = temp_dir / f"{month}_{day}_assets.json"
    with asset_path.open("w") as f:
        json.dump(temp_event_assets, f, indent=2)

    temp_json_files.append(str(asset_path))

    logger(f"{emoji('check')} Saved event assets to {asset_path}")
    return temp_event_assets, asset_path

def generate_assets_threaded(events, image_func, tts_func, temp_dir, month, day, logger, delay_between_starts=1.5):
    logger(f"{emoji('gear')} Starting threaded asset generation...")

    # Limit concurrent image generation to avoid hitting rate limits

    temp_event_assets = [None] * len(events)  # Preallocate to preserve order
    futures = []
    future_to_index = {}

    def process_event(idx, event):
        logger(f"{emoji('frame')} Generating assets for event {idx + 1}/{len(events)}...")
        
        audio_path_1, audio_path_2, audio_path_3 = generate_event_audio(event, idx, tts_func, logger)
        image_path = generate_event_image(event, idx, image_func, logger)
        return {
            "event_index": idx,
            "image_path": str(image_path),
            "audio_path_1": str(audio_path_1),
            "audio_path_2": str(audio_path_2),
            "audio_path_3": str(audio_path_3),
        }

    with ThreadPoolExecutor(max_workers=min(6, len(events))) as executor:
        for idx, event in enumerate(events):
            future = executor.submit(process_event, idx, event)
            futures.append(future)
            future_to_index[future] = idx
            time.sleep(delay_between_starts)  # ⏱️ stagger thread launch

        for future in as_completed(futures):
            idx = future_to_index[future]
            asset = future.result()
            temp_event_assets[idx] = asset

    asset_path = temp_dir / f"{month}_{day}_assets.json"
    with asset_path.open("w") as f:
        json.dump(temp_event_assets, f, indent=2)

    temp_json_files.append(str(asset_path))
    logger(f"{emoji('check')} Saved event assets to {asset_path}")
    return temp_event_assets, asset_path

# --- STEP 5: Load Reviewed Assets ---
def load_reviewed_assets(asset_path, logger):
    logger(f"\n{emoji('inbox')} Loading reviewed assets...")
    with asset_path.open("r") as f:
        return json.load(f)

# --- STEP 6: Build Video Slides ---
def build_video_segments(month, day, reviewed_events, reviewed_assets, tts_func, temp_dir, logger):
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
        video_path = build_event_segment_ffmpeg_edited(event, idx, (asset["audio_path_1"], asset["audio_path_2"], asset["audio_path_3"]), asset["image_path"], logger)
        video_paths.append(video_path)

    return video_paths

# --- STEP 7: Export Final Video ---
def export_final_output(video_paths, month, day, logger):
    logger(f"\n{emoji('rocket')} Exporting final video...")
    final_path = export_final_video_ffmpeg(video_paths, month, day, logger)
    logger(f"\n{emoji('tada')} Done! Video exported to: {final_path}")
    return final_path

# --- STEP 8: Cleanup ---
def cleanup(logger):
    from daily_chronicle.slide_generation import temp_audio_files, temp_image_files, video_paths, temp_json_files
    logger(f"\n{emoji('broom')} Cleaning up temporary files...")
    cleanup_temp_files(temp_audio_files, temp_image_files, video_paths, temp_json_files, logger)
    logger(f"{emoji('check')} Temporary files cleaned up.")