"""
Runs the quiz-generator
"""
import os
from AI.stableFunctions import getPathToImage
from quizMaker import preprocess_quiz, finish_quiz, scramble_answers
import json

class Program_Runner:
    def make_directories(self):
        directories = [
            f"output/{self.title}/audio",
            f"output/{self.title}/images",
            f"output/{self.title}/slideImages",
            f"output/{self.title}/tempVids"
            ]
        for each in directories:
            if not os.path.exists(each):
                os.makedirs(each)

    def get_images(self, specific_image = False):
        title=self.title
        with open(f"output/{title}/{title}.json", "r", encoding="utf-8") as file:
            json_data = json.load(file)
        if specific_image:
            path = getPathToImage(title, json_data[specific_image]["prompt"], specific_image, ratio = "1:1")
            return
        for i in range(0, len(json_data)):
            if not os.path.exists(f"output/{title}/images/{i}.png"):
                json_data[i]["id"] = i
                print(f"Processing image {i}/{len(json_data)-1} (This will take a bit)")
                path = getPathToImage(title, json_data[i]["prompt"], i, ratio = "1:1")
                path = f"output/{title}/images/{i}.png"
                json_data[i]["image_path"] = path
                print("Processed!")
        with open(f"output/{title}/{title}.json", "w", encoding="utf-8") as file:
            json.dump(json_data, file, indent=4, ensure_ascii=False)


    def __init__(self):
        correct = "n"
        while correct.lower() not in ["yes", 'y']:
            self.title=input("What video are you working on today?\n").lower().replace(" ", "_")
            correct = input(f"Confirming that title is {self.title}. Enter 'y' to proceed.\n")
        path = f"output/{self.title}"
        if not os.path.exists(path):
            os.mkdir(path)
        self.make_directories()
        if not os.path.exists(path+"/"+self.title+".json"):
            while not os.path.exists(path+"/"+self.title+".json"):
                input(f"{self.title}.json was not found. Drop it into the output/{self.title} directory and press enter to proceed")
        running = True
        while running:
            print("Enter 1 to generate pictures.\nEnter 2 to make the quiz.\nEnter 3 to scramble answers.\nEnter 4 to regenerate a specific image.\nEnter q to quit")
            choice = input("What would you like to do?\n")
            if choice == "1":
                print("Generating all missing images. Please do not edit the JSON until all images are generated\n")
                self.get_images()
                print("All images have been (re)generated. If any aren't to your liking, delete them and generate again.")
            if choice == "2":
                print("Making the video! This may take a while.")
                clips = preprocess_quiz(self.title)
                finish_quiz(self.title, clips)
                running = False
            if choice == "3":
                scramble_answers(self.title)
            if choice == "4":
                choice = input("Which image would you like to regenerate?\n")
                if choice.isnumeric():
                    self.get_images(int(choice))
            if choice == "q":
                running=False



if __name__ == "__main__":
    runner = Program_Runner()