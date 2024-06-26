from openAI.aiFunctions import getThePics 
from stability.stabilityFunctions import getPathToImage

json = getThePics("African Safari!")

for image in json:
    print(getPathToImage("African Animals", image))