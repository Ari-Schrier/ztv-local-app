import tkinter as tk
from PIL import Image, ImageTk
import requests
from io import BytesIO

class JsonDisplay(tk.Frame):
    def __init__(self, master, json_list, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.json_list = json_list
        self.current_index = 0
        self.create_widgets()
        self.update_display()
        self.bind_keys()
        
    def create_widgets(self):
        self.title_label = tk.Label(self, font=("Arial", 20))
        self.title_label.pack(pady=10)
        
        self.image_label = tk.Label(self)
        self.image_label.pack(pady=10)
        
        self.caption_label = tk.Label(self, font=("Arial", 16))
        self.caption_label.pack(pady=10)
        
        self.caption_var = tk.StringVar(value="Title")
        self.radio_frame = tk.Frame(self)
        self.radio_frame.pack(pady=10)
        
        self.title_radio = tk.Radiobutton(self.radio_frame, text="Title", variable=self.caption_var, value="Title", command=self.update_caption)
        self.title_radio.pack(side=tk.LEFT, padx=5)
        
        self.fun_fact_radio = tk.Radiobutton(self.radio_frame, text="Fun Fact", variable=self.caption_var, value="Fun Fact", command=self.update_caption)
        self.fun_fact_radio.pack(side=tk.LEFT, padx=5)
        
        self.question_radio = tk.Radiobutton(self.radio_frame, text="Question", variable=self.caption_var, value="Question", command=self.update_caption)
        self.question_radio.pack(side=tk.LEFT, padx=5)
        
        self.prev_button = tk.Button(self, text="Prev", command=self.show_prev)
        self.prev_button.pack(side=tk.LEFT, padx=20, pady=20)
        
        self.next_button = tk.Button(self, text="Next", command=self.show_next)
        self.next_button.pack(side=tk.RIGHT, padx=20, pady=20)
        
    def update_display(self):
        slide = self.json_list[self.current_index]
        self.title_label.config(text=slide['title'][0])
        self.update_caption()
        
        # Load the image from the URL
        response = requests.get(slide['img'])
        img_data = response.content
        img = Image.open(BytesIO(img_data))
        img = img.resize((500, 300), Image.ANTIALIAS)
        img_tk = ImageTk.PhotoImage(img)
        self.image_label.config(image=img_tk)
        self.image_label.image = img_tk
        
    def update_caption(self):
        slide = self.json_list[self.current_index]
        caption_type = self.caption_var.get()
        if caption_type == "Title":
            self.caption_label.config(text=slide['title'][0])
        elif caption_type == "Fun Fact":
            self.caption_label.config(text=slide['funFact'][0])
        elif caption_type == "Question":
            self.caption_label.config(text=slide['question'][0])
        
    def show_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
        
    def show_next(self):
        if self.current_index < len(self.json_list) - 1:
            self.current_index += 1
            self.update_display()
    
    def bind_keys(self):
        self.focus_set()
        self.bind("<Left>", lambda event: self.show_prev())
        self.bind("<Right>", lambda event: self.show_next())
