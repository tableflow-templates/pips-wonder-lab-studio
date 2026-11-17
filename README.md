# Pip's Wonder Lab — animation studio

Code that renders episodes of **Pip's Wonder Lab** (YouTube: @PipsWonderLabTV), an original animated science series for kids aged 4–8. Characters: Mia, Leo and the robot Pip.

Python (Pillow, numpy, scipy) + ffmpeg. No other packages needed.

| File | What it does |
|---|---|
| `art.py` | Character rig (Mia, Leo, Pip: blink, mouth, surprised), Treehouse Lab background, props, banners. Draws at 2× and downsamples. |
| `script.py` | Episode script as scenes of events: `("say", WHO, text, expr)`, `("wait", sec, tag)`, `("tag", name)`. `timeline()` gives line and tag times. |
| `render.py` | One function per scene → frames piped to ffmpeg (one mp4 per scene). Episode 1 scenes are the reference. |
| `audio.py` | Original music (Karplus-Strong ukulele) + SFX tied to tags → `out/soundtrack.wav`. |

## Render an episode

```bash
mkdir -p out stills
python3 render.py still 0 4.0 stills/a.png      # check a frame (scene index, time)
python3 render.py r 0 2 4 & python3 render.py r 1 3 5; wait
python3 audio.py
printf "file 'scene%d.mp4'\n" 1 2 3 4 5 6 > out/list.txt
cd out && ffmpeg -f concat -safe 0 -i list.txt -c copy video_only.mp4 \
  && ffmpeg -i video_only.mp4 -i soundtrack.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest episode.mp4
```

## New episode

Copy `script.py` / `render.py`, write new scenes and props reusing `art.py`. Keep characters, colors and the 6-part structure (Hook, Mystery, Experiment 1, Experiment 2, Aha!, Takeaway). Every episode needs its own story, setting and lesson.

When voice files exist (`S{scene}_{n}_{WHO}.mp3`), take line durations from them instead of `line_dur()`.
