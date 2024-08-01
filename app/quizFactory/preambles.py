jsonPreamble = """I'm building a program to present quizzes to viewers. I would like you to make a sample quiz for me. I would like your response in a JSON formatted as follows:

[
{
"question":"A multiple-choice question at about a second-grade difficulty level",
"A":"A) a potential answer",
"B":"B) a potential answer",
"C":"C) a potential answer",
"D":"D) a potential answer",
"answer":"A, B, C, or D",
"fun fact":"A short piece of trivia about the subject of the question"
"prompt":"Give a brief description which could be used with an AI image-generation model to generate a photograph illustrating the fun fact. 
The prompt should be very simple-- simply state the subject, the background, and what the subject is doing.
Do not include any words, and be very specific with the number of objects present in the photograph.
Also include mention of the type of camera used to take the photograph, and what sort of lens was used with it."
},
{REPEAT FOR ALL QUESTIONS}
]

ONLY SEND BACK THE JSON!!! This is very important. If you send back anything beyond the JSON, the system will crash.
"""
