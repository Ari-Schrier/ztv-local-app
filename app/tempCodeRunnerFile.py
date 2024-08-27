if __name__ == "__main__":
    #getPathToImage("test", "a cat wearing sunglasses", "1", "1:1")

    type = "blah"
    while (type != "SLIDESHOW" and type != "QUIZ"):
        type = input("Would you like to make a quiz, or a slideshow?\n").strip().upper()
        print(type)

    if type == "SLIDESHOW":
        title = input("What would you like  the title of this slideshow to be?\n")
        questions = input("How many slides long should this slideshow be?\n")
    else:
        title = input("What would you like the title of this quiz to be?\n")
        questions = input("How many questions long should this quiz be?\n")
    saveJSON(title, questions, type)
    with open(f"output/{title}/{title}.json", "r") as file:
        json_data = json.load(file)
    for i in range(0, len(json_data)):
        json_data[i]["id"] = i
        print(f"Processing image {i+1}/{len(json_data)} (This will take a bit)")
        path = getPathToImage(title, json_data[i]["prompt"], i)
        json_data[i]["image_path"] = path
        print("Processed!")
    root = tk.Tk()
    ImageReviewWindow(root, json_data, title)
    root.mainloop()
    if type == "QUIZ":
        partial = quizMaker.preprocess_quiz(title)
    else:
        partial = slideshowMaker.preprocess_slideshow(title)
    quizMaker.finish_quiz(title, partial)