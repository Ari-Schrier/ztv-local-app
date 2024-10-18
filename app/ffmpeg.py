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

def merge_crossfade_ffmpeg(videos, output, fade_duration):
    filter_complex = ""
    input_flags = []
    lengths =[get_video_duration(vid) for vid in videos]
    total_length = lengths[0]

    for each in videos:
        input_flags.append(f"-i {each}")
    
    for i in range(len(videos)-1):
        if i == 0:
            filter_complex += f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={lengths[0]-fade_duration}[v1]; "
            total_length = total_length - fade_duration + lengths[1]
        else:
            filter_complex += f"[v{i}][{i+1}:v]xfade=transition=fade:duration={fade_duration}:offset={total_length-fade_duration}[v{i+1}]; "
            total_length = total_length - fade_duration + lengths[i+1]
    
    filter_complex = filter_complex.rstrip("; ") + f";[v{len(videos)-1}]format=yuv420p[vout]"
    
    ffmpeg_command = f"ffmpeg {' '.join(input_flags)} -filter_complex \"{filter_complex}\" -map \"[vout]\" -c:v libx264 -preset slow -crf 23 {output}"
    #print(ffmpeg_command)
    subprocess.run(ffmpeg_command, shell=True, check=True)

if __name__ == "__main__":
    from moviepy.editor import *
    from moviepy.audio import *
    vid0 = "C:\\temporary_delete_me\\fuckme0.mp4"
    vid1 = "C:\\temporary_delete_me\\fuckme1.mp4"
    vid2 = "C:\\temporary_delete_me\\fuckme2.mp4"

    videos = [vid0, vid1, vid2]
    
    merge_crossfade_ffmpeg(videos, "C:\\temporary_delete_me\\merge-practice-audio.mp4", 2)