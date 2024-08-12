from aiFunctions import getSpeech
def getAudioFor(title, question):
    destination = f"output/{title}/{question["id"]}_"
    for each in ["question", "fun fact"]:
        getSpeech(destination+each+".mp3", question[each])
    for each in ["A", "B", "C", "D"]:
        getSpeech(destination+each+".mp3", question[each][2:] +"?")
    answer = question["answer"]
    getSpeech(destination+"answer.mp3", f"The answer is {answer}: {question[answer][2:]}.")