from PIL import Image, ImageDraw, ImageFont

def get_wrapped_text(draw, text, font, max_width):
    """Wrap text based on the max width allowed."""
    lines = []
    words = text.split()  # Split the text into words
    current_line = []
    
    for word in words:
        # Test if the current line with the new word fits within the width
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)  # Get bounding box of the text
        width = bbox[2] - bbox[0]  # Calculate the width of the text

        if width <= max_width:
            current_line.append(word)
        else:
            # If not, finalize the current line and start a new one
            lines.append(' '.join(current_line))
            current_line = [word]
    
    # Add the last line
    lines.append(' '.join(current_line))
    return lines

def fit_text_to_box(draw, text, max_width, max_height, font_path, initial_font_size):
    """Fit text within a given width and height by reducing font size if needed."""
    font_size = initial_font_size
    font = ImageFont.truetype(font_path, font_size)
    
    while True:
        # Get the wrapped lines with the current font size
        lines = get_wrapped_text(draw, text, font, max_width)
        
        # Calculate total height for the wrapped lines
        line_height = font.getbbox('A')[3]  # Height of a single line of text (using getbbox)
        total_text_height = len(lines) * line_height

        if total_text_height <= max_height:
            # If the total height fits, we are done
            return lines, font_size
        else:
            # Reduce font size and try again
            font_size -= 2
            font = ImageFont.truetype(font_path, font_size)

def create_text_image(text, max_width, max_height, font_path, initial_font_size):
    """Create an image with the text fitted to the specified width and height."""
    # Create a blank image with a large enough size
    img = Image.new('RGB', (1920, 1080), color=(0, 0, 0))  # Adjust size and background color
    draw = ImageDraw.Draw(img)
    
    # Fit the text to the box, reducing font size if needed
    lines, final_font_size = fit_text_to_box(draw, text, max_width, max_height, font_path, initial_font_size)
    font = ImageFont.truetype(font_path, final_font_size)
    
    # Calculate the starting position (center the text vertically)
    total_text_height = len(lines) * font.getbbox('A')[3]
    y_start = (max_height - total_text_height) // 2 + 207  # Adjust starting Y position as needed
    
    # Draw each line of text on the image
    y_pos = y_start
    for line in lines:
        draw.text((50, y_pos), line, font=font, fill="white")  # Adjust the x position as needed
        y_pos += font.getbbox(line)[3]  # Move to the next line

    # Save or show the resulting image
    img.save("fitted_text_image.png")
    img.show()

# Example usage
text = "Your long question text that might need to be split into multiple lines goes here."
font_path = "arial.ttf"  # Path to the font file
initial_font_size = 45
max_width = 1000  # Maximum width allowed for the text block
max_height = 300  # Maximum height allowed for the text block

create_text_image(text, max_width, max_height, font_path, initial_font_size)
