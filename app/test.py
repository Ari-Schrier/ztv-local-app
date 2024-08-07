import json
from stability.stabilityFunctions import getPathToImage
if __name__ == "__main__":
    with open("output/WhaleQuiz/WhaleQuiz.json", "r") as file:
        whales = json.load(file)
    for each in whales:
        getPathToImage("WhaleQuiz", each)