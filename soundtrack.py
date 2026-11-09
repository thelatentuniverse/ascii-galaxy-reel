"""Ambient drone + keyboard clicks for the galaxy reel (pure numpy, no audio files needed)."""
import numpy as np, wave

def make_soundtrack(path, dur=20.0, typing_until=18.5, sr=44100, seed=3):
    n = int(sr * dur); t = np.arange(n) / sr
    rng = np.random.default_rng(seed)
    out = np.zeros(n)
    for f, a in ((55, 0.06), (82.4, 0.04), (110, 0.03), (164.8, 0.02)):
        out += a * np.sin(2 * np.pi * f * t + 1.2 * np.sin(2 * np.pi * 0.06 * t * f / 55))
    pad = sum(np.sin(2 * np.pi * f * t + 2 * np.sin(2 * np.pi * 0.1 * t + f)) for f in (220, 277.2, 329.6, 440))
    out += pad * 0.012 * np.clip(t / 6, 0, 1)
    tk = 0.0
    while tk < typing_until:                       # keyboard clicks
        s = int(tk * sr); k = np.arange(min(int(sr * 0.012), n - s))
        out[s:s + len(k)] += rng.uniform(0.05, 0.11) * np.exp(-k / (sr * 0.002)) * rng.normal(0, 1, len(k))
        tk += rng.exponential(0.065) + 0.025
    out *= np.minimum(1, np.minimum(t / 0.3, (dur - t) / 1.5))
    out /= np.abs(out).max() * 1.15
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((out * 32767).astype('<i2').tobytes())

if __name__ == '__main__':
    make_soundtrack('soundtrack.wav'); print('saved soundtrack.wav')
