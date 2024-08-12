from imageReviewWindow import ImageReviewWindow
from AI.aiFunctions import saveJSON
from AI.stableFunctions import getPathToImage
import tkinter as tk
import json

if __name__ == "__main__":
    title = input("What would you like the title of this quiz to be?\n")
    questions = input("How many questions long should this quiz be?\n")
    saveJSON(title, questions)
    with open(f"output/{title}/{title}.json", "r") as file:
        json_data = json.load(file)
    for i in range(0, len(json_data)):
        json_data[i]["id"] = i
        print(f"Processing image {i+1}/{len(json_data)} (This will take a bit)")
        path = getPathToImage(title, json_data[i]["prompt"], i)
        json_data[i]["image_path"] = path
        print("Processed!")
    root = tk.Tk()
    ImageReviewWindow(root, json_data, title, False)
    root.mainloop()
    print("HALLELUJAH")

    # from AI.aiFunctions import getSpeech
    # names = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    # names = ["alloy"]
    # for each in names:
    #     line = f"Hello, my name is {each} and I'd like to audition as a reader for Zinnia TV."
    #     getSpeech(f"output/voiceAudition/{each}.mp3", line, each)

    # from moviepy.editor import AudioFileClip, vfx

    # # Load the audio file
    # audio = AudioFileClip("output/voiceAudition/echo.mp3")
    # speeds = [1.0, 0.95, 0.9, 0.85, 0.8, 0.75]
    # for each in speeds:

    #     # Slow down the audio by a factor (e.g., 2.0 for half speed)
    #     slow_audio = audio.fx(vfx.speedx, factor=each)  # 0.5 means half speed

    #     # Save the new audio file
    #     slow_audio.write_audiofile(f"output/speeds/echo{each}.mp3")