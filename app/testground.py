
import os

from openAI import aiFunctionsFake
from stability import stabilityFunctions
myjson = aiFunctionsFake.getJson("Test")
for element in myjson:
    print(element)
myjson= stabilityFunctions.processJson("testttFile", myjson)
for element in myjson:
    print(element)