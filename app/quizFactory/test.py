import tkinter as tk
from tkinter import ttk, messagebox

class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Maker")

        # Title input
        self.title_label = tk.Label(root, text="Video Title:")
        self.title_label.grid(row=0, column=0, padx=10, pady=10)
        self.title_entry = tk.Entry(root)
        self.title_entry.grid(row=0, column=1, padx=10, pady=10)

        # Video type selection
        self.video_type_label = tk.Label(root, text="Video Type:")
        self.video_type_label.grid(row=1, column=0, padx=10, pady=10)
        self.video_type = tk.StringVar(value="slideshow")
        self.quiz_radio = tk.Radiobutton(root, text="Quiz", variable=self.video_type, value="quiz")
        self.slideshow_radio = tk.Radiobutton(root, text="Slideshow", variable=self.video_type, value="slideshow")
        self.quiz_radio.grid(row=1, column=1, padx=10, pady=10)
        self.slideshow_radio.grid(row=1, column=2, padx=10, pady=10)

        # Start button
        self.start_button = tk.Button(root, text="Start", command=self.start_process)
        self.start_button.grid(row=2, column=0, columnspan=3, pady=20)

    def start_process(self):
        title = self.title_entry.get()
        video_type = self.video_type.get()
        if not title:
            messagebox.showerror("Error", "Please enter a title.")
            return
        # Call the function to generate JSON and handle image generation
        self.handle_generation(title, video_type)

    def handle_generation(self, title, video_type):
        # Call your existing function to get JSON
        # Example: json_data = get_json_from_title(title)
        json_data = {"example": "data"}  # Placeholder for actual JSON data
        # Implement the logic to generate images and open image review window
        self.review_images(json_data)

    def review_images(self, json_data):
        # Open image review and editing window
        ImageReviewWindow(self.root, json_data)


class ImageReviewWindow:
    def __init__(self, root, json_data):
        self.top = tk.Toplevel(root)
        self.top.title("Review and Edit Images")
        self.json_data = json_data

        # Example listbox for image prompts, replace with actual implementation
        self.listbox = tk.Listbox(self.top)
        self.listbox.pack(padx=10, pady=10)

        # Example buttons for regenerating and replacing images
        self.regenerate_button = tk.Button(self.top, text="Regenerate Image", command=self.regenerate_image)
        self.regenerate_button.pack(padx=10, pady=10)
        self.replace_button = tk.Button(self.top, text="Replace Image", command=self.replace_image)
        self.replace_button.pack(padx=10, pady=10)

        self.load_images()

    def load_images(self):
        # Load images from json_data and populate the listbox
        for item in self.json_data:
            self.listbox.insert(tk.END, item)

    def regenerate_image(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select an image to regenerate.")
            return
        # Call your function to regenerate image
        # Example: regenerate_image(json_data[selected_index[0]])
        messagebox.showinfo("Info", "Image regenerated.")

    def replace_image(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "Please select an image to replace.")
            return
        # Implement logic to replace image
        messagebox.showinfo("Info", "Image replaced.")


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoApp(root)
    root.mainloop()
