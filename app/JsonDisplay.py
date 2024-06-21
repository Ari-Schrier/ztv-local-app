import tkinter as tk
from PIL import Image, ImageTk

class JsonDisplay(tk.Frame):
    def __init__(self, master, json_list, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.json_list = json_list
        self.current_index = 0
        self.create_widgets()
        self.update_display()
        self.bind_keys()
        self.after(100, self.update_display)
        
    def create_widgets(self):
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
        self.caption_var = tk.StringVar(value="Title")
        
        self.title_radio = tk.Radiobutton(self, text="Title", variable=self.caption_var, value="Title", command=self.update_caption)
        self.title_radio.pack(side=tk.LEFT, padx=5)
        
        self.fun_fact_radio = tk.Radiobutton(self, text="Fun Fact", variable=self.caption_var, value="Fun Fact", command=self.update_caption)
        self.fun_fact_radio.pack(side=tk.LEFT, padx=5)
        
        self.question_radio = tk.Radiobutton(self, text="Question", variable=self.caption_var, value="Question", command=self.update_caption)
        self.question_radio.pack(side=tk.LEFT, padx=5)
        
        self.prev_button = tk.Button(self, text="Prev", command=self.show_prev)
        self.prev_button.pack(side=tk.LEFT, padx=20, pady=20)
        
        self.next_button = tk.Button(self, text="Next", command=self.show_next)
        self.next_button.pack(side=tk.RIGHT, padx=20, pady=20)
        
    def update_display(self):
        self.canvas.delete("all")
        slide = self.json_list[self.current_index]
        
        # Load the placeholder image (bee.png)
        img_path = slide["photo"]  # Assuming bee.png is in the same directory as this script
        img = Image.open(img_path)
        
        # Resize the image to fit the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width > 1 and canvas_height > 1:
            img = img.resize((canvas_width, canvas_height), Image.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(img)
        
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)
        
        self.update_caption()
        
    def update_caption(self):
        self.canvas.delete("caption")
        slide = self.json_list[self.current_index]
        caption_type = self.caption_var.get()
        if caption_type == "Title":
            caption_text = slide['title'][0]
        elif caption_type == "Fun Fact":
            caption_text = slide['funFact'][0]
        elif caption_type == "Question":
            caption_text = slide['question'][0]
        
        # Center the text at the bottom of the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Offsets for creating a black outline
        offsets = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in offsets:
            self.canvas.create_text(canvas_width / 2 + dx, canvas_height - 50 + dy, anchor=tk.S, text=caption_text, fill="black", font=("Arial", 45, "bold"), tag="caption")
        self.canvas.create_text(canvas_width / 2, canvas_height - 50, anchor=tk.S, text=caption_text, fill="white", font=("Arial", 45, "bold"), tag="caption")
        
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
