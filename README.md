# ASCII Galaxy Reel

A spiral galaxy that forms out of a gas cloud, drawn entirely in text characters,
while the code that describes it types itself out underneath. Renders a vertical
**1080×1920, 30 fps, 20-second** video ready for Instagram Reels, YouTube Shorts or TikTok.

![preview](examples/preview.png)

## What happens in the video

| Time | Galaxy | 
|------|--------|
| 0–5 s | a turbulent gas cloud settles into a disk |
| 4–10 s | two spiral arms grow, with dust lanes and young pink/blue stars |
| 10–16 s | the galaxy tilts away from the viewer (0° → 58°) while spinning |

Below it, `src/galaxy.py` types out line by line with syntax highlighting, a
highlighted current line, and live stats (`arms`, `tilt`, `letters`).

## Quick start

```bash
pip install -r requirements.txt
# ffmpeg must also be installed and on your PATH  (https://ffmpeg.org)

python src/render_galaxy_reel.py                     # -> galaxy_reel.mp4 (with sound)
python src/render_galaxy_reel.py --preview 5 14      # quick still frames
python src/render_galaxy_reel.py --label "@yourhandle"
python src/render_galaxy_reel.py --no-audio --out silent.mp4
```

A full render takes about 2–3 minutes on a laptop.

## Project layout

```
src/
  render_galaxy_reel.py   renders the video (art + code panel + overlays)
  galaxy.py               the code shown typing on screen
  soundtrack.py           ambient drone + keyboard clicks (pure numpy)
examples/
  preview.png             a sample frame
```

## How the galaxy is drawn

- **Density wave arms:** brightness follows `cos(2·(θ − ln r / tan(pitch) − Ωt))`,
  so the spiral pattern turns slower than the stars moving through it.
- **Flat rotation curve:** stars move with angular speed ∝ 1/r, so inner stars lap outer ones.
- **Dust lanes:** a darker band just inside each arm.
- **Tilt:** the disk is projected by squashing its y-axis by cos(tilt).
- **Brightness → text:** each cell picks a character from the ramp `" .'`,:;-~=+*xo%#&@"`.

## Customise

In `src/render_galaxy_reel.py`:

- `ARMS`, `PITCH`: number of spiral arms and how tightly they wind
- `TILT`: final viewing tilt
- `RAMP`: characters used from faint to bright
- `DUR`, `FPS`: length and frame rate

If you change `src/galaxy.py`, the on-screen code changes with it.

## Fonts

Uses DejaVu Sans Mono (Linux), Consolas (Windows) or Menlo (macOS). If none is
found, place `DejaVuSansMono.ttf` and `DejaVuSansMono-Oblique.ttf` next to the script.

## Note

`src/galaxy.py` is the readable on-screen version of the algorithm; it leaves out
display helpers (`sparkle`, `draw`), so it is not meant to run on its own.
The renderer is the runnable program.

## License

MIT, see [LICENSE](LICENSE).
