import numpy as np

def sound(sequence):
    SAMPLE_RATE = 44100
    TONE_DURATION = 0.3
    
    FREQUENCIES = {
        0: 0,
        1: 440.0,    # A4
        2: 554.37,   # C#5
        3: 659.25    # E5
    }
    
    def create_signal(freq, duration, sr):
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        if freq == 0:
            return np.zeros_like(t)
        audio = np.sin(2 * np.pi * freq * t)
        fade_len = int(sr * 0.01)
        envelope = np.ones_like(audio)
        envelope[:fade_len] = np.linspace(0, 1, fade_len)
        envelope[-fade_len:] = np.linspace(1, 0, fade_len)
        return audio * envelope
    
    full_audio = np.concatenate([
        create_signal(FREQUENCIES[idx], TONE_DURATION, SAMPLE_RATE)
        for idx in sequence
    ])
    
    return {
        "audio": full_audio.tolist(),
        "sampleRate": SAMPLE_RATE
    }