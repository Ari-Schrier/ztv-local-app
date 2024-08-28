from moviepy.editor import *
from PIL import Image, ImageFilter, ImageDraw

if __name__ == "__main__":
    question = "What do robots do on their day off?"
    option_a = "They recharge by the beach."
    option_b = "They have a 'bit' of fun."
    option_c = "They go out for a 'byte' to eat."
    option_d = "They watch reruns of The Jetsons."

    image_path = "output/testOutput/testbot.png"
    video_duration = 3  # Duration of the video in seconds
    output_video_path = 'output/testOutput/firstchunk.mp4'
    video_width, video_height = 1920, 1080  # 16:9 aspect ratio dimensions
    image_border = 100

    # Load and process the image
    image = Image.open(image_path)

    # Calculate the aspect ratios
    image_ratio = image.width / image.height
    target_ratio = video_width / video_height

    # Crop and zoom the image to fill 16:9 frame
    if image_ratio > target_ratio:
        # Image is wider than 16:9, crop the width
        new_width = int(image.height * target_ratio)
        offset = (image.width - new_width) // 2
        image = image.crop((offset, 0, offset + new_width, image.height))
    else:
        # Image is taller than 16:9, crop the height
        new_height = int(image.width / target_ratio)
        offset = (image.height - new_height) // 2
        image = image.crop((0, offset, image.width, offset + new_height))

    # Resize to video dimensions
    image = image.resize((video_width, video_height), Image.LANCZOS)

    # Apply a heavy blur to the image (this will serve as the background)
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=20))

    # Apply a 20% black opacity scrim
    overlay = Image.new('RGBA', blurred_image.size, (0, 0, 0, 51))  # 51 is 20% opacity of 255
    blurred_image_with_scrim = Image.alpha_composite(blurred_image.convert('RGBA'), overlay)

    # Save the blurred background temporarily
    blurred_background_path = 'temp_blurred_background.png'
    blurred_image_with_scrim.save(blurred_background_path)

    # Load the original image again for overlay (ensure it's square for rounded edges)
    image = Image.open(image_path)
    image_size = 1080 - 2*image_border
    image = image.resize((image_size, image_size), Image.LANCZOS)

    # Create a mask for rounded corners
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, image_size, image_size], radius=50, fill=255)

    # Apply the rounded mask to the image
    image_with_rounded_corners = Image.new('RGBA', image.size)
    image_with_rounded_corners.paste(image, (0, 0), mask=mask)

    # Position the image on the right-hand side of the video frame
    final_background = Image.open(blurred_background_path)
    image_position = (video_width - image_with_rounded_corners.width - image_border, image_border)  # Adjust positioning as necessary
    final_background.paste(image_with_rounded_corners, image_position, image_with_rounded_corners)

    # Save the final composed image temporarily
    final_image_path = 'output/testOutput/background.png'
    final_background.save(final_image_path)

    clip = ImageClip(final_image_path, duration=video_duration)

    question_text = TextClip(
        question, 
        font="resources/HelveticaNeueBold.otf", 
        method="caption", 
        align="west", 
        fontsize=80, 
        color='white', 
        kerning=5, 
        size=(1920 - image_size - 2*image_border, None)
    ).set_pos((image_border, image_border)).set_duration(video_duration)

    new_line = image_border + question_text.size[1] + 30

    clips = [clip, question_text]

    answers = [option_a, option_b, option_c, option_d]

    for answer in answers:
        new_text = TextClip(
            answer, 
            font="resources/HelveticaNeueMedium.otf", 
            method="caption", 
            align="west", 
            fontsize=75, 
            color='white', 
            kerning=5, 
            size=(1920 - image_size - 2*image_border, None)
        ).set_duration(video_duration).set_pos((image_border, new_line))
        
        new_line += (new_text.size[1] + 25)
        clips.append(new_text)

    # Set the output video properties
    clip = clip.set_duration(video_duration)
    clip = clip.set_fps(24)

    clip = CompositeVideoClip(clips)

    # Write the final video to a file
    clip.write_videofile(output_video_path, codec='libx264', fps=24)

    # Cleanup temporary images
    import os
    os.remove(blurred_background_path)
    os.remove(final_image_path)