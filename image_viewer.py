"""Image loading, navigation, zoom, rotation, and transitions for HoloGallery."""

import os
import cv2
import numpy as np
from config import (
    SUPPORTED_IMAGE_FORMATS,
    DEFAULT_IMAGE_FOLDER,
    IMAGE_DISPLAY_WIDTH,
    IMAGE_DISPLAY_HEIGHT,
    ZOOM_MIN,
    ZOOM_MAX,
    ROTATION_MIN,
    ROTATION_MAX,
    TRANSITION_FRAMES,
)


class ImageViewer:
    """Loads images, provides navigation, zoom, rotation, and transitions."""

    def __init__(self, folder_path: str = DEFAULT_IMAGE_FOLDER) -> None:
        self.folder_path: str = folder_path
        self.images: list[str] = []
        self.current_index: int = 0
        self.total_images: int = 0

        # Transform state
        self.zoom_level: float = 1.0
        self.rotation_angle: float = 0.0

        # Transition state
        self._transition_alpha: float = 1.0
        self._previous_image: cv2.Mat | None = None
        self._transition_counter: int = 0

        self._load_images()

    # ─── Image Loading ─────────────────────────────────────────────

    def _load_images(self) -> None:
        """Scan the folder for supported image files."""
        if not os.path.isdir(self.folder_path):
            print(f"[WARNING] Image folder not found: {self.folder_path}")
            print(f"[INFO] Creating folder: {self.folder_path}")
            os.makedirs(self.folder_path, exist_ok=True)
            return

        all_files = os.listdir(self.folder_path)
        self.images = []

        for file in sorted(all_files):
            if file.lower().endswith(SUPPORTED_IMAGE_FORMATS):
                full_path = os.path.join(self.folder_path, file)
                self.images.append(full_path)

        self.total_images = len(self.images)
        self.current_index = 0 if self.total_images > 0 else -1

        if self.total_images == 0:
            print(f"[INFO] No images found in {self.folder_path}")
        else:
            print(f"[INFO] Loaded {self.total_images} image(s)")

    # ─── Navigation ────────────────────────────────────────────────

    def next_image(self) -> None:
        """Move to next image with transition."""
        if self.total_images == 0:
            return
        self._start_transition()
        self.current_index = (self.current_index + 1) % self.total_images

    def previous_image(self) -> None:
        """Move to previous image with transition."""
        if self.total_images == 0:
            return
        self._start_transition()
        self.current_index = (self.current_index - 1) % self.total_images

    def get_status_text(self) -> str:
        """Get image counter text like '3 / 12'."""
        if self.total_images == 0:
            return "No Images"
        return f"{self.current_index + 1} / {self.total_images}"

    def change_folder(self, new_path: str) -> None:
        """Load images from a different folder."""
        self.folder_path = new_path
        self._load_images()
        self.reset_transform()

    # ─── Zoom & Rotation ───────────────────────────────────────────

    def zoom_in(self, amount: float = 0.1) -> None:
        """Increase zoom level."""
        self.zoom_level = min(self.zoom_level + amount, ZOOM_MAX)

    def zoom_out(self, amount: float = 0.1) -> None:
        """Decrease zoom level."""
        self.zoom_level = max(self.zoom_level - amount, ZOOM_MIN)

    def rotate(self, delta_degrees: float) -> None:
        """Rotate by delta degrees."""
        self.rotation_angle += delta_degrees
        self.rotation_angle = max(ROTATION_MIN, min(self.rotation_angle, ROTATION_MAX))

    def reset_transform(self) -> None:
        """Reset zoom and rotation to default."""
        self.zoom_level = 1.0
        self.rotation_angle = 0.0

    # ─── Transitions ───────────────────────────────────────────────

    def _start_transition(self) -> None:
        """Save current image and start crossfade."""
        if self.total_images > 0:
            self._previous_image = self.get_current_image()
            self._transition_counter = TRANSITION_FRAMES
            self._transition_alpha = 0.0

    def _update_transition(self) -> None:
        """Advance transition by one frame."""
        if self._transition_counter > 0:
            self._transition_counter -= 1
            self._transition_alpha = 1.0 - (
                self._transition_counter / TRANSITION_FRAMES
            )

    def _get_transition_image(self, current: cv2.Mat) -> cv2.Mat:
        """Blend previous and current image during transition."""
        self._update_transition()

        if self._previous_image is None or self._transition_counter <= 0:
            return current

        if self._previous_image.shape != current.shape:
            self._previous_image = cv2.resize(
                self._previous_image, (current.shape[1], current.shape[0])
            )

        alpha = self._transition_alpha
        blended = cv2.addWeighted(
            self._previous_image, 1 - alpha, current, alpha, 0
        )
        return blended

    # ─── Rendering ─────────────────────────────────────────────────

    def get_current_image(self) -> cv2.Mat:
        """Load, transform, and return the current image."""
        if self.total_images == 0:
            return self._create_placeholder()

        path = self.images[self.current_index]
        image = cv2.imread(path)

        if image is None:
            print(f"[WARNING] Could not read: {path}")
            return self._create_placeholder()

        image = self._apply_zoom(image)
        image = self._apply_rotation(image)
        image = self._resize_fit(image, IMAGE_DISPLAY_WIDTH, IMAGE_DISPLAY_HEIGHT)
        image = self._get_transition_image(image)

        return image

    # ─── Private Helpers ───────────────────────────────────────────

    def _apply_zoom(self, image: cv2.Mat) -> cv2.Mat:
        """Crop center of image based on zoom level."""
        if self.zoom_level == 1.0:
            return image

        h, w = image.shape[:2]
        new_w = int(w / self.zoom_level)
        new_h = int(h / self.zoom_level)

        x1 = max(0, (w - new_w) // 2)
        y1 = max(0, (h - new_h) // 2)
        x2 = min(w, x1 + new_w)
        y2 = min(h, y1 + new_h)

        cropped = image[y1:y2, x1:x2]
        return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

    def _apply_rotation(self, image: cv2.Mat) -> cv2.Mat:
        """Rotate image around its center."""
        if self.rotation_angle == 0.0:
            return image

        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, self.rotation_angle, 1.0)
        rotated = cv2.warpAffine(
            image, matrix, (w, h),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )
        return rotated

    def _resize_fit(
        self, image: cv2.Mat, target_w: int, target_h: int
    ) -> cv2.Mat:
        """Resize to fit target, preserving aspect ratio with letterbox."""
        h, w = image.shape[:2]
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        canvas = np.zeros((target_h, target_w, 3), dtype=np.uint8)
        x_offset = (target_w - new_w) // 2
        y_offset = (target_h - new_h) // 2
        canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized

        return canvas

    def _create_placeholder(self) -> cv2.Mat:
        """Create a dark placeholder with 'No Images' text."""
        canvas = np.zeros(
            (IMAGE_DISPLAY_HEIGHT, IMAGE_DISPLAY_WIDTH, 3), dtype=np.uint8
        )
        canvas[:] = (30, 30, 40)

        text = "No Images"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        thickness = 2
        color = (100, 100, 120)

        (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
        x = (IMAGE_DISPLAY_WIDTH - text_w) // 2
        y = (IMAGE_DISPLAY_HEIGHT + text_h) // 2
        cv2.putText(canvas, text, (x, y), font, font_scale, color, thickness)

        return canvas
