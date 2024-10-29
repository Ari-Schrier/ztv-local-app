import subprocess
import json

def get_video_duration(video_path):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', video_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    duration = json.loads(result.stdout)['format']['duration']
    return float(duration)

# def fix_inputs(vid):
#     command = f"ffmpeg -y -i {vid} -c:v libx264 -c:a copy -vsync 1 {vid}.mp4"
#     subprocess.run(command, shell=True, check=True)

def merge_crossfade_ffmpeg(videos, output, fade_duration):
    video_titles = " ".join(videos)
    command = f"ffmpeg-concat -t fade -d {fade_duration*1000} -o {output} {video_titles}"
    # Print or run the command
    print(command)
    subprocess.run(command, shell=True, check=True)

if __name__ == "__main__":
    from moviepy.editor import *
    from moviepy.audio import *
    vid0 = "C:\\temporary_delete_me\\fuckme0.mp4"
    vid1 = "C:\\temporary_delete_me\\fuckme1.mp4"
    vid2 = "C:\\temporary_delete_me\\fuckme2.mp4"

    videos = [vid0, vid1, vid2]
    
    merge_crossfade_ffmpeg(videos, "C:\\temporary_delete_me\\merge-practice-audiooh.mp4", 2)

    msg = """ffmpeg -i C:\\temporary_delete_me\\fuckme0.mp4 -i C:\\temporary_delete_me\\fuckme1.mp4 -i C:\\temporary_delete_me\\fuckme2.mp4 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=2:offset=6.02[v1]; [v1][2:v]xfade=transition=fade:duration=2:offset=12.04[v2];[v2]format=yuv420p[vout]; [1:a]adelay=6020|6020[a1]; [2:a]adelay=18060|18060[a2];[0:a][a1][a2]amix=inputs=3[aout] " -map "[vout]" -map "[aout]" -c:v libx264 -preset slow -crf 23 -c:a aac -b:a 192k C:\\temporary_delete_me\\merge-practice-audio2.mp4"""