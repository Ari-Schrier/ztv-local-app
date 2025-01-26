from moviepy.editor import VideoFileClip, AudioFileClip

# Input and output file paths
input_file = "resources/credits_2025.mov"  # Replace with your input video path
output_file = "resources/endcredits_silent.mp4"  # Replace with your desired output path
silent_audio_file = "resources/15-seconds-of-silence.mp3"  # Replace with your silent audio file path

# Open the video file
clip = VideoFileClip(input_file)

# Resize the video to 1920x1080
resized_clip = clip.resize(newsize=(1920, 1080))

# Load the silent audio file and clip it to the video duration
duration = resized_clip.duration
silent_audio = AudioFileClip(silent_audio_file).subclip(0, duration)

# Add the silent audio track to the video
silent_clip = resized_clip.set_audio(silent_audio)

# Write the result to a new file
silent_clip.write_videofile(output_file, fps=24)

# Close the clips to release resources
clip.close()
silent_clip.close()
