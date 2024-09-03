import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import requests
from PIL import Image, ImageTk
import os
from io import BytesIO
import uuid
import json
import threading
from AI.aiFunctions import getPictureURL
from AI.stableFunctions import getPathToImage

class ImageReviewWindow:
    def __init__(self, root, json_data, title):
        self.video_title = title
        self.root = root
        self.json_data = json_data
        self.current_index = 0  # To keep track of the current image

        # Define the canvas size to maintain a 16:9 aspect ratio
        self.canvas_width = 1280
        self.canvas_height = 720

        # Create main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas to display images
        self.canvas = tk.Canvas(self.main_frame, bg='gray', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Toolbar frame
        self.toolbar_frame = tk.Frame(self.main_frame)
        self.toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Prompt entry
        self.prompt_text = tk.Text(self.toolbar_frame, height=4, width=80)
        self.prompt_text.pack(side=tk.LEFT, padx=10, pady=10)

        # Navigation buttons
        self.prev_button = tk.Button(self.toolbar_frame, text="Previous", state="disabled", command=self.show_prev_image)
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.next_button = tk.Button(self.toolbar_frame, text="Next", command=self.show_next_image)
        self.next_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Buttons for regenerating and replacing images
        self.regenerate_button = tk.Button(self.toolbar_frame, text="Regenerate Image", command=self.regenerate_image)
        self.regenerate_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.replace_button = tk.Button(self.toolbar_frame, text="Replace Image", command=self.ask_image_source)
        self.replace_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Button for saving the json
        self.save_button = tk.Button(self.toolbar_frame, text="Save", command=self.save)
        self.save_button.pack(side=tk.LEFT, padx=10, pady=10)
        self.show_image(self.current_index)


    def update_image_url(self, index, prompt):
        # Placeholder for the actual implementation of getURL
        image_url = self.getURL(prompt, (index + 1))
        self.json_data[index]["image_path"] = image_url

    def getURL(self, prompt, index):
        # Simulate a function that gets an image URL based on a prompt
        # Replace with the actual implementation of your function
        return getPathToImage(self.video_title, prompt, index, "1:1")

    def show_image(self, index):
        image_path = self.json_data[index]["image_path"]
        prompt = self.json_data[index]["prompt"]

        # Load and display the image
        if image_path.startswith('http://') or image_path.startswith('https://'):
            response = requests.get(image_path)
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
        else:
            image = Image.open(image_path)

        image = self.resize_image_to_canvas(image)
        self.image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        
        # Display the prompt in the entry widget
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", prompt)

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
        self.current_index -= 1
        self.next_button["state"] = "normal"
        if self.current_index == 0:
            self.prev_button["state"] = "disabled"
        self.show_image(self.current_index)

    def show_next_image(self):
        self.current_index += 1
        self.prev_button["state"] = "normal"
        if self.current_index == len(self.json_data) - 1:
            self.next_button["state"] = "disabled"
        self.show_image(self.current_index)

    def regenerate_image(self):
        # Placeholder for regenerate image functionality
        new_prompt = self.prompt_text.get("1.0", tk.END).strip()
        self.json_data[self.current_index]["prompt"] = new_prompt
        self.json_data[self.current_index]["image_path"] = self.getURL(new_prompt, self.current_index)
        self.show_image(self.current_index)

    def save(self):
        with open(f"output/{self.video_title}/{self.video_title}.json", "w") as file:
            json.dump(self.json_data, file, indent=4)

    def ask_image_source(self):
        # Create a custom dialog to ask the user for the image source
        self.dialog_window = tk.Toplevel(self.root)
        self.dialog_window.title("Select Image Source")
        self.dialog_window.geometry("600x150")

        label = tk.Label(self.dialog_window, text="Would you like to upload an image from your computer, or the internet?")
        label.pack(pady=10)

        button_frame = tk.Frame(self.dialog_window)
        button_frame.pack(pady=10)

        my_computer_button = tk.Button(button_frame, text="My Computer", command=lambda: self.dialog_response("computer"))
        my_computer_button.pack(side=tk.LEFT, padx=5)

        internet_button = tk.Button(button_frame, text="The Internet", command=lambda: self.dialog_response("internet"))
        internet_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancel", command=lambda: self.dialog_response("cancel"))
        cancel_button.pack(side=tk.LEFT, padx=5)

    def dialog_response(self, response):
        self.dialog_window.destroy()
        self.replace_image(response)

    def show_loading_message(self):
        self.loading_label = tk.Label(self.main_frame, text="Loading images, please wait...")
        self.loading_label.pack(side=tk.TOP, pady=10)
        
        self.spinner_label = tk.Label(self.main_frame, text="")
        self.spinner_label.pack(side=tk.TOP, pady=10)
        
        self.spinner_chars = "|/-\\"
        self.spinner_index = 0
        self.update_spinner()
    
    def update_spinner(self):
        self.spinner_label.config(text=self.spinner_chars[self.spinner_index])
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
        self.root.after(100, self.update_spinner)


    def replace_image(self, source):
        if source == "cancel":
            return

        # Define the specific directory where images will be saved
        specific_directory = os.path.join(os.getcwd(), "output", "specificvideo")
        os.makedirs(specific_directory, exist_ok=True)  # Create the directory if it doesn't exist

        if source == "computer":
            # Open file dialog to select an image from the hard drive
            file_path = filedialog.askopenfilename(
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
            if not file_path:
                return  # User cancelled the file dialog
            new_image_path = file_path
        else:
            # Ask the user to enter the URL of the image
            url = simpledialog.askstring("Input", "Enter the URL of the image:")
            if not url:
                return  # User cancelled the URL input dialog

            # Download the image from the URL
            try:
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Generate a unique filename for the image
                image_filename = f"{uuid.uuid4()}.jpg"
                new_image_path = os.path.join(specific_directory, image_filename)
                
                # Save the downloaded image locally
                with open(new_image_path, "wb") as f:
                    f.write(response.content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download the image: {e}")
                return

        # Update the image path in the JSON data
        selected_index = self.current_index
        self.json_data[selected_index]["image_path"] = new_image_path

        # Reload the image with the new image path
        self.show_image(selected_index)

        messagebox.showinfo("Info", "Image replaced.")



# Example JSON data for testing
json_data = [
    {"prompt": "A cat playing with yarn", "image_path": "resources/default_image.png"},
    {"prompt": "A cat dabbing", "image_path": "resources/default_image.png"},
    {"prompt": "A cat playing hockey", "image_path": "resources/default_image.png"},
]

if __name__ == "__main__":
    root = tk.Tk()
    ImageReviewWindow(root, json_data, "testOutput")
    root.mainloop()
