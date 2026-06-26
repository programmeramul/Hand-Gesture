"""Tkinter settings window for HoloGallery."""

import tkinter as tk
from tkinter import filedialog, ttk
import json
import os
from config import SETTINGS_FILE, DEFAULT_SETTINGS


class AppSettings:
    """Shared settings state between Tkinter and OpenCV."""

    def __init__(self) -> None:
        self.image_folder: str = DEFAULT_SETTINGS["image_folder"]
        self.camera_index: int = DEFAULT_SETTINGS["camera_index"]
        self.swipe_threshold: int = DEFAULT_SETTINGS["swipe_threshold"]
        self.pinch_sensitivity: float = DEFAULT_SETTINGS["pinch_sensitivity"]
        self.fullscreen: bool = DEFAULT_SETTINGS["fullscreen"]
        self.reload_images: bool = False
        self.restart_camera: bool = False
        self._load()

    def _load(self) -> None:
        """Load settings from JSON file."""
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                self.image_folder = data.get("image_folder", self.image_folder)
                self.camera_index = data.get("camera_index", self.camera_index)
                self.swipe_threshold = data.get("swipe_threshold", self.swipe_threshold)
                self.pinch_sensitivity = data.get("pinch_sensitivity", self.pinch_sensitivity)
                self.fullscreen = data.get("fullscreen", self.fullscreen)
                print("[INFO] Settings loaded from file")
            except Exception as e:
                print(f"[WARNING] Could not load settings: {e}")

    def save(self) -> None:
        """Save settings to JSON file."""
        data = {
            "image_folder": self.image_folder,
            "camera_index": self.camera_index,
            "swipe_threshold": self.swipe_threshold,
            "pinch_sensitivity": self.pinch_sensitivity,
            "fullscreen": self.fullscreen,
        }
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print("[INFO] Settings saved")
        except Exception as e:
            print(f"[ERROR] Could not save settings: {e}")


class SettingsWindow:
    """Tkinter window for configuring HoloGallery."""

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        self.window: tk.Tk | None = None
        self._open = False

    def show(self) -> None:
        """Open the settings window (non-blocking)."""
        if self._open:
            return

        self._open = True
        self.window = tk.Tk()
        self.window.title("HoloGallery — Settings")
        self.window.geometry("480x420")
        self.window.configure(bg="#14141e")
        self.window.resizable(False, False)

        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#14141e")
        style.configure("TLabel", background="#14141e", foreground="#b4b4c8", font=("Segoe UI", 10))
        style.configure("TButton", background="#1e1e30", foreground="#50b4ff", font=("Segoe UI", 10))
        style.configure("TScale", background="#14141e", troughcolor="#1e1e30")
        style.configure("TCheckbutton", background="#14141e", foreground="#b4b4c8")

        # Title
        title = tk.Label(
            self.window, text="⚙ HOLO GALLERY SETTINGS",
            bg="#14141e", fg="#50b4ff", font=("Segoe UI", 14, "bold")
        )
        title.pack(pady=(20, 15))

        # ── Image Folder ─────────────────────────────────────
        folder_frame = tk.Frame(self.window, bg="#14141e")
        folder_frame.pack(fill="x", padx=30, pady=5)

        tk.Label(folder_frame, text="Image Folder", bg="#14141e", fg="#b4b4c8",
                 font=("Segoe UI", 10)).pack(anchor="w")

        folder_row = tk.Frame(folder_frame, bg="#14141e")
        folder_row.pack(fill="x", pady=(3, 0))

        self.folder_var = tk.StringVar(value=self.settings.image_folder)
        folder_entry = tk.Entry(folder_row, textvariable=self.folder_var,
                                bg="#1e1e30", fg="#ffffff", insertbackground="#ffffff",
                                relief="flat", font=("Segoe UI", 9))
        folder_entry.pack(side="left", fill="x", expand=True, ipady=3)

        browse_btn = tk.Button(folder_row, text="Browse", command=self._browse_folder,
                               bg="#1e1e30", fg="#50b4ff", relief="flat",
                               font=("Segoe UI", 9), padx=12, cursor="hand2")
        browse_btn.pack(side="left", padx=(8, 0))

        # ── Camera Index ─────────────────────────────────────
        cam_frame = tk.Frame(self.window, bg="#14141e")
        cam_frame.pack(fill="x", padx=30, pady=(15, 5))

        tk.Label(cam_frame, text="Camera Index", bg="#14141e", fg="#b4b4c8",
                 font=("Segoe UI", 10)).pack(anchor="w")

        self.cam_var = tk.IntVar(value=self.settings.camera_index)
        cam_spin = tk.Spinbox(cam_frame, from_=0, to=9, textvariable=self.cam_var,
                              bg="#1e1e30", fg="#ffffff", relief="flat",
                              font=("Segoe UI", 10), width=5, justify="center",
                              buttonbackground="#1e1e30")
        cam_spin.pack(anchor="w", pady=(3, 0))

        # ── Swipe Threshold ──────────────────────────────────
        swipe_frame = tk.Frame(self.window, bg="#14141e")
        swipe_frame.pack(fill="x", padx=30, pady=(15, 5))

        swipe_label = tk.Label(swipe_frame, text="Swipe Threshold: 80",
                               bg="#14141e", fg="#b4b4c8", font=("Segoe UI", 10))
        swipe_label.pack(anchor="w")

        self.swipe_var = tk.IntVar(value=self.settings.swipe_threshold)
        swipe_scale = tk.Scale(
            swipe_frame, from_=30, to=200, orient="horizontal",
            variable=self.swipe_var, bg="#14141e", fg="#50b4ff",
            troughcolor="#1e1e30", relief="flat", length=400,
            command=lambda v: swipe_label.config(text=f"Swipe Threshold: {int(float(v))}")
        )
        swipe_scale.pack(fill="x", pady=(0, 0))

        # ── Pinch Sensitivity ────────────────────────────────
        pinch_frame = tk.Frame(self.window, bg="#14141e")
        pinch_frame.pack(fill="x", padx=30, pady=(10, 5))

        pinch_label = tk.Label(pinch_frame, text="Pinch Sensitivity: 0.02",
                               bg="#14141e", fg="#b4b4c8", font=("Segoe UI", 10))
        pinch_label.pack(anchor="w")

        self.pinch_var = tk.DoubleVar(value=self.settings.pinch_sensitivity)
        pinch_scale = tk.Scale(
            pinch_frame, from_=0.005, to=0.1, resolution=0.005,
            orient="horizontal", variable=self.pinch_var,
            bg="#14141e", fg="#50b4ff", troughcolor="#1e1e30",
            relief="flat", length=400,
            command=lambda v: pinch_label.config(text=f"Pinch Sensitivity: {float(v):.3f}")
        )
        pinch_scale.pack(fill="x", pady=(0, 0))

        # ── Fullscreen ───────────────────────────────────────
        self.fullscreen_var = tk.BooleanVar(value=self.settings.fullscreen)
        fs_check = tk.Checkbutton(
            self.window, text="Fullscreen Mode", variable=self.fullscreen_var,
            bg="#14141e", fg="#b4b4c8", selectcolor="#14141e",
            font=("Segoe UI", 10), activebackground="#14141e",
            activeforeground="#50b4ff"
        )
        fs_check.pack(padx=30, pady=(15, 5), anchor="w")

        # ── Buttons ──────────────────────────────────────────
        btn_frame = tk.Frame(self.window, bg="#14141e")
        btn_frame.pack(pady=(20, 15))

        save_btn = tk.Button(btn_frame, text="💾 Save & Apply", command=self._save,
                             bg="#50b4ff", fg="#14141e", relief="flat",
                             font=("Segoe UI", 11, "bold"), padx=25, pady=6,
                             cursor="hand2")
        save_btn.pack(side="left", padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self._close,
                              bg="#1e1e30", fg="#b4b4c8", relief="flat",
                              font=("Segoe UI", 11), padx=25, pady=6,
                              cursor="hand2")
        close_btn.pack(side="left", padx=5)

        # Handle window close button
        self.window.protocol("WM_DELETE_WINDOW", self._close)

        # Center on screen
        self.window.update_idletasks()
        sw = self.window.winfo_screenwidth()
        sh = self.window.winfo_screenheight()
        ww = self.window.winfo_width()
        wh = self.window.winfo_height()
        x = (sw - ww) // 2
        y = (sh - wh) // 2
        self.window.geometry(f"+{x}+{y}")

        self.window.mainloop()

    def _browse_folder(self) -> None:
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(title="Select Image Folder")
        if folder:
            self.folder_var.set(folder)

    def _save(self) -> None:
        """Save settings and signal main loop."""
        old_folder = self.settings.image_folder
        old_camera = self.settings.camera_index

        self.settings.image_folder = self.folder_var.get()
        self.settings.camera_index = self.cam_var.get()
        self.settings.swipe_threshold = self.swipe_var.get()
        self.settings.pinch_sensitivity = self.pinch_var.get()
        self.settings.fullscreen = self.fullscreen_var.get()

        if self.settings.image_folder != old_folder:
            self.settings.reload_images = True
        if self.settings.camera_index != old_camera:
            self.settings.restart_camera = True

        self.settings.save()
        print("[INFO] Settings applied")

    def _close(self) -> None:
        """Close the window."""
        self._open = False
        if self.window:
            self.window.destroy()
            self.window = None
