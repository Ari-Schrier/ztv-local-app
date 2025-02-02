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
        
        highest_width = 0
        if (len(current_line) == 0) and (width > max_width):
            print(f"PROBLEM LINE IS {word}")
            return(["PROBLEM"], width)

        if width <= max_width:
            current_line.append(word)
        else:
            # If not, finalize the current line and start a new one
            lines.append(' '.join(current_line))
            current_line = [word]
            highest_width = max(highest_width, width)
    
    # Add the last line
    lines.append(' '.join(current_line))
    return lines, highest_width

def fit_text_to_box(draw, text, max_width, max_height, font_path, initial_font_size, interline_factor):
    """Fit text within a given width and height by reducing font size if needed."""
    font_size = initial_font_size
    font = ImageFont.truetype(font_path, font_size)
    
    while True:
        # Get the wrapped lines with the current font size
        lines, highest_width = get_wrapped_text(draw, text, font, max_width)
        
        # Calculate the bounding box for multiple characters to get accurate line height
        ascent, descent = font.getmetrics()
        line_height = ascent + descent
        adjusted_line_height = line_height * interline_factor  # Adjust with interline_factor
        
        total_text_height = len(lines) * adjusted_line_height

        if total_text_height > max_height or lines == ["PROBLEM"]:
            # Reduce font size and try again
            font_size -= 2
            font = ImageFont.truetype(font_path, font_size)
        else:
            # If the total height fits, we are done
            return lines, font_size

def create_text_image(background, text, font_path, initial_font_size, interline_factor, max_width, max_height, left_margin, y_position):
    """Replicate the behavior of MoviePy's TextClip using PIL with proper line height and text wrapping."""
    # Create a blank image with a large enough size
    img = Image.open(background)  # Adjust size and background color
    draw = ImageDraw.Draw(img)
    
    # Fit the text to the box, reducing font size if needed
    lines, final_font_size = fit_text_to_box(draw, text, max_width, max_height, font_path, initial_font_size, interline_factor)
    font = ImageFont.truetype(font_path, final_font_size)
    
    # Calculate the bounding box for line height
    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    adjusted_line_height = line_height * interline_factor

    # Draw each line of text with adjusted line height
    y_pos = y_position
    for line in lines:
        draw.text((left_margin, y_pos), line, font=font, fill="white")  # Draw text line
        y_pos += adjusted_line_height  # Move to the next line with the adjusted line height

    # Save or display the image
    return img, y_pos

def make_title_page(text, background, font_path="resources/HelveticaNeueBold.otf", size=(1920, 1080)):
    bg = Image.open(background)
    draw = ImageDraw.Draw(bg)
    caption = text.lower().replace("_", " ")
    # Fit the text to the box, reducing font size if needed
    lines, final_font_size = fit_text_to_box(draw, caption, 720, 1080, font_path, 118, 1.4)
    font = ImageFont.truetype(font_path, final_font_size)
    ascent, descent = font.getmetrics()
    line_height = ascent
    adjusted_line_height = line_height * 1.4
    total_text_height = len(lines) * adjusted_line_height
    y_pos = ((size[1] -total_text_height)/2) - 48
    for line in lines:
        draw.text((120, y_pos), line, font=font, fill="white")  # Draw text line
        y_pos += adjusted_line_height  # Move to the next line with the adjusted line height
    draw.text((120, y_pos+48), "quiz", font=ImageFont.truetype("resources/HelveticaNeueThin.otf", 88), fill="white")
    watermark = Image.open("resources/logo_small.png")
    bg.paste(watermark, (70, 85), watermark)
    # Save or display the image
    filename = f'output/{text}/slideImages/title.png'
    bg.save(filename)

if __name__ == "__main__":
    make_title_page("thanksgiving_(easier)", "output/thanksgiving_(easier)/slideImages/1_background.png")

