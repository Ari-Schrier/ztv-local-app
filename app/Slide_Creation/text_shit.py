import freetype
import uharfbuzz as hb
import numpy as np
from PIL import Image, ImageDraw

# Load a font using FreeType
def load_font(font_path, font_size):
    face = freetype.Face(font_path)
    face.set_char_size(font_size * 64)
    return face

# Shape text using Harfbuzz
def shape_text(face, text):
    hb_font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    
    # Shape the text (apply kerning, ligatures, etc.)
    hb.shape(hb_font, buf)
    
    # Extract glyph information (positions, advances, etc.)
    positions = buf.glyph_positions
    infos = buf.glyph_infos
    
    return positions, infos

# Render shaped text using Pillow
def render_text(face, positions, infos, output_image_path, font_size=24):
    # Create a blank image to draw on
    image = Image.new('RGBA', (800, 300), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)

    x, y = 50, 100  # Starting position for text

    # Loop through each glyph and render it with kerning and positioning
    for pos, info in zip(positions, infos):
        # Load the glyph
        glyph_index = info.codepoint
        face.load_glyph(glyph_index)
        glyph = face.glyph

        # Get glyph bitmap
        bitmap = glyph.bitmap
        width, rows = bitmap.width, bitmap.rows
        bitmap_data = np.array(bitmap.buffer).reshape(rows, width)
        glyph_image = Image.fromarray(np.uint8(bitmap_data * 255), mode='L')

        # Render the glyph at the correct position
        glyph_x = x + pos.x_offset / 64  # Convert from FreeType 1/64th pixels
        glyph_y = y - pos.y_offset / 64  # Adjust vertical offset
        
        # Paste the glyph into the main image
        image.paste(glyph_image, (int(glyph_x), int(glyph_y - rows)), glyph_image)
        
        # Advance the pen position (kerning applied automatically by Harfbuzz)
        x += pos.x_advance / 64
        y += pos.y_advance / 64

    # Save the final image
    image.save(output_image_path)

# Main function to load font, shape text, and render the result
def main():
    font_path = "path/to/your/font.ttf"  # Path to your TTF font
    text = "Hello, world!"  # Text to shape and render
    font_size = 24  # Font size

    # Load the font with FreeType
    face = load_font(font_path, font_size)

    # Shape the text with Harfbuzz (apply kerning, ligatures, etc.)
    positions, infos = shape_text(face, text)

    # Render the text and save it as an image
    render_text(face, positions, infos, "output_image_with_harfbuzz.png", font_size)

# Run the program
if __name__ == "__main__":
    main()
