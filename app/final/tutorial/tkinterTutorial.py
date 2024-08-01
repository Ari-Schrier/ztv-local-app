import tkinter as tk
from PIL import Image, ImageTk

# Create the main window
root = tk.Tk()
root.title("Display Image with Pillow")

# Load an image using Pillow
image_path = "output/Adorable Kittens/1.png"
image = Image.open(image_path)

# Convert the image to a Tkinter-compatible format
image_tk = ImageTk.PhotoImage(image)

# Create a label to display the image
image_label = tk.Label(root, image=image_tk)
image_label.pack(padx=10, pady=10)

# Run the application
root.mainloop()
