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
    audio_map = ""
    input_flags = []
    lengths = [get_video_duration(vid) for vid in videos]
    total_length = lengths[0]

    # Add input flags for each video
    for each in videos:
        input_flags.append(f"-i {each}")

    # Process each video for crossfade and audio delay
    for i in range(len(videos) - 1):
        if i == 0:
            # First crossfade
            filter_complex += f"[0:v][1:v]xfade=transition=fade:duration={fade_duration}:offset={lengths[0] - fade_duration:.6f}[v1]; "
            total_length = total_length - fade_duration + lengths[1]
            # Delay for video 2 audio to match crossfade
            audio_map += f"[1:a]adelay={int((lengths[0] - fade_duration) * 1000)}|{int((lengths[0] - fade_duration) * 1000)}[a1]; "
        else:
            # Crossfades for subsequent videos
            filter_complex += f"[v{i}][{i+1}:v]xfade=transition=fade:duration={fade_duration}:offset={total_length - fade_duration}[v{i+1}]; "
            audio_map += f"[{i+1}:a]adelay={int((total_length - fade_duration) * 1000)}|{int((total_length - fade_duration) * 1000)}[a{i+1}]; "
            total_length = total_length - fade_duration + lengths[i + 1]
            # Delay for subsequent videos' audio


    # Add final format conversion and combine audio streams
    filter_complex = filter_complex.rstrip("; ") + f"; [v{len(videos)-1}]format=yuv420p[vout];"
    
    # Combine the audio streams (audio_map) for the final output
    audio_maps = "".join([f"[a{i}]" for i in range(1, len(videos))])
    audio_maps = f"[0:a]" + audio_maps +f"amix=inputs={len(videos)}:duration=longest:dropout_transition={fade_duration}:normalize=0[aout]"
    

    # Final FFmpeg command with video and audio mapping
    ffmpeg_command = (
        f"ffmpeg -y -hide_banner -loglevel error {' '.join(input_flags)} -filter_complex \"{filter_complex} {audio_map}{audio_maps}\" "
        f"-map \"[vout]\" -map \"[aout]\" -c:v libx264 -preset slow -crf 23 -c:a aac -b:a 192k {output}"
    )
    
    # Print or run the command
    subprocess.run(ffmpeg_command, shell=True, check=True)
    print(ffmpeg_command)

if __name__ == "__main__":
    from moviepy.editor import *
    from moviepy.audio import *
    vid0 = "C:\\temporary_delete_me\\fuckme0.mp4"
    vid1 = "C:\\temporary_delete_me\\fuckme1.mp4"
    vid2 = "C:\\temporary_delete_me\\fuckme2.mp4"

    videos = [vid0, vid1, vid2]
    
    merge_crossfade_ffmpeg(videos, "C:\\temporary_delete_me\\merge-practice-audiooh.mp4", 2)

    msg = """ffmpeg -i C:\\temporary_delete_me\\fuckme0.mp4 -i C:\\temporary_delete_me\\fuckme1.mp4 -i C:\\temporary_delete_me\\fuckme2.mp4 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=2:offset=6.02[v1]; [v1][2:v]xfade=transition=fade:duration=2:offset=12.04[v2];[v2]format=yuv420p[vout]; [1:a]adelay=6020|6020[a1]; [2:a]adelay=18060|18060[a2];[0:a][a1][a2]amix=inputs=3[aout] " -map "[vout]" -map "[aout]" -c:v libx264 -preset slow -crf 23 -c:a aac -b:a 192k C:\\temporary_delete_me\\merge-practice-audio2.mp4"""