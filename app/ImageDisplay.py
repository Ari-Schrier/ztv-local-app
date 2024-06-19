import tkinter as tk
from PIL import Image, ImageTk
import os

class ImageDisplay(tk.Frame):
    def __init__(self, master, img_path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.img_path = img_path
        self.create_widgets()
        
    def create_widgets(self):
        # Print the current working directory
        current_working_directory = os.getcwd()
        print("Current working directory:", current_working_directory)
        
        # Resolve the absolute path of the image
        abs_img_path = os.path.abspath(self.img_path)
        print("Absolute path of the image:", abs_img_path)
        
        # Check if the file exists
        if not os.path.exists(abs_img_path):
            print("Error: The file does not exist at:", abs_img_path)
            return
        
        # Load the image
        img = Image.open(abs_img_path)
        img = img.resize((500, 300), Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)
        
        # Create a label to display the image
        self.image_label = tk.Label(self, image=img_tk)
        self.image_label.image = img_tk  # Keep a reference to avoid garbage collection
        self.image_label.pack(pady=10)

# Integration with the main application
root = tk.Tk()
root.title("Image Display")
root.state('zoomed')
root.config(bg="white")

# Replace "bee.png" with your image file path
image_display = ImageDisplay(root, "app/bee.png")
image_display.pack(expand=True, fill=tk.BOTH)

root.mainloop()
