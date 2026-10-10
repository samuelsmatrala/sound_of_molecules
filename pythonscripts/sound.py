import numpy as np
def scale_to_range(x, x_min = -8 , x_max = -0.005, new_min=82.41, new_max=329.63):
    if x_max == x_min:
        return new_min
    return (x - x_min) / (x_max - x_min) * (new_max - new_min) + new_min
def sound(sequence, energies):
    SAMPLE_RATE = 44100
    TONE_DURATION = 0.25
    
    FREQUENCIES = {
        0: 0,
        1: scale_to_range(energies[0]),
        2: scale_to_range(energies[1]),
        3: scale_to_range(energies[2]),
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