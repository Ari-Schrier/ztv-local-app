import tkinter as tk

class TitleInput(tk.Frame):
    def __init__(self, master, submit_callback, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.submit_callback = submit_callback
        self.create_widgets()
        
    def create_widgets(self):
        self.label = tk.Label(self, text="Enter Slideshow Title:")
        self.label.pack(pady=10)
        
        self.entry = tk.Entry(self, font=("Arial", 20))
        self.entry.pack(pady=10)
        
        self.submit_button = tk.Button(self, text="Submit", command=self.submit_title)
        self.submit_button.pack(pady=10)
        
        # Focus on the entry widget and bind the return key to submit
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda event: self.submit_title())
        
    def submit_title(self):
        title = self.entry.get()
        if title:
            self.submit_callback(title)