"""
Central config for the ESP overlay.
Tweak these values to trade off speed vs. accuracy vs. visual style.
"""

# --- Capture ---
CAPTURE_FPS_TARGET = 30          # how often we try to grab + process a frame
CAPTURE_REGION = None            # None = full primary monitor. Or set {"top":0,"left":0,"width":1920,"height":1080}
DOWNSCALE_FOR_DETECTION = 0.75   # run YOLO on a smaller copy of the frame for speed; boxes get scaled back up

# --- Detection ---
YOLO_MODEL = "yolov8n.pt"        # nano model = fastest, good enough for ESP-style boxes
PERSON_CLASS_ID = 0              # COCO class id for "person"
CONFIDENCE_THRESHOLD = 0.45
DEVICE = "cpu"                   # set to "cuda" if you have an NVIDIA GPU + CUDA torch installed

# --- Pose (skeleton) ---
POSE_MODEL_COMPLEXITY = 1        # 0=fast/less accurate, 1=balanced, 2=slow/more accurate
POSE_MIN_DETECTION_CONF = 0.5
POSE_MIN_TRACKING_CONF = 0.5

# --- Tracking ---
TRACK_MAX_MISSES = 10            # frames a tracked person can go undetected before we drop them
TRACK_IOU_MATCH_THRESHOLD = 0.3  # min IOU to consider a detection the "same person" as an existing track

# --- Motion / urgency scoring ---
# Urgency is derived purely from how fast tracked keypoints are moving frame-to-frame.
# It is NOT emotion or mood inference - just a normalized speed metric.
MOTION_HISTORY_LEN = 8           # how many recent frames of motion to average over
URGENCY_LOW_THRESHOLD = 0.15     # normalized motion below this = "calm" (green)
URGENCY_HIGH_THRESHOLD = 0.55    # normalized motion above this = "high activity" (red)

# --- Overlay appearance ---
BOX_COLOR_CALM = (0, 255, 0)       # green
BOX_COLOR_MEDIUM = (0, 255, 255)   # yellow
BOX_COLOR_HIGH = (0, 0, 255)       # red
BOX_THICKNESS = 2
SKELETON_THICKNESS = 2
FONT_SCALE = 0.5
SHOW_LABELS = True                 # show "Person #N - activity: 0.42" above each box
