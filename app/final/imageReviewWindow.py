import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class ImageReviewWindow:
    def __init__(self, root, json_data):
        self.top = tk.Toplevel(root)
        self.top.title("Review and Edit Images")
        self.json_data = json_data
        self.current_index = 0  # To keep track of the current image

        # Define the canvas size to maintain a 16:9 aspect ratio
        self.canvas_width = 1280
        self.canvas_height = 720

        # Create main frame
        self.main_frame = tk.Frame(self.top)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas to display images
        self.canvas = tk.Canvas(self.main_frame, bg='gray', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Toolbar frame
        self.toolbar_frame = tk.Frame(self.main_frame)
        self.toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Prompt entry
        self.prompt_entry = tk.Entry(self.toolbar_frame, width=50)
        self.prompt_entry.pack(side=tk.LEFT, padx=10, pady=10)

        # Navigation buttons
        self.prev_button = tk.Button(self.toolbar_frame, text="Previous", command=self.show_prev_image)
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.next_button = tk.Button(self.toolbar_frame, text="Next", command=self.show_next_image)
        self.next_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Buttons for regenerating and replacing images
        self.regenerate_button = tk.Button(self.toolbar_frame, text="Regenerate Image", command=self.regenerate_image)
        self.regenerate_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.replace_button = tk.Button(self.toolbar_frame, text="Replace Image", command=self.replace_image)
        self.replace_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Load first image
        self.load_images()

    def load_images(self):
        self.show_image(self.current_index)

    def show_image(self, index):
        image_path = self.json_data[index]["image_path"]
        prompt = self.json_data[index]["prompt"]

        # Load and display the image
        image = Image.open(image_path)
        image = self.resize_image_to_canvas(image)
        self.image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        
        # Display the prompt in the entry widget
        self.prompt_entry.delete(0, tk.END)
        self.prompt_entry.insert(0, prompt)

    def resize_image_to_canvas(self, image):
        # Calculate the aspect ratio of the image
        image_aspect_ratio = image.width / image.height
        canvas_aspect_ratio = self.canvas_width / self.canvas_height

        if image_aspect_ratio > canvas_aspect_ratio:
            # Image is wider than the canvas, fit to width
            new_width = self.canvas_width
            new_height = int(self.canvas_width / image_aspect_ratio)
        else:
            # Image is taller than the canvas, fit to height
            new_width = int(self.canvas_height * image_aspect_ratio)
            new_height = self.canvas_height

        return image.resize((new_width, new_height), Image.LANCZOS)

    def show_prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image(self.current_index)
        else:
            messagebox.showinfo("Info", "This is the first image.")

    def show_next_image(self):
        if self.current_index < len(self.json_data) - 1:
            self.current_index += 1
            self.show_image(self.current_index)
        else:
            messagebox.showinfo("Info", "This is the last image.")

    def regenerate_image(self):
        # Placeholder for regenerate image functionality
        new_prompt = self.prompt_entry.get()
        self.json_data[self.current_index]["prompt"] = new_prompt
        messagebox.showinfo("Info", "Image regenerated.")

    def replace_image(self):
        # Placeholder for replace image functionality
        messagebox.showinfo("Info", "Image replaced.")


# Example JSON data for testing
json_data = [
    {"prompt": "Image 1 prompt", "image_path": "output/Adorable Kittens/1.png"},
    {"prompt": "Image 2 prompt", "image_path": "output/Adorable Kittens/2.png"},
    {"prompt": "Image 3 prompt", "image_path": "output/Adorable Kittens/3.png"},
]

if __name__ == "__main__":
    root = tk.Tk()
    ImageReviewWindow(root, json_data)
    root.mainloop()
