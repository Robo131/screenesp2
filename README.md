# Screen ESP Overlay (person detection + skeleton + motion-based activity)

Draws a live, click-through green (→yellow→red) box and pose skeleton over
any person visible on your screen — including people in a YouTube video,
a game, a video call, etc. Box/skeleton color shifts based on how fast the
person's keypoints are moving, as a rough "activity" indicator.

**What this does NOT do, on purpose:** guess anyone's age, gender, ethnicity,
or emotional state. Those all involve inferring a real personal attribute
about a real (often identifiable, non-consenting) person from a video feed,
using models that are known to be unreliable for exactly that kind of
inference. The "activity" score here is just normalized keypoint speed —
plain motion math, nothing inferred about who someone is or how they feel.

## Setup (Windows)

1. Install Python 3.10 or 3.11 (mediapipe doesn't yet support 3.12+ on all platforms).
2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. First run will auto-download `yolov8n.pt` (~6MB) from Ultralytics.

## Run

```
python main.py
```

- A transparent overlay appears over your whole primary monitor.
- It's click-through — you can still interact with whatever's underneath
  (browser, game, etc.) normally.
- Press **ESC** to quit (works globally, since the overlay can't take
  keyboard focus by design).

## Performance notes

- `config.py` → `DEVICE = "cpu"` works out of the box. If you have an
  NVIDIA GPU, install a CUDA build of PyTorch first, then set
  `DEVICE = "cuda"` for a big speed boost.
- `DOWNSCALE_FOR_DETECTION` in `config.py` trades accuracy for speed —
  lower it (e.g. 0.5) if the overlay feels laggy.
- Pose (skeleton) extraction is the most expensive part. If you only want
  boxes, you can skip the `_extract_pose` call in `detector.py` and set
  keypoints to `[]`.

## Building a standalone .exe

A `.exe` has to be built on Windows itself (PyInstaller bundles the actual
Windows runtime), so this isn't something I can produce for you directly —
but `build_exe.bat` automates it:

1. Run `python main.py` once first, so `yolov8n.pt` gets downloaded into
   the project folder.
2. Run `build_exe.bat` (from inside your activated venv).
3. Grab `dist\ScreenESP.exe` — it's a self-contained executable, no Python
   install needed to run it on that machine.

Note: because everything (YOLO weights, mediapipe, PyQt6) gets bundled in,
the exe will be a few hundred MB. That's normal for PyInstaller + ML models.

## Multi-monitor

By default it captures your primary monitor (`mss.monitors[1]`). To target
a specific monitor or region, set `CAPTURE_REGION` in `config.py`, e.g.:
```python
CAPTURE_REGION = {"top": 0, "left": 1920, "width": 1920, "height": 1080}
```

## Extending it

Ideas that stay in objective, motion/pose-based territory:
- Trail/motion blur behind fast-moving tracks
- A minimap-style radar in the corner showing all tracked people
- Alert sound when `activity_score` crosses the high threshold
- Multi-person distance-from-camera estimate using box height as a proxy
