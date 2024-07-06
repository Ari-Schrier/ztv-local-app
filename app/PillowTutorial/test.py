import random
from moviepy.editor import ImageClip, VideoClip

def ken_burns_effect(image_path, duration, zoom_start=1.0, zoom_end=1.5):
    clip = ImageClip(image_path)
    w, h = clip.size
    
    # Randomly choose a corner: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    corners = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
    chosen_corner = random.choice(corners)
    print(f"Chosen corner: {chosen_corner}")
    
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

# Example usage:
ken_burns_clip = ken_burns_effect('output/Adorable Kittens/1.png', duration=5)
ken_burns_clip.write_videofile('ken_burns_effect.mp4', fps=24)
