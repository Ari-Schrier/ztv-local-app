# --- Padding helper ---
import numpy as np
from moviepy.audio.AudioClip import AudioArrayClip, CompositeAudioClip


def pad_audio_with_silence(audio_clip, pre_duration=1.0, post_duration=5.0):
    pre_samples = int(audio_clip.fps * pre_duration)
    post_samples = int(audio_clip.fps * post_duration)
    silence_pre = np.zeros((pre_samples, audio_clip.nchannels), dtype=np.float32)
    silence_post = np.zeros((post_samples, audio_clip.nchannels), dtype=np.float32)

    pre_clip = AudioArrayClip(silence_pre, fps=audio_clip.fps)
    post_clip = AudioArrayClip(silence_post, fps=audio_clip.fps)

    full_clip = CompositeAudioClip([
        pre_clip.set_start(0),
        audio_clip.set_start(pre_duration),
        post_clip.set_start(pre_duration + audio_clip.duration)
    ])

    return full_clip.set_duration(pre_duration + audio_clip.duration + post_duration)