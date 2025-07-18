# --- Padding helper ---
import numpy as np
from moviepy.audio.AudioClip import AudioArrayClip, concatenate_audioclips


def pad_audio_with_silence(audio_clip, pre_duration=1.0, post_duration=5.0):
    fps = audio_clip.fps
    nchannels = audio_clip.nchannels

    pre_clip = AudioArrayClip(np.zeros((int(fps * pre_duration), nchannels)), fps=fps)
    post_clip = AudioArrayClip(np.zeros((int(fps * post_duration), nchannels)), fps=fps)

    return concatenate_audioclips([pre_clip, audio_clip, post_clip])