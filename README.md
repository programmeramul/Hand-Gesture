# HoloGallery 🖐️

A futuristic **Gesture Controlled Image Viewer** inspired by Iron Man's HUD.

Control your images using hand gestures detected from your webcam — no mouse or keyboard needed.

---

## ✨ Features

- **🖐️ Hand Gesture Controls** — Swipe, Pinch, Rotate, Open Palm
- **🎨 Neon HUD Interface** — Futuristic glassmorphism panels with neon blue accents
- **📸 Picture-in-Picture Webcam** — See yourself while browsing images
- **🔄 Smooth Transitions** — Crossfade animations between images
- **⚙️ Settings Panel** — Adjust gesture sensitivity, switch cameras, select folders
- **🖥️ Fullscreen Mode** — Immersive viewing experience
- **💾 Persistent Settings** — Saves your preferences automatically

---

## 🎮 Gestures

| Gesture | Action |
|---------|--------|
| Swipe Left | Previous Image |
| Swipe Right | Next Image |
| Pinch In/Out | Zoom |
| Two Fingers Rotate | Rotate Image |
| Open Palm | Reset View |

---

## ⌨️ Keyboard Controls

| Key | Action |
|-----|--------|
| ← → | Navigate Images |
| + / - | Zoom In / Out |
| r / R | Rotate |
| 0 | Reset View |
| s | Open Settings |
| f | Toggle Fullscreen |
| q / ESC | Quit |

---

## 🛠️ Tech Stack

- **Python** 3.12+
- **OpenCV** — Image processing & display
- **MediaPipe** — Hand tracking & landmark detection
- **NumPy** — Array operations
- **Tkinter** — Settings window
- **Pillow** — Image format support

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- A webcam
- Linux (Ubuntu/Debian recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/programmeramul/Hand-Gesture.git
cd holo-gallery

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies


pip install -r requirements.txt

# Create images folder and add your images
mkdir -p assets/images
# Copy your .jpg / .png files into assets/images/

holo-gallery/
├── main.py              # Application entry point
├── camera.py            # Webcam capture & management
├── gesture_detector.py  # Hand tracking + gesture recognition
├── image_viewer.py      # Image loading, zoom, rotation, transitions
├── hud.py               # Neon HUD overlay rendering
├── settings.py          # Tkinter settings window
├── config.py            # All configuration constants
├── requirements.txt     # Python dependencies
├── .gitignore
├── assets/
│   └── images/          # Place your images here
└── README.md
