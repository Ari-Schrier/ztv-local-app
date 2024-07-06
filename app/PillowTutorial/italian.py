from moviepy.editor import *
import random
import json

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

def add_caption(clip, text, max_fontsize=72, font='Arial-Bold', bg_opacity=0.6, margin=10, y_offset=50):
    # Function to dynamically resize text
    def get_resized_text_clip(text, clip_width, max_fontsize, font):
        for fontsize in range(max_fontsize, 10, -2):
            txt_clip = TextClip(text, fontsize=fontsize, color='white', font=font)
            if txt_clip.w < (clip_width - 2 * margin):
                return txt_clip.set_duration(clip.duration)
        return TextClip(text, fontsize=10, color='white', font=font).set_duration(clip.duration)
    
    # Create the text clip with dynamically adjusted font size
    txt_clip = get_resized_text_clip(text, clip.w, max_fontsize, font)
    
    # Create the background clip
    txt_bg = ColorClip(size=(txt_clip.w + 2 * margin, txt_clip.h + margin), color=(0, 0, 0)).set_duration(clip.duration)
    txt_bg = txt_bg.set_opacity(bg_opacity)
    
    # Determine the position for the text and background
    txt_clip = txt_clip.set_position(('center', 'bottom'))
    txt_bg = txt_bg.set_position(('center', 'bottom'))
    
    # Composite the text and background
    txt_composite = CompositeVideoClip([txt_bg, txt_clip])
    
    # Move the composite up by y_offset pixels
    final_clip = CompositeVideoClip([clip, txt_composite.set_position(('center', clip.h - txt_composite.h - y_offset))])
    
    return final_clip

data = """
[{"id": "1", "title": ["Classic Spaghetti", "Done"], "funFact": ["Spaghetti is one of the oldest pasta types, originating around the 12th century in Southern Italy.", "Done"], "question": ["Do you like spaghetti?", "Done"], "prompt": "A plate of classic spaghetti with tomato sauce and fresh basil, taken in natural light."}, {"id": "2", "title": ["Margherita Pizza", "Done"], "funFact": ["Margherita pizza is named after Queen Margherita of Savoy and is designed in the colors of the Italian flag.", "Done"], "question": ["Have you ever tried Margherita pizza?", "Done"], "prompt": "A top-down view of a Margherita pizza with tomatoes, mozzarella, and basil, on a wooden table."}, {"id": "3", "title": ["Lasagna", "Done"], "funFact": ["Lasagna is believed to have originated in Ancient Greece and evolved into the Italian version we know today.", "Done"], "question": ["Do you know anyone who makes a great lasagna?", "Done"], "prompt": "A slice of homemade lasagna with layers of pasta, cheese, and meat sauce, in a cozy kitchen setting."}, {"id": "4", "title": ["Risotto", "Done"], "funFact": ["Risotto is a traditional Northern Italian rice dish cooked to a creamy consistency.", "Done"], "question": ["Have you ever had risotto?", "Done"], "prompt": "A creamy risotto with mushrooms and parmesan cheese, served in a ceramic bowl."}, {"id": "5", "title": ["Gelato", "Done"], "funFact": ["Gelato is an Italian version of ice cream, known for its dense and rich texture.", "Done"], "question": ["Do you have a favorite gelato flavor?", "Done"], "prompt": "A bowl of colorful gelato scoops in different flavors, garnished with fresh fruits."}, {"id": "6", "title": ["Tiramisu", "Done"], "funFact": ["Tiramisu is a popular Italian dessert made with layers of coffee-soaked ladyfingers and mascarpone cheese.", "Done"], "question": ["Have you ever tried making tiramisu?", "Done"], "prompt": "A slice of tiramisu with a dusting of cocoa powder on top, served on a white plate."}, {"id": "7", "title": ["Fettuccine Alfredo", "Done"], "funFact": ["Fettuccine Alfredo was created by Italian restaurateur Alfredo di Lelio in the early 20th century.", "Done"], "question": ["Do you like creamy pasta dishes?", "Done"], "prompt": "A plate of fettuccine Alfredo with a creamy sauce, garnished with parsley, on a wooden table."}, {"id": "8", "title": ["Pesto", "Done"], "funFact": ["Pesto is a traditional sauce from Genoa, made with basil, pine nuts, garlic, Parmesan, and olive oil.", "Done"], "question": ["Do you enjoy the taste of basil?", "Done"], "prompt": "A jar of freshly made pesto sauce with a bunch of basil leaves and a clove of garlic nearby."}, {"id": "9", "title": ["Bruschetta", "Done"], "funFact": ["Bruschetta is an antipasto consisting of grilled bread rubbed with garlic and topped with olive oil and salt.", "Done"], "question": ["Have you ever made bruschetta at home?", "Done"], "prompt": "Bruschetta topped with diced tomatoes, basil, and mozzarella on a rustic wooden board."}, {"id": "10", "title": ["Prosciutto", "Done"], "funFact": ["Prosciutto is a dry-cured ham that is usually thinly sliced and served uncooked.", "Done"], "question": ["Do you like to have prosciutto in your sandwiches?", "Done"], "prompt": "A plate of thinly sliced prosciutto with fresh figs and a glass of red wine."}, {"id": "11", "title": ["Arancini", "Done"], "funFact": ["Arancini are stuffed rice balls that are coated with breadcrumbs and fried, most commonly found in Italy.", "Done"], "question": ["Have you ever tried arancini?", "Done"], "prompt": "A plate of golden-brown arancini with a side of marinara sauce, garnished with fresh parsley."}, {"id": "12", "title": ["Carbonara", "Done"], "funFact": ["Carbonara is a Roman pasta dish made with egg, hard cheese, pancetta, and pepper.", "Done"], "question": ["Do you enjoy pasta with bacon?", "Done"], "prompt": "A bowl of spaghetti carbonara with creamy sauce, sprinkled with grated Parmesan and black pepper."}, {"id": "13", "title": ["Cannoli", "Done"], "funFact": ["Cannoli are tube-shaped shells of fried pastry dough, filled with a sweet, creamy filling.", "Done"], "question": ["Have you ever had a cannoli?", "Done"], "prompt": "A plate of cannoli with a creamy ricotta filling, topped with powdered sugar."}, {"id": "14", "title": ["Osso Buco", "Done"], "funFact": ["Osso Buco is a Milanese specialty of cross-cut veal shanks braised with vegetables, white wine, and broth.", "Done"], "question": ["Do you like slow-cooked meals?", "Done"], "prompt": "A hearty serving of Osso Buco with gremolata, on a rustic plate with a side of risotto."}, {"id": "15", "title": ["Panna Cotta", "Done"], "funFact": ["Panna cotta is a creamy, chilled dessert, similar to a custard, but set with gelatin.", "Done"], "question": ["Do you like creamy desserts?", "Done"], "prompt": "A delicate panna cotta topped with fresh berries and a drizzle of fruit sauce."}, {"id": "16", "title": ["Minestrone", "Done"], "funFact": ["Minestrone is a thick soup of Italian origin made with vegetables, often with the addition of pasta or rice.", "Done"], "question": ["Have you ever had minestrone soup?", "Done"], "prompt": "A steaming bowl of minestrone soup with chunks of vegetables and pasta in a light tomato broth."}, {"id": "17", "title": ["Caprese Salad", "Done"], "funFact": ["Caprese salad is a simple Italian salad made of fresh tomatoes, mozzarella, basil, and olive oil.", "Done"], "question": ["Do you enjoy fresh salads?", "Done"], "prompt": "A colorful plate of caprese salad with sliced tomatoes, mozzarella, fresh basil leaves, and a drizzle of olive oil."}, {"id": "18", "title": ["Eggplant Parmesan", "Done"], "funFact": ["Eggplant Parmesan is a baked dish made with breaded eggplant slices layered with tomato sauce and cheese.", "Done"], "question": ["Have you ever tried Eggplant Parmesan?", "Done"], "prompt": "A serving of eggplant Parmesan with melted cheese on top, garnished with a sprig of basil."}, {"id": "19", "title": ["Zuppa Toscana", "Done"], "funFact": ["Zuppa Toscana is a hearty soup made with kale, potatoes, and sausage, originating from Tuscany.", "Done"], "question": ["Do you like hearty soups?", "Done"], "prompt": "A bowl of Zuppa Toscana with chunks of sausage, kale, and potatoes in a creamy broth."}, {"id": "20", "title": ["Focaccia", "Done"], "funFact": ["Focaccia is a flat oven-baked Italian bread, similar in style and texture to pizza dough.", "Done"], "question": ["Have you ever baked bread?", "Done"], "prompt": "A loaf of focaccia bread with rosemary sprigs and sea salt on a wooden cutting board."}, {"id": "21", "title": ["Gnocchi", "Done"], "funFact": ["Gnocchi are soft dough dumplings, often made from potatoes, flour, and eggs.", "Done"], "question": ["Have you ever made gnocchi from scratch?", "Done"], "prompt": "A plate of golden-brown gnocchi sautéed with butter and sage, dusted with Parmesan cheese."}, {"id": "22", "title": ["Parmigiana", "Done"], "funFact": ["Parmigiana is a dish made with layers of fried eggplant layered with cheese and tomato sauce, then baked.", "Done"], "question": ["Do you enjoy dishes with tomato sauce?", "Done"], "prompt": "A close-up of a serving of eggplant Parmigiana, with melted cheese and tomato sauce."}, {"id": "23", "title": ["Limoncello", "Done"], "funFact": ["Limoncello is a sweet lemon liqueur from Southern Italy, often served as a digestif.", "Done"], "question": ["Have you ever had Limoncello?", "Done"], "prompt": "A glass of chilled Limoncello with a lemon garnish, set on a sunny outdoor table."}, {"id": "24", "title": ["Polenta", "Done"], "funFact": ["Polenta is a dish made from boiled cornmeal and can be served as a hot porridge or solidified into a loaf.", "Done"], "question": ["Do you like corn-based dishes?", "Done"], "prompt": "A serving of creamy polenta with a topping of sautéed wild mushrooms and herbs."}, {"id": "25", "title": ["Ravioli", "Done"], "funFact": ["Ravioli are stuffed pasta pillows, traditionally filled with ricotta and spinach, or meat.", "Done"], "question": ["Do you like stuffed pasta?", "Done"], "prompt": "A plate of ravioli with spinach and ricotta filling, topped with marinara sauce and a sprinkle of Parmesan."}, {"id": "26", "title": ["Saltimbocca", "Done"], "funFact": ["Saltimbocca is a Roman dish made with veal, prosciutto, and sage, cooked in white wine and butter.", "Done"], "question": ["Do you enjoy dishes with sage?", "Done"], "prompt": "A serving of saltimbocca with a side of roasted vegetables, on a white plate."}, {"id": "27", "title": ["Panettone", "Done"], "funFact": ["Panettone is a type of sweet bread loaf originally from Milan, usually prepared and enjoyed for Christmas.", "Done"], "question": ["Have you ever tried Panettone?", "Done"], "prompt": "A slice of Panettone with visible dried fruits, served with a cup of hot chocolate."}, {"id": "28", "title": ["Grissini", "Done"], "funFact": ["Grissini are thin, crunchy breadsticks that originated in Turin, traditionally served as an appetizer.", "Done"], "question": ["Do you like crunchy snacks?", "Done"], "prompt": "A jar filled with long, thin Grissini breadsticks, set on a table with a small bowl of dipping sauce."}, {"id": "29", "title": ["Biscotti", "Done"], "funFact": ["Biscotti, also known as cantucci, are almond biscuits that are twice-baked, oblong-shaped, dry, and crunchy.", "Done"], "question": ["Do you like to dip biscotti in coffee?", "Done"], "prompt": "A plate of freshly baked biscotti with almonds, alongside a cup of coffee."}, {"id": "30", "title": ["Panzanella", "Done"], "funFact": ["Panzanella is a Tuscan bread salad made with tomatoes, soaked stale bread, onions, and basil.", "Done"], "question": ["Do you enjoy fresh vegetable salads?", "Done"], "prompt": "A colorful bowl of Panzanella salad with chunks of tomato, cucumber, and soaked bread, garnished with fresh basil."}]
"""

data = json.loads(data)

clips = []
for slide in data:
    newClip = ken_burns_effect(f"output/Italian Food!/{slide['id']}.png", duration=11)
    newClip = add_caption(newClip, slide["funFact"][0])
    clips.append(newClip)

concat_clip = combine_videos_with_transition(clips,1)

# Load the background music
audio1 = AudioFileClip("resources/italianClassic.mp3")
audio2 = AudioFileClip("resources/vivaAmore.mp3")
audio = concatenate_audioclips([audio1, audio2])

# Set the audio duration to match the video duration
audio = audio.set_duration(concat_clip.duration)

# Set the audio to the concatenated video clip
concat_clip = concat_clip.set_audio(audio)

concat_clip.write_videofile("output/italiano2.mp4", fps=24)
