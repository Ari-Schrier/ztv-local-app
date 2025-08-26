import os
from PIL import Image

def crop_center(img: Image.Image) -> Image.Image:
    """Crops the image to a square based on the shortest side."""
    width, height = img.size
    min_side = min(width, height)
    left = (width - min_side) / 2
    top = (height - min_side) / 2
    right = (width + min_side) / 2
    bottom = (height + min_side) / 2
    return img.crop((left, top, right, bottom))

def process_images(input_folder: str, output_folder: str):
    """Processes all images in the input folder, cropping to square and resizing to 1080x1080."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        
        input_path = os.path.join(input_folder, filename)
        base_name, _ = os.path.splitext(filename)  # Get filename without extension
        output_filename = base_name + ".png"  # Always use .png
        output_path = os.path.join(output_folder, output_filename)
        
        try:
            with Image.open(input_path) as img:
                img = crop_center(img)
                img = img.resize((1080, 1080), Image.LANCZOS)
                img.save(output_path, format="PNG")
                print(f"Processed: {filename} -> {output_filename}")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    input_folder = "input_images"  # Change to your actual input folder
    output_folder = "output_images"  # Change to your actual output folder
    process_images(input_folder, output_folder)
