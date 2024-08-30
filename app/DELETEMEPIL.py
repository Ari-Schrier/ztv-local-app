from moviepy.editor import *
import os

# Function to check if file exists
def check_file_exists(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

# Function to validate the audio clip
def load_audio_clip(filepath):
    check_file_exists(filepath)
    try:
        audio_clip = AudioFileClip(filepath)
        print(f"Loaded audio: {filepath} (Duration: {audio_clip.duration} seconds)")
        return audio_clip
    except Exception as e:
        raise RuntimeError(f"Failed to load audio file: {e}")

# Function to validate the image clip
def load_image_clip(filepath, duration):
    check_file_exists(filepath)
    try:
        image_clip = ImageClip(filepath, duration=duration)
        print(f"Loaded image: {filepath} (Duration set to: {duration} seconds)")
        return image_clip
    except Exception as e:
        raise RuntimeError(f"Failed to load image file: {e}")

def main():
    try:
        # File paths (replace these with your file paths)
        audio_file_path = "output/pnw/slide_1_question.mp3"
        image_file_path = "output/pnw/slide_1.png"
        output_video_path = "output/testOutput/output_with_audio.mp4"

        # Load the audio clip
        audio_clip = load_audio_clip(audio_file_path)

        # Optional: Set FPS for the audio to ensure proper playback (standard is 44100)
        audio_clip = audio_clip.set_fps(44100)

        # Load the image clip and set its duration to match the audio duration
        image_clip = load_image_clip(image_file_path, duration=audio_clip.duration)

        # Set the audio to the image clip
        image_clip = image_clip.set_audio(audio_clip)

        # Save the final video with the attached audio
        image_clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac', fps=24)

        print(f"Video saved successfully: {output_video_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
