"""HUD overlay rendering — glassmorphism panels, FPS, status bar."""

import time
import cv2
import numpy as np
from config import (
    NEON_BLUE,
    NEON_CYAN,
    PANEL_BG,
    PANEL_BORDER,
    TEXT_SECONDARY,
    GLASS_ALPHA,
    GLASS_BORDER_WIDTH,
    PIP_WIDTH,
    PIP_HEIGHT,
    PIP_MARGIN,
    PIP_CORNER_RADIUS,
    HUD_BAR_HEIGHT,
)


class HUD:
    """Renders all HUD elements."""

    def __init__(self) -> None:
        self.fps: float = 0.0
        self._frame_count: int = 0
        self._last_fps_time: float = time.time()

    def update_fps(self) -> None:
        """Call once per frame."""
        self._frame_count += 1
        now = time.time()
        elapsed = now - self._last_fps_time
        if elapsed >= 0.5:
            self.fps = self._frame_count / elapsed
            self._frame_count = 0
            self._last_fps_time = now

    def draw_all(
        self,
        canvas: cv2.Mat,
        webcam_frame: cv2.Mat,
        image_count_text: str,
        zoom_level: float,
        rotation_angle: float,
        gesture_text: str = "",
    ) -> cv2.Mat:
        """Draw complete HUD on canvas."""
        h, w = canvas.shape[:2]

        self._draw_pip(canvas, webcam_frame, w)
        self._draw_hud_bar(canvas, image_count_text, zoom_level,
                           rotation_angle, gesture_text, w, h)
        return canvas

    def _draw_pip(self, canvas: cv2.Mat, webcam: cv2.Mat, canvas_w: int) -> None:
        """Picture-in-picture webcam in top-right."""
        pip = cv2.resize(webcam, (PIP_WIDTH, PIP_HEIGHT))

        x1 = canvas_w - PIP_WIDTH - PIP_MARGIN
        y1 = PIP_MARGIN
        x2 = x1 + PIP_WIDTH
        y2 = y1 + PIP_HEIGHT

        bg_x1, bg_y1 = x1 - 6, y1 - 6
        bg_x2, bg_y2 = x2 + 6, y2 + 6
        self._draw_glass_panel(canvas, bg_x1, bg_y1, bg_x2, bg_y2, PIP_CORNER_RADIUS)

        canvas[y1:y2, x1:x2] = pip
        cv2.rectangle(canvas, (x1, y1), (x2, y2), NEON_BLUE, 1)
        cv2.putText(canvas, "● LIVE", (x1 + 8, y1 + 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, NEON_CYAN, 1)

    def _draw_hud_bar(
        self, canvas: cv2.Mat, image_text: str, zoom: float,
        rotation: float, gesture: str, canvas_w: int, canvas_h: int,
    ) -> None:
        """Bottom status bar."""
        bar_y = canvas_h - HUD_BAR_HEIGHT

        overlay = canvas.copy()
        cv2.rectangle(overlay, (0, bar_y), (canvas_w, canvas_h), PANEL_BG, -1)
        cv2.addWeighted(canvas, 1 - GLASS_ALPHA, overlay, GLASS_ALPHA, 0, canvas)
        cv2.line(canvas, (0, bar_y), (canvas_w, bar_y), NEON_BLUE, 2)

        # Left: Image counter
        cv2.putText(canvas, "IMAGE", (30, bar_y + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_SECONDARY, 1)
        cv2.putText(canvas, image_text, (30, bar_y + 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEON_BLUE, 2)

        # Center: FPS
        x_pos = canvas_w // 2 - 60
        cv2.putText(canvas, "FPS", (x_pos, bar_y + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_SECONDARY, 1)
        cv2.putText(canvas, f"{self.fps:.0f}", (x_pos, bar_y + 42),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEON_CYAN, 2)

        # Right: Zoom & Rotation
        x_pos = canvas_w - 280
        cv2.putText(canvas, "ZOOM / ROT", (x_pos, bar_y + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, TEXT_SECONDARY, 1)
        cv2.putText(canvas, f"{zoom:.1f}x  |  {rotation:.0f}°",
                    (x_pos, bar_y + 42), cv2.FONT_HERSHEY_SIMPLEX, 0.6, NEON_BLUE, 2)

        # Gesture indicator
        if gesture:
            text_size = cv2.getTextSize(gesture, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            gx = canvas_w // 2 - text_size[0] // 2
            cv2.putText(canvas, gesture, (gx, bar_y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, NEON_CYAN, 1)

    def _draw_glass_panel(
        self, canvas: cv2.Mat, x1: int, y1: int, x2: int, y2: int, radius: int
    ) -> None:
        """Glassmorphism rounded rectangle."""
        overlay = canvas.copy()
        self._rounded_rect(overlay, x1, y1, x2, y2, radius, PANEL_BG, -1)
        cv2.addWeighted(overlay, GLASS_ALPHA, canvas, 1 - GLASS_ALPHA, 0, canvas)
        self._rounded_rect(canvas, x1, y1, x2, y2, radius, PANEL_BORDER, GLASS_BORDER_WIDTH)

    @staticmethod
    def _rounded_rect(
        img: cv2.Mat, x1: int, y1: int, x2: int, y2: int,
        radius: int, color: tuple, thickness: int,
    ) -> None:
        """Draw rounded rectangle using rectangles and corner ellipses."""
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(img.shape[1], x2)
        y2 = min(img.shape[0], y2)

        if x2 <= x1 or y2 <= y1:
            return

        # Horizontal bars
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
        # Vertical bars
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness)

        # Four corners
        cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius),
                    180, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius),
                    270, 0, 90, color, thickness)
        cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius),
                    90, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius),
                    0, 0, 90, color, thickness)
