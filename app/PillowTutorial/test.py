from moviepy.editor import AudioFileClip

audio_path = 'output/biblequiz/q5_A.mp3'  # Replace with your actual path

try:
    audio_clip = AudioFileClip(audio_path)
    print(f"Duration: {audio_clip.duration} seconds")
except OSError as e:
    print(f"Error: {e}")
