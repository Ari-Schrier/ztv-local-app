import tkinter as tk
from JsonDisplay import JsonDisplay
from TitleInput  import TitleInput
from openAI.aiFunctionsFake import getJson


def on_title_submit(title):
    print(f"Slideshow titles submitted: {title}")
    title_input.pack_forget()
    json_list = getJson(title)
    json_display = JsonDisplay(root, json_list)
    json_display.pack(expand=True, fill=tk.BOTH)

root = tk.Tk()
root.title("ZTV Video Factory")
root.state('zoomed')
root.config(bg="white")

title_input = TitleInput(root, on_title_submit)
title_input.pack(expand=True, fill=tk.BOTH)

root.mainloop()