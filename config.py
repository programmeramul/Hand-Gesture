"""Central configuration for HoloGallery."""

# Window
WINDOW_TITLE = "HoloGallery"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Camera
CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FPS = 30

# MediaPipe Hand Detection
MAX_HANDS = 1
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.5

# Drawing
LANDMARK_COLOR = (0, 255, 255)
LANDMARK_RADIUS = 5
CONNECTION_COLOR = (0, 200, 200)
CONNECTION_THICKNESS = 2

# Image Viewer
SUPPORTED_IMAGE_FORMATS = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff")
DEFAULT_IMAGE_FOLDER = "assets/images"
IMAGE_DISPLAY_WIDTH = 640
IMAGE_DISPLAY_HEIGHT = 480

# Layout
WEBCAM_WIDTH_DISPLAY = 640
WEBCAM_HEIGHT_DISPLAY = 480
PANEL_GAP = 10

# Gesture Recognition
SWIPE_THRESHOLD = 80
SWIPE_TIME_WINDOW = 15
PINCH_SENSITIVITY = 0.01
ROTATION_SENSITIVITY = 1.5
OPEN_PALM_FINGERS = 5
ZOOM_MIN = 0.5
ZOOM_MAX = 3.0
ROTATION_MIN = -180
ROTATION_MAX = 180

# ═══════════════════════════════════════════════════════════════════
# Phase 4 — HUD / Visual Settings
# ═══════════════════════════════════════════════════════════════════

# HUD Colors (BGR)
NEON_BLUE = (255, 180, 50)
NEON_BLUE_DIM = (180, 120, 30)
NEON_CYAN = (255, 220, 80)
PANEL_BG = (25, 25, 35)
PANEL_BORDER = (200, 150, 40)
TEXT_PRIMARY = (240, 220, 180)
TEXT_SECONDARY = (160, 150, 130)

# Glassmorphism
GLASS_ALPHA = 0.25
GLASS_BLUR = 5
GLASS_BORDER_WIDTH = 2
GLASS_CORNER_RADIUS = 15

# Neon Glow
GLOW_RADIUS = 12
GLOW_ALPHA = 0.3
GLOW_COLOR = (255, 200, 60)

# PiP (Picture-in-Picture) Webcam
PIP_WIDTH = 280
PIP_HEIGHT = 200
PIP_MARGIN = 20
PIP_CORNER_RADIUS = 12

# Animations
TRANSITION_FRAMES = 15
FPS_UPDATE_INTERVAL = 10

# HUD Bar
HUD_BAR_HEIGHT = 60

# ═══════════════════════════════════════════════════════════════════
# Phase 5 — Settings
# ═══════════════════════════════════════════════════════════════════

SETTINGS_FILE = "holo_gallery_settings.json"

DEFAULT_SETTINGS = {
    "image_folder": "assets/images",
    "camera_index": 0,
    "swipe_threshold": 80,
    "pinch_sensitivity": 0.02,
    "fullscreen": False,
}
