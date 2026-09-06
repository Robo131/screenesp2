"""
Grabs frames from the screen using mss (fast, cross-platform, no GPU needed).
Returns BGR numpy arrays ready for OpenCV / YOLO.
"""

import mss
import numpy as np
import cv2

import config


class ScreenCapture:
    def __init__(self, region: dict | None = None):
        self._sct = mss.mss()
        if region is not None:
            self.monitor = region
        else:
            # monitors[0] is the "all monitors combined" virtual screen in mss;
            # monitors[1] is the primary monitor. Use primary by default.
            self.monitor = self._sct.monitors[1]

    def grab(self) -> np.ndarray:
        raw = self._sct.grab(self.monitor)
        frame = np.array(raw)  # BGRA
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame

    def region_origin(self) -> tuple[int, int]:
        """Top-left corner of the captured region, in screen coordinates.
        Needed so the overlay window (which may cover the whole screen)
        can place boxes at the right absolute position."""
        return self.monitor["left"], self.monitor["top"]

    def close(self):
        self._sct.close()
