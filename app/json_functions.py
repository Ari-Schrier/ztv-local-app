import json
import stability.stabilityFunctions as sf
import openAI.aiFunctions as oa

def loadFile(filename):
    # Open the JSON file and load the data
    with open(filename, 'r') as file:
        data = json.load(file)

    return data

def generateAllPics(filename, subject):
    data = loadFile(filename)
    for slide in data:
        sf.getPathToImage(subject, slide)

def regenerateSpecificPics(filename, subject, targets):
    data = loadFile(filename)
    for slide in data:
        if slide["id"] in targets:
            sf.getPathToImage(subject, slide)

def getAudio(subject, type):
    filename = f"output/{subject}/{subject}.json"
    data = loadFile(filename)
    for slide in data:
        oa.getSpeech(f"output/{subject}/{slide["id"]}_{type}.mp3", slide[type])


if __name__ == "__main__":
    from video_functions import make_video
    #generateAllPics("output/ostrich/ostrich.json", "ostrich")
    #subjects = ["slide_29"]
    #regenerateSpecificPics("output/ostrich/ostrich.json", "ostrich", subjects)
    #getAudio("ostrich", "text")
    data=loadFile("output/ostrich/ostrich.json")
    make_video("Ostrich Overload", "ostrich", data, question=True)
