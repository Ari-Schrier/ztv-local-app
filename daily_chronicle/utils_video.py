import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips
from datetime import datetime
from pathlib import Path
import os
import platform

def reveal_video_in_file_browser(path: str):
    if platform.system() == "Windows":
        # Use explorer and select the file
        subprocess.run(["explorer", "/select,", os.path.normpath(path)])
    elif platform.system() == "Darwin":
        # Use macOS `open` with -R to reveal the file in Finder
        subprocess.run(["open", "-R", path])
    elif platform.system() == "Linux":
        # On Linux, try xdg-open the folder (cannot highlight file in most environments)
        folder = os.path.dirname(path)
        subprocess.run(["xdg-open", folder])
    else:
        print("Unsupported OS for opening file browser.")

def export_final_video(video_clips, event_month: str, event_day: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    event_label = f"{event_month}_{event_day}"
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Add the end credits to the list of video clips
    end_credits_path = Path("resources") / "endcredits_silent.mp4"
    if end_credits_path.exists():
        end_credits_clip = VideoFileClip(str(end_credits_path))
        video_clips.append(end_credits_clip)
        print(f"🎞️ Added end credits: {end_credits_path}")
    else:
        print(f"⚠️ End credits file not found: {end_credits_path}")

    for clip in video_clips:
        print(f"Clip resolution: {clip.size}, FPS: {clip.fps}")

    output_path = output_dir / f"{event_label}_{timestamp}.mp4"

    print(f"🎞️ Concatenating {len(video_clips)} video clips...")

    final_video = concatenate_videoclips(video_clips, method="compose")
    final_video.write_videofile(str(output_path), fps=30, codec="libx264", audio_codec="aac")

    return str(output_path)

def export_final_video_ffmpeg(video_paths, event_month: str, event_day: str, logger=print) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    event_label = f"{event_month}_{event_day}"
    output_dir = Path("daily_chronicle/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    concat_txt_path = output_dir / f"{event_label}_concat_list.txt"
    output_video_path = output_dir / f"{event_label}_{timestamp}.mp4"

    # Include end credits if they exist
    end_credits_path = Path("resources") / "endcredits_silent.mp4"
    if end_credits_path.exists():
        video_paths.append(str(end_credits_path))
        logger(f"🎞️ Added end credits: {str(end_credits_path)}")
    else:
        logger("⚠️ No end credits found")

    # Create the .txt file for ffmpeg concat
    with concat_txt_path.open("w") as f:
        for path in video_paths:
            f.write(f"file '{Path(path).resolve()}'\n")

    # Run ffmpeg concat
    ffmpeg_cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt_path),
        "-c:v", "libx264",
        "-r", "24",                 # enforce consistent framerate
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_video_path)
    ]

    logger(f"🚀 Running ffmpeg to concat {len(video_paths)} files...")
    subprocess.run(ffmpeg_cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    # remove end credits from video_paths to avoid destroying the mp4
    video_paths.remove(str(end_credits_path))

    # remove the txt from the outputs folder
    if concat_txt_path.exists():
        concat_txt_path.unlink()

    return str(output_video_path)