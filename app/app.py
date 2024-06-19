import tkinter as tk
from TitleDisplay import TitleDisplay
from TitleInput  import TitleInput

def on_title_submit(titles):
    print(f"Slideshow titles submitted: {titles}")
    title_input.pack_forget()
    title_display = TitleDisplay(root, titles)
    title_display.pack(expand=True, fill=tk.BOTH)

root = tk.Tk()
root.title("ZTV Video Factory")
root.state('zoomed')
root.config(bg="white")

title_input = TitleInput(root, on_title_submit)
title_input.pack(expand=True, fill=tk.BOTH)

root.mainloop()