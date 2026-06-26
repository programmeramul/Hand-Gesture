"""Hand gesture detection and recognition using MediaPipe."""

import math
import cv2
import mediapipe as mp
from config import (
    MAX_HANDS,
    MIN_DETECTION_CONFIDENCE,
    MIN_TRACKING_CONFIDENCE,
    LANDMARK_COLOR,
    LANDMARK_RADIUS,
    SWIPE_THRESHOLD,
    SWIPE_TIME_WINDOW,
    PINCH_SENSITIVITY,
    ROTATION_SENSITIVITY,
    OPEN_PALM_FINGERS,
    GLOW_RADIUS,
    GLOW_ALPHA,
    GLOW_COLOR,
    NEON_CYAN,
)


class GestureDetector:
    """Detects hands, draws landmarks, and recognizes gestures."""

    def __init__(self) -> None:
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=MAX_HANDS,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )

        # Swipe tracking state
        self.wrist_history: list[tuple[float, float]] = []
        self.swipe_detected: str | None = None

        # Pinch state
        self.is_pinching: bool = False
        self.pinch_start_distance: float = 0.0

        # Rotation state
        self.is_rotating: bool = False
        self.rotation_start_angle: float = 0.0
        self.current_angle: float = 0.0

        # Open palm state
        self.open_palm_frames: int = 0

    def process(self, frame: cv2.Mat) -> cv2.Mat:
        """Detect hands, draw landmarks, and update gesture state."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False

        results = self.hands.process(rgb_frame)
        rgb_frame.flags.writeable = True

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw connections
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style(),
                )

                # Draw neon glow landmarks
                for lm in hand_landmarks.landmark:
                    h, w, _ = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)

                    # Outer glow
                    glow_overlay = frame.copy()
                    cv2.circle(glow_overlay, (cx, cy), GLOW_RADIUS, GLOW_COLOR, -1)
                    cv2.addWeighted(glow_overlay, GLOW_ALPHA, frame, 1 - GLOW_ALPHA, 0, frame)

                    # Bright dot
                    cv2.circle(frame, (cx, cy), LANDMARK_RADIUS, NEON_CYAN, -1)
                    # Hot center
                    cv2.circle(frame, (cx, cy), 2, (255, 255, 255), -1)

                # Update gesture recognition
                self._update_gestures(hand_landmarks.landmark, w, h)
                self._draw_gesture_hints(frame)

        return frame

    def get_landmarks(self, frame: cv2.Mat) -> list | None:
        """Extract landmark coordinates."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)
        rgb_frame.flags.writeable = True

        if results.multi_hand_landmarks:
            h, w, _ = frame.shape
            landmarks = []
            for lm in results.multi_hand_landmarks[0].landmark:
                landmarks.append((len(landmarks), lm.x * w, lm.y * h, lm.z))
            return landmarks
        return None

    # ─── Public gesture queries ────────────────────────────────────

    def get_swipe(self) -> str | None:
        """Return 'left' or 'right' if swipe detected, then clear it."""
        swipe = self.swipe_detected
        self.swipe_detected = None
        return swipe

    def is_open_palm(self) -> bool:
        """Return True if open palm detected."""
        return self.open_palm_frames >= 10

    # ─── Internal gesture logic ────────────────────────────────────

    def _update_gestures(self, landmarks, frame_w: int, frame_h: int) -> None:
        """Analyze landmarks and update gesture states."""
        wrist = (landmarks[0].x * frame_w, landmarks[0].y * frame_h)
        thumb_tip = (landmarks[4].x * frame_w, landmarks[4].y * frame_h)
        index_tip = (landmarks[8].x * frame_w, landmarks[8].y * frame_h)
        middle_tip = (landmarks[12].x * frame_w, landmarks[12].y * frame_h)

        # Swipe Detection
        self.wrist_history.append(wrist)
        if len(self.wrist_history) > SWIPE_TIME_WINDOW:
            self.wrist_history.pop(0)

        if len(self.wrist_history) >= SWIPE_TIME_WINDOW:
            start_x = self.wrist_history[0][0]
            end_x = self.wrist_history[-1][0]
            dx = end_x - start_x

            if dx > SWIPE_THRESHOLD:
                self.swipe_detected = "right"
                self.wrist_history.clear()
            elif dx < -SWIPE_THRESHOLD:
                self.swipe_detected = "left"
                self.wrist_history.clear()

        # Pinch Detection
        pinch_dist = self._distance(thumb_tip, index_tip)
        self.is_pinching = pinch_dist < 50

        # Rotation Detection
        index_middle_dist = self._distance(index_tip, middle_tip)
        self.is_rotating = 30 < index_middle_dist < 120

        if self.is_rotating:
            self.current_angle = self._angle(index_tip, middle_tip)

        # Open Palm Detection
        extended = 0
        if landmarks[4].x < landmarks[3].x:
            extended += 1
        for tip_id, pip_id in [(8, 6), (12, 10), (16, 14), (20, 18)]:
            if landmarks[tip_id].y < landmarks[pip_id].y:
                extended += 1

        if extended >= OPEN_PALM_FINGERS:
            self.open_palm_frames += 1
        else:
            self.open_palm_frames = 0

    def _draw_gesture_hints(self, frame: cv2.Mat) -> None:
        """Draw small text showing active gesture."""
        y_pos = 30
        if self.is_pinching:
            cv2.putText(frame, "PINCH", (10, y_pos),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        if self.is_rotating:
            cv2.putText(frame, "ROTATE", (10, y_pos + 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        if self.open_palm_frames >= 5:
            cv2.putText(frame, "OPEN PALM", (10, y_pos + 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # ─── Math helpers ──────────────────────────────────────────────

    @staticmethod
    def _distance(p1: tuple, p2: tuple) -> float:
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    @staticmethod
    def _angle(p1: tuple, p2: tuple) -> float:
        return math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))

    def release(self) -> None:
        """Release MediaPipe resources."""
        self.hands.close()
        print("[INFO] Gesture detector released")
