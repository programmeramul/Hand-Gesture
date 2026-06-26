"""HoloGallery — Gesture Controlled Image Viewer.
Phase 5: Settings Window + Final Version.
"""

import cv2
import numpy as np
from camera import Camera
from config import (
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    HUD_BAR_HEIGHT,
)
from gesture_detector import GestureDetector
from image_viewer import ImageViewer
from hud import HUD
from settings import AppSettings, SettingsWindow


def main() -> None:
    """Initialize and run the main application loop."""
    print("=" * 50)
    print("  HoloGallery — Phase 5")
    print("  Gesture Controlled Image Viewer")
    print("=" * 50)
    print("Controls:")
    print("  Swipe Left/Right → Navigate")
    print("  Pinch           → Zoom")
    print("  Two Fingers     → Rotate")
    print("  Open Palm       → Reset")
    print("  's'             → Settings")
    print("  'f'             → Fullscreen")
    print("  'q' or ESC      → Quit\n")

    # Load settings
    app_settings = AppSettings()

    # Initialize components
    camera = Camera(camera_index=app_settings.camera_index)
    detector = GestureDetector()
    viewer = ImageViewer(folder_path=app_settings.image_folder)
    hud = HUD()

    if not camera.start():
        print("[ERROR] Failed to start camera. Exiting.")
        return

    cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_NORMAL)

    if app_settings.fullscreen:
        cv2.setWindowProperty(WINDOW_TITLE, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    else:
        cv2.resizeWindow(WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT)

    prev_pinch_dist = None
    current_gesture = ""
    settings_window: SettingsWindow | None = None

    try:
        while True:
            # Check for settings changes
            if app_settings.reload_images:
                viewer.change_folder(app_settings.image_folder)
                app_settings.reload_images = False

            if app_settings.restart_camera:
                camera.restart(app_settings.camera_index)
                app_settings.restart_camera = False

            success, frame = camera.read_frame()
            if not success:
                break

            hud.update_fps()
            frame = detector.process(frame)

            # ─── Gesture Recognition ──────────────────────────
            current_gesture = ""

            swipe = detector.get_swipe()
            if swipe == "right":
                viewer.next_image()
                current_gesture = "SWIPE → NEXT"
                print(f"  👋 Swipe Right → {viewer.get_status_text()}")
            elif swipe == "left":
                viewer.previous_image()
                current_gesture = "SWIPE ← PREV"
                print(f"  👋 Swipe Left  → {viewer.get_status_text()}")

            landmarks = detector.get_landmarks(frame)
            if landmarks:
                thumb = landmarks[4]
                index = landmarks[8]
                pinch_dist = np.hypot(index[1] - thumb[1], index[2] - thumb[2])

                if prev_pinch_dist is not None and pinch_dist < 100:
                    delta = prev_pinch_dist - pinch_dist
                    if abs(delta) > 2:
                        if delta > 0:
                            viewer.zoom_in(app_settings.pinch_sensitivity)
                            current_gesture = "ZOOM IN"
                        else:
                            viewer.zoom_out(app_settings.pinch_sensitivity)
                            current_gesture = "ZOOM OUT"
                prev_pinch_dist = pinch_dist

            if detector.is_open_palm():
                viewer.reset_transform()
                current_gesture = "RESET"
                print("  🖐️  Open Palm → Reset")

            # ─── Build Display ────────────────────────────────
            window_w = WINDOW_WIDTH
            window_h = WINDOW_HEIGHT
            if app_settings.fullscreen:
                # Get actual screen size
                rect = cv2.getWindowImageRect(WINDOW_TITLE)
                if rect:
                    _, _, window_w, window_h = rect

            canvas = np.zeros((window_h, window_w, 3), dtype=np.uint8)
            canvas[:] = (15, 15, 25)

            current_image = viewer.get_current_image()
            image_area_height = window_h - HUD_BAR_HEIGHT
            image_display = cv2.resize(current_image, (window_w, image_area_height))
            canvas[0:image_area_height, 0:window_w] = image_display

            canvas = hud.draw_all(
                canvas,
                webcam_frame=frame,
                image_count_text=viewer.get_status_text(),
                zoom_level=viewer.zoom_level,
                rotation_angle=viewer.rotation_angle,
                gesture_text=current_gesture,
            )

            cv2.imshow(WINDOW_TITLE, canvas)

            # ─── Keyboard ─────────────────────────────────────
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q") or key == 27:
                break
            elif key == ord("s"):
                # Open settings
                if settings_window is None or not settings_window._open:
                    settings_window = SettingsWindow(app_settings)
                    settings_window.show()
            elif key == ord("f"):
                app_settings.fullscreen = not app_settings.fullscreen
                if app_settings.fullscreen:
                    cv2.setWindowProperty(WINDOW_TITLE, cv2.WND_PROP_FULLSCREEN,
                                          cv2.WINDOW_FULLSCREEN)
                    print("[INFO] Fullscreen ON")
                else:
                    cv2.setWindowProperty(WINDOW_TITLE, cv2.WND_PROP_FULLSCREEN,
                                          cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT)
                    print("[INFO] Fullscreen OFF")
            elif key == 81:
                viewer.previous_image()
            elif key == 83:
                viewer.next_image()
            elif key == ord("+") or key == ord("="):
                viewer.zoom_in(0.1)
            elif key == ord("-"):
                viewer.zoom_out(0.1)
            elif key == ord("r"):
                viewer.rotate(5)
            elif key == ord("R"):
                viewer.rotate(-5)
            elif key == ord("0"):
                viewer.reset_transform()

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")

    finally:
        app_settings.save()
        camera.release()
        detector.release()
        cv2.destroyAllWindows()
        print("[INFO] Application closed.")


if __name__ == "__main__":
    main()
