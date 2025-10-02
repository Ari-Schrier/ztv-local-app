import wikipediaapi
import wikipediaAiFunctions
from metadata_fetcher import get_pd_cc0_images
from download_wikipedia_images import download_all_images
from imgCropper import process_images
import slide
import subprocess
import os
import json
import time

FILEPATH = f"app/wikipedia/output"

def processPics(day):
    initialJsonLocation = f"{FILEPATH}/{day}/selections.json"
    with open(initialJsonLocation, encoding="utf-8") as file:
        data = json.load(file)
    for entry in data:
        imgPath = f"{FILEPATH}/{day}/{entry['page'].replace(' ', '_')}/processedImages"
        if len(os.listdir(imgPath)) == 0:
            process_images(f"{FILEPATH}/{day}/{entry['page'].replace(' ', '_')}/rawImages", imgPath)
            if len(os.listdir(imgPath)) == 0:
                print(entry["prompt"])
                wikipediaAiFunctions.generatePicture(entry["prompt"], imgPath +"/generatedImage.png")

def processConcept(day, struct):
    fileStart = f"{FILEPATH}/{day}/{struct['page'].replace(' ', '_')}"

    rawImageLocation = f"{fileStart}/rawImages"
    directory = os.path.dirname(rawImageLocation)
    os.makedirs(directory, exist_ok=True)

    processedImageLocation = f"{fileStart}/processedImages"
    directory = os.path.dirname(processedImageLocation)
    os.makedirs(directory, exist_ok=True)

    legalImages = get_pd_cc0_images(struct["page"])
    download_all_images(fileStart+"/rawImages", legalImages)
    with open(f"{fileStart}/images.json", 'w') as filePath:
        json.dump(legalImages, filePath, indent=4)

    process_images(rawImageLocation, processedImageLocation)


def wikiWalk(day):
    initialJsonLocation = f"{FILEPATH}/{day}/selections.json"
    directory = os.path.dirname(initialJsonLocation)
    os.makedirs(directory, exist_ok=True)

    if not os.path.exists(initialJsonLocation):

        command = wikipediaAiFunctions.getRelevantDataForDate(day.replace("_", " "))

        wikipediaAiFunctions.saveJSON(initialJsonLocation, command)

    with open(initialJsonLocation, encoding="utf-8") as file:
        data = json.load(file)
    for each in data:
        processConcept(day, each)

def finishWalk(day):
    if os.path.exists(f"output/todayInHistory/{day}.mp4"):
        return
    initialJsonLocation = f"{FILEPATH}/{day}/selections.json"
    with open(initialJsonLocation, encoding="utf-8") as file:
        data = json.load(file)
    num = int(day.split("_")[1])
    voices = [
    "alloy",
    "ash",
    "coral",
    "sage"
    ]
    voice = voices[num%4]
    for i, script in enumerate(data):
        fileStart = f"{FILEPATH}/{day}/{script['page'].replace(' ', '_')}"
        if i == 0:
            slide.makeSlidesForFolder(fileStart, script, day.replace("_", " "))
        elif i == len(data)-1:
            slide.makeSlidesForFolder(fileStart, script, "thank you")
        else:
            slide.makeSlidesForFolder(fileStart, script, "")
        
        script["description"] = script["description"] + "\n\n" + script["detail"]
            
        for each in ["header_title", "description"]:
            if not os.path.exists(f"{fileStart}/{each}.mp3"):

                wikipediaAiFunctions.getSpeech(f"{fileStart}/{each}.mp3", script[each], voice)

                command = f'ffmpeg -f lavfi -t 2.5 -i anullsrc=r=48000:cl=stereo -i {fileStart}/{each}.mp3 -f lavfi -t 1.5 -i anullsrc=r=48000:cl=stereo -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1[a]" -map "[a]" -c:a aac -b:a 192k {fileStart}/{each}.m4a'

                subprocess.run(command, shell=True, check=True)
            if not os.path.exists(f"{fileStart}/{each}.mp4"):

                command = f"ffmpeg -loop 1 -i {fileStart}/{each}.png -i {fileStart}/{each}.m4a -r 30 -c:v libx264 -tune stillimage -pix_fmt yuv420p -crf 18 -preset veryfast -c:a aac -b:a 192k -shortest {fileStart}/{each}.mp4"

                subprocess.run(command, shell=True, check=True)

        videos = [f"{fileStart}/{each}.mp4" for each in ["header_title", "description"]]
        for each in videos: print(each)
        video_titles = " ".join(videos)
        print(video_titles)
        video_titles += " resources/blackspace.mp4"

        command = f"ffmpeg-concat -t fade -d {1.5*1000} -o {fileStart}/{script['page'].replace(' ','_')}.mp4 {video_titles}"
        print(f"Making subFinal with command:\n{command}\n")
        if not os.path.exists(f"{fileStart}/{script['page'].replace(' ','_')}.mp4"):
            subprocess.run(command, shell=True, check=True)

    
    firstThing = data[0]['page'].replace(' ', '_')
    bgLocation = f"{FILEPATH}/{day}/{firstThing}"
    command = f"ffmpeg -loop 1 -i {bgLocation}/bg.png -i resources/{voice}Intro.m4a -r 30 -c:v libx264 -tune stillimage -pix_fmt yuv420p -crf 18 -preset veryfast -c:a aac -b:a 192k -shortest {f'{FILEPATH}/{day}/title'}.mp4"
    subprocess.run(command, shell=True, check=True)
    lastThing = data[len(data)-1]['page'].replace(' ', '_')
    bgLocation = f"{FILEPATH}/{day}/{lastThing}"
    command = f"ffmpeg -loop 1 -i {bgLocation}/bg.png -i resources/{voice}Outro.m4a -r 30 -c:v libx264 -tune stillimage -pix_fmt yuv420p -crf 18 -preset veryfast -c:a aac -b:a 192k -shortest {f'{FILEPATH}/{day}/end'}.mp4"
    subprocess.run(command, shell=True, check=True)
    videos = [f'{FILEPATH}/{day}/title.mp4']
    for each in data:
        videos.append(f"{FILEPATH}/{day}/{each['page'].replace(' ', '_')}/{each['page'].replace(' ', '_')}.mp4")
    videos.append(f'{FILEPATH}/{day}/end.mp4')
    videos.append('resources/endcredits_silent.mp4')
    video_titles = " ".join(videos)
    print("Making Finale")
    command = f"ffmpeg-concat -t fade -d {1.5*1000} -o output/todayInHistory/{day}.mp4 {video_titles}"
    subprocess.run(command, shell=True, check=True)

if __name__ == "__main__":
    print("Running!")
    for i in range(9, 15):
        finishWalk(f"november_{i}")
    print("Dekimashita!")