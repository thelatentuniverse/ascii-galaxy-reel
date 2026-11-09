import numpy as np

RAMP = " .'`,:;-~=+*xo%#&@"
ARMS, PITCH = 2, np.radians(13)       # two arms, 13 degree pitch
R_DISK, R_BULGE = 0.42, 0.07
TILT = np.radians(58)                  # how far we tip the disk

def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)

def stars(n, rng):
    # every star gets a radius, an angle and a colour
    r = rng.exponential(R_DISK * 0.45, n)
    th = rng.uniform(0, 2 * np.pi, n)
    hot = rng.random(n) < 0.04        # young blue/pink stars
    return r, th, hot

def omega(r):
    # flat rotation curve: inner stars lap the outer ones
    return 1.0 / np.maximum(r, 0.03)

def arm_wave(r, th, t, amp):
    # a density wave: the pattern turns slower than the stars
    phase = ARMS * (th - np.log(r + 1e-3) / np.tan(PITCH) - 0.6 * t)
    return 1 + amp * np.cos(phase)

def bulge(x, y, glow):
    return glow * np.exp(-(x * x + y * y) / R_BULGE ** 2)

def project(r, th, t, tilt, spin):
    a = th + omega(r) * t * 0.05 + spin
    x, y = r * np.cos(a), r * np.sin(a)
    return x, y * np.cos(tilt)         # tip the disk toward us

def dust(r, th, t, amp):
    # dark lanes sit just inside each arm
    lane = ARMS * (th - np.log(r + 1e-3) / np.tan(PITCH) - 0.6 * t)
    return 1 - 0.55 * amp * smooth((np.cos(lane - 0.7) - 0.6) * 3)

def frame(t, cols, rows, aspect, rng):
    form = smooth(t / 5)               # gas cloud settles into a disk
    amp = smooth((t - 4) / 6)          # arms grow out of the disk
    tilt = TILT * smooth((t - 10) / 6)
    spin = 0.12 * t
    X, Y = grid(cols, rows, aspect)
    r = np.hypot(X, Y / max(np.cos(tilt), 0.3))
    th = np.arctan2(Y / max(np.cos(tilt), 0.3), X) - spin
    disk = np.exp(-r / (R_DISK * (2.2 - 1.2 * form)))
    light = disk * arm_wave(r, th, t, amp) * dust(r, th, t, amp)
    light += bulge(X, Y, 0.4 + 1.6 * form)
    return light

def to_text(light, heat):
    i = np.clip(light * heat * len(RAMP), 0, len(RAMP) - 1)
    return np.array(list(RAMP))[i.astype(int)]

def grid(cols, rows, aspect):
    x = np.linspace(-0.6, 0.6, cols)
    y = np.linspace(-0.6, 0.6, rows) * rows / cols * aspect
    return np.meshgrid(x, y)

def main():
    rng = np.random.default_rng(7)
    r, th, hot = stars(9000, rng)
    for t in np.arange(0, 20, 1 / 30):
        light = frame(t, 108, 62, 1.6, rng)
        x, y = project(r, th, t, TILT * smooth((t - 10) / 6), 0.12 * t)
        sparkle(light, x, y, hot)
        draw(to_text(light, heat=0.9), t)

main()
