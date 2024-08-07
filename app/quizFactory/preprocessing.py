from aiFunctions import getSpeech
def getAudioFor(title, question):
    destination = f"output/{title}/{question["id"]}_"
    for each in ["question", "fun fact"]:
        getSpeech(destination+each+".mp3", question[each])
    for each in ["A", "B", "C", "D"]:
        getSpeech(destination+each+".mp3", question[each][2:] +"?")
    answer = question["answer"]
    getSpeech(destination+"answer.mp3", f"The answer is {answer}: {question[answer][2:]}.")

if __name__ == "__main__":
    with open("output/Rabbits/Rabbits.json", "r") as file:
        whales = json.load(file)
        bad = ["3", "4"]
    for each in whales:
        getAudioFor("Rabbits", each)