from imageReviewWindow import ImageReviewWindow
from AI.aiFunctions import saveJSON
import tkinter as tk
import json

if __name__ == "__main__":
    # saveJSON("Squirrels", "ten")
    # with open("output/Squirrels/Squirrels.json", "r") as file:
    #     json_data = json.load(file)
    # root = tk.Tk()
    # ImageReviewWindow(root, json_data, "Squirrels", True)
    # root.mainloop()

    # from AI.aiFunctions import getSpeech
    # names = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    # names = ["alloy"]
    # for each in names:
    #     line = f"Hello, my name is {each} and I'd like to audition as a reader for Zinnia TV."
    #     getSpeech(f"output/voiceAudition/{each}.mp3", line, each)

    from moviepy.editor import AudioFileClip, vfx

    # Load the audio file
    audio = AudioFileClip("output/voiceAudition/echo.mp3")
    speeds = [1.0, 0.95, 0.9, 0.85, 0.8, 0.75]
    for each in speeds:

        # Slow down the audio by a factor (e.g., 2.0 for half speed)
        slow_audio = audio.fx(vfx.speedx, factor=each)  # 0.5 means half speed

        # Save the new audio file
        slow_audio.write_audiofile(f"output/speeds/echo{each}.mp3")