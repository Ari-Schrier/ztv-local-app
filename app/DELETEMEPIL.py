from moviepy.editor import *

# Load a sample audio file
audio_clip = AudioFileClip("output/testOutput/pleasework.mp3")

# Load a sample image and set the duration of the video
image_clip = ImageClip("output/manitees/slide_01.png", duration=audio_clip.duration)  # 10 seconds duration

audio_clip.preview()

# Set the audio to the image clip
audio_clip = audio_clip.set_duration(image_clip.duration)
image_clip = image_clip.set_audio(audio_clip)

# Save the final video with the attached audio
image_clip.write_videofile("output/testOutput/output_with_audio.mp4", fps=24)

