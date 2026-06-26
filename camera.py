"""Webcam capture module for HoloGallery."""

import cv2
from config import CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS


class Camera:
    """Manages webcam capture using OpenCV."""

    def __init__(self, camera_index: int = 0) -> None:
        self.camera_index: int = camera_index
        self.cap: cv2.VideoCapture | None = None

    def start(self) -> bool:
        """Open the webcam and configure resolution/FPS."""
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            print(f"[ERROR] Cannot open camera at index {self.camera_index}")
            return False

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"[INFO] Camera opened: {actual_width}x{actual_height} (index {self.camera_index})")

        return True

    def restart(self, new_index: int) -> bool:
        """Release current camera and open a new one."""
        self.release()
        self.camera_index = new_index
        return self.start()

    def read_frame(self) -> tuple[bool, cv2.Mat | None]:
        """Read a single frame from the webcam."""
        if self.cap is None:
            return False, None

        success, frame = self.cap.read()
        if not success:
            print("[WARNING] Failed to read frame from camera")
            return False, None

        frame = cv2.flip(frame, 1)
        return True, frame

    def release(self) -> None:
        """Release the camera resource."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            print("[INFO] Camera released")
