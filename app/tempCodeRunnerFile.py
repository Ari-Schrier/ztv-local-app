from moviepy.editor import *

vid = ImageClip("resources/title.png", duration=2)
vid.set_duration(2)
aud = AudioFileClip("resources/5-seconds-of-silence.mp3")
aud.subclip(0, vid.duration)
vid.audio = aud
vid.write_videofile("resources/blackspace.mp4", fps=24)