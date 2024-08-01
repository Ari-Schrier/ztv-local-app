from moviepy.editor import *
import random
import json

data = """[
    {
      "id": "1",
      "title": "Starting Our Journey",
      "text": "We begin our adventure by entering the lush rainforest.",
      "prompt": "A photograph of a lush rainforest entrance, with tall trees and dense foliage. The sunlight filters through the leaves, creating a serene atmosphere."
    },
    {
      "id": "2",
      "title": "First Sighting",
      "text": "We see a bright red parrot flying above us.",
      "prompt": "A photograph of a bright red parrot flying through the rainforest, with a background of green leaves and trees. The parrot's vibrant feathers should be in sharp focus."
    },
    {
      "id": "3",
      "title": "Giant Ferns",
      "text": "We walk past giant ferns, towering over us.",
      "prompt": "A photograph of giant ferns in the rainforest, towering over the ground with detailed, green fronds. The ground is covered with smaller plants and fallen leaves."
    },
    {
      "id": "4",
      "title": "Colorful Flowers",
      "text": "Beautiful flowers in many colors catch our eyes.",
      "prompt": "A photograph of colorful rainforest flowers, in various shades of red, yellow, and purple. The flowers are surrounded by lush greenery, with sunlight highlighting their vibrant colors."
    },
    {
      "id": "5",
      "title": "Stream Crossing",
      "text": "We come across a clear, bubbling stream.",
      "prompt": "A photograph of a clear stream flowing through the rainforest, with rocks and moss along the banks. The water is sparkling in the sunlight, and the surrounding trees are reflected in the water."
    },
    {
      "id": "6",
      "title": "Hidden Waterfall",
      "text": "We discover a hidden waterfall, cascading into a pool.",
      "prompt": "A photograph of a hidden waterfall in the rainforest, cascading into a clear pool. The waterfall is surrounded by rocks and lush vegetation, with mist rising from the water."
    },
    {
      "id": "7",
      "title": "Playful Monkeys",
      "text": "We see playful monkeys swinging from the trees.",
      "prompt": "A photograph of two playful monkeys swinging from branches in the rainforest. The monkeys are in motion, with the background blurred to show their speed and agility."
    },
    {
      "id": "8",
      "title": "Colorful Butterflies",
      "text": "Butterflies of many colors flutter around us.",
      "prompt": "A photograph of colorful butterflies fluttering around in the rainforest, with various shades of blue, orange, and yellow. The butterflies are in sharp focus, with a background of green leaves."
    },
    {
      "id": "9",
      "title": "Ancient Tree",
      "text": "We find an ancient tree, its trunk wide and gnarled.",
      "prompt": "A photograph of an ancient tree in the rainforest, with a wide and gnarled trunk. The tree is covered in moss and vines, and its branches stretch high into the canopy."
    },
    {
      "id": "10",
      "title": "Rainforest Canopy",
      "text": "We look up and see the dense canopy above us.",
      "prompt": "A photograph of the dense rainforest canopy, with sunlight filtering through the leaves. The canopy is a mix of different shades of green, creating a natural roof above the forest."
    },
    {
      "id": "11",
      "title": "Colorful Toucans",
      "text": "A group of toucans with colorful beaks fly by.",
      "prompt": "A photograph of a group of three colorful toucans flying through the rainforest canopy, with their distinctive bright beaks in sharp focus. The background is a blur of green foliage."
    },
    {
      "id": "12",
      "title": "Rainforest Clearing",
      "text": "We find a peaceful clearing with soft grass.",
      "prompt": "A photograph of a peaceful clearing in the rainforest, with soft grass and a few scattered wildflowers. The surrounding trees create a natural border around the clearing."
    },
    {
      "id": "13",
      "title": "Exotic Fruits",
      "text": "We taste some exotic fruits from a nearby tree.",
      "prompt": "A photograph of papayas hanging from a tree in the rainforest, with vibrant colors. The fruits are ripe and ready to be picked."
    },
    {
      "id": "14",
      "title": "Hidden Cave",
      "text": "We discover a hidden cave behind some vines.",
      "prompt": "A photograph of a hidden cave entrance in the rainforest, partially covered by hanging vines. The inside of the cave is dark, contrasting with the bright green foliage outside."
    },
    {
      "id": "15",
      "title": "Rainforest River",
      "text": "A wide river flows through the rainforest.",
      "prompt": "A photograph of a wide river flowing through the rainforest, with clear water and a sandy bank. The river is surrounded by dense vegetation and tall trees."
    },
    {
      "id": "16",
      "title": "Beautiful Orchids",
      "text": "We spot beautiful orchids growing on a tree.",
      "prompt": "A photograph of beautiful orchids growing on a tree in the rainforest, with delicate petals in shades of pink and white. The orchids are in sharp focus against a blurred background of leaves."
    },
    {
      "id": "17",
      "title": "Nightfall",
      "text": "As night falls, we hear the sounds of the rainforest.",
      "prompt": "A photograph of the rainforest at night, with the sky darkening and the trees silhouetted against the sky. The scene is lit by soft moonlight, creating a calm and serene atmosphere."
    },
    {
      "id": "18",
      "title": "Glowing Fireflies",
      "text": "We see fireflies glowing in the dark.",
      "prompt": "A photograph of fireflies glowing in the dark rainforest, with tiny lights dotting the scene. The background is dark, highlighting the soft glow of the fireflies."
    },
    {
      "id": "19",
      "title": "Owl's Hoot",
      "text": "We hear an owl hooting from a tree.",
      "prompt": "A photograph of a spectacled owl perched on a tree branch in the rainforest, with its large eyes and detailed feathers in sharp focus. The background is dark, with the owl lit by moonlight."
    },
    {
      "id": "20",
      "title": "Rainfall",
      "text": "It starts to rain, and we find shelter under a large leaf.",
      "prompt": "A photograph of rain falling in the rainforest, with large drops hitting the leaves and ground. A large leaf provides shelter, with water dripping off its edges."
    },
    {
      "id": "21",
      "title": "Frogs Singing",
      "text": "We hear frogs singing after the rain.",
      "prompt": "A photograph of frogs sitting on leaves and branches in the rainforest, with their bodies wet from the rain. The frogs are in sharp focus, and the background is lush and green."
    },
    {
      "id": "22",
      "title": "Twinkling Stars",
      "text": "We look up and see stars twinkling through the canopy.",
      "prompt": "A photograph of the night sky seen through the rainforest canopy, with stars twinkling brightly. The trees are silhouetted against the sky, creating a magical atmosphere."
    },
    {
      "id": "23",
      "title": "Fireplace",
      "text": "We set up a small campfire for warmth.",
      "prompt": "A photograph of a small log campfire in the rainforest, with flames flickering and casting a warm glow. The surrounding area is dark, with the fire providing light and warmth."
    },
    {
      "id": "24",
      "title": "Rainforest at Dawn",
      "text": "The sun rises, bringing light back to the forest.",
      "prompt": "A photograph of the rainforest at dawn, with the first light of the sun illuminating the trees and foliage. The sky is painted with soft colors of pink and orange."
    },
    {
      "id": "25",
      "title": "Morning Mist",
      "text": "Morning mist hangs over the forest.",
      "prompt": "A photograph of morning mist hanging over the rainforest, with the trees and plants partially obscured by the mist. The scene is calm and ethereal, with soft light filtering through."
    },
    {
      "id": "26",
      "title": "Hummingbirds",
      "text": "Hummingbirds flit from flower to flower.",
      "prompt": "A photograph of hummingbirds flitting from flower to flower in the rainforest, with their wings a blur of motion. The flowers are colorful and vibrant against the green background."
    },
    {
      "id": "27",
      "title": "Path",
      "text": "We follow a winding path through the trees.",
      "prompt": "A photograph of a path winding through the trees in the rainforest. The path is surrounded by tall trees and lush vegetation."
    },
    {
      "id": "28",
      "title": "Friendly Animals",
      "text": "We encounter friendly animals on our way back.",
      "prompt": "A photograph of friendly capybara peacefully grazing or resting. The background is a mix of green plants and trees."
    },
    {
      "id": "29",
      "title": "Returning Home",
      "text": "We make our way back to the edge of the forest.",
      "prompt": "A photograph of the edge of the rainforest, with the dense trees giving way to a more open area. The path leads out of the forest, with sunlight shining brightly ahead."
    },
    {
      "id": "30",
      "title": "End of the Adventure",
      "text": "Our rainforest adventure comes to a happy end.",
      "prompt": "A photograph of a serene scene at the edge of the rainforest, with a clear view of the sky and the surrounding landscape. The journey ends on a peaceful note, with a sense of accomplishment."
    }
  ]"""
data = json.loads(data)

def combine_videos_with_transition(clips, transition_duration):
    return concatenate_videoclips([
            clip if i == 0 else clip.crossfadein(transition_duration)
            for i, clip in enumerate(clips)
        ],
        padding=-transition_duration, 
        method="compose"
    )

def ken_burns_effect(image_path, duration, zoom_start=1.0, zoom_end=1.4):
    clip = ImageClip(image_path)
    w, h = clip.size
    
    # Randomly choose a corner: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    corners = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
    chosen_corner = random.choice(corners)
    
    def get_crop_center(chosen_corner, w, h, zoom):
        if chosen_corner == 'top-left':
            return w / (2 * zoom), h / (2 * zoom)
        elif chosen_corner == 'top-right':
            return w - w / (2 * zoom), h / (2 * zoom)
        elif chosen_corner == 'bottom-left':
            return w / (2 * zoom), h - h / (2 * zoom)
        elif chosen_corner == 'bottom-right':
            return w - w / (2 * zoom), h - h / (2 * zoom)
    
    def make_frame(t):
        zoom = zoom_start + (zoom_end - zoom_start) * (t / duration)
        x_center, y_center = get_crop_center(chosen_corner, w, h, zoom)
        cropped = clip.crop(x_center=x_center, y_center=y_center, width=w/zoom, height=h/zoom)
        return cropped.resize((w, h)).get_frame(t)
    
    return VideoClip(make_frame, duration=duration)

def add_caption(clip, text, fontsize=75, font='Arial', margin=120, y_offset=50):
    
    # Create the text clip with a fixed font size and wrapping
    txt_clip = TextClip(text, fontsize=fontsize, bg_color='black', color='white', font=font, method='caption', interline=10, size=(clip.w - 2 * margin, None)).set_duration(clip.duration)
    
    # Determine the position for the text and background
    txt_clip = txt_clip.set_position(('center', 'bottom'))

    # Make the clip partially transparent
    txt_clip = txt_clip.set_opacity(.7)
    
    # Move the clip up by y_offset pixels
    final_clip = CompositeVideoClip([clip, txt_clip.set_position(('center', clip.h - txt_clip.h - y_offset))])
    
    return final_clip

clips = []

title_text = TextClip("Our Rainforest Adventure", fontsize=75, color='white', size=(2040, 1152), bg_color='black')
title_text = title_text.set_duration(5)
title_text = title_text.set_pos('center')

clips.append(title_text)

for slide in data:
    newClip = ken_burns_effect(f"output/rainforest/{slide['id']}.png", duration=21)
    newClip = add_caption(newClip, slide["text"])
    voice_over = AudioFileClip(f"output/rainforest/{slide['id']}.mp3")
    silent_audio = AudioFileClip("resources/5-seconds-of-silence.mp3")
    combined_voice_over = concatenate_audioclips([silent_audio, voice_over])


    newClip = newClip.set_audio(combined_voice_over)
    clips.append(newClip)

end_text = TextClip("Thank You For Watching!", fontsize=75, color='white', size=(2040, 1152), bg_color='black')
end_text = end_text.set_duration(5)  # 5 seconds
end_text = end_text.set_pos('center')
clips.append(end_text)
    

concat_clip = combine_videos_with_transition(clips,1)

# Load the background music
audio1 = AudioFileClip("resources/rf1.mp3")
audio2 = AudioFileClip("resources/rf2.mp3")
audio3 = AudioFileClip("resources/rf3.mp3")
audio4 = AudioFileClip("resources/rf4.mp3")
audio = concatenate_audioclips([audio1, audio2, audio3, audio4])

# Set the audio duration to match the video duration
bg_audio = audio.set_duration(concat_clip.duration)
bg_audio = bg_audio.volumex(0.3)


concat_audio = concat_clip.audio

mixed_audio = CompositeAudioClip([bg_audio, concat_audio])

# Set the audio to the concatenated video clip
concat_clip = concat_clip.set_audio(mixed_audio)

concat_clip.write_videofile("output/rainforest.mp4", fps=24)