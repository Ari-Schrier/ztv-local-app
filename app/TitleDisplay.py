import tkinter as tk

class TitleDisplay(tk.Frame):
    def __init__(self, master, titles, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.titles = titles
        self.current_index = 0
        self.create_widgets()
        self.update_display()
        self.bind_keys()
        
    def create_widgets(self):
        self.config(bg="green")
        
        self.label = tk.Label(self, bg="green", fg="white", font=("Arial", 30))
        self.label.pack(expand=True, pady=20)
        
        self.prev_button = tk.Button(self, text="Prev", command=self.show_prev)
        self.prev_button.pack(side=tk.LEFT, padx=20, pady=20)
        
        self.next_button = tk.Button(self, text="Next", command=self.show_next)
        self.next_button.pack(side=tk.RIGHT, padx=20, pady=20)
        
    def update_display(self):
        self.label.config(text=self.titles[self.current_index])
        
    def show_prev(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
        
    def show_next(self):
        if self.current_index < len(self.titles) - 1:
            self.current_index += 1
            self.update_display()
    
    def bind_keys(self):
        self.focus_set()
        self.bind("<Left>", lambda event: self.show_prev())
        self.bind("<Right>", lambda event: self.show_next())
