"""
Run with:  python main.py

Press ESC at any time to quit (polled globally, works even though the
overlay window is click-through and can't receive keyboard focus).
"""

import sys
import time
import win32api

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

import config
from capture import ScreenCapture
from detector import PersonDetector
from tracker import PersonTracker
from overlay import OverlayWindow

VK_ESCAPE = 0x1B


class App:
    def __init__(self):
        print("[ScreenESP] Starting up...")

        print("[ScreenESP] Initializing screen capture...")
        self.capture = ScreenCapture(config.CAPTURE_REGION)
        mon = self.capture.monitor
        print(f"[ScreenESP] Capturing region: {mon['width']}x{mon['height']} at ({mon['left']},{mon['top']})")

        print("[ScreenESP] Loading YOLO model (this can take a few seconds on first run)...")
        self.detector = PersonDetector()
        print("[ScreenESP] YOLO model loaded.")

        self.tracker = PersonTracker()

        print("[ScreenESP] Creating overlay window...")
        origin_x, origin_y = self.capture.region_origin()
        self.overlay = OverlayWindow(mon["width"], mon["height"])
        self.overlay.move(origin_x, origin_y)
        self.overlay.show()
        print("[ScreenESP] Overlay is live. Press ESC to quit.")

        self.frame_count = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        interval_ms = int(1000 / config.CAPTURE_FPS_TARGET)
        self.timer.start(interval_ms)

    def tick(self):
        if win32api.GetAsyncKeyState(VK_ESCAPE) & 0x8000:
            self.shutdown()
            return

        frame = self.capture.grab()
        detections = self.detector.detect(frame)
        tracks = self.tracker.update(detections)
        self.overlay.set_tracks(tracks)

        self.frame_count += 1
        if self.frame_count % (config.CAPTURE_FPS_TARGET * 2) == 0:  # log roughly every 2 seconds
            print(f"[ScreenESP] frame {self.frame_count} - {len(tracks)} person(s) tracked")

    def shutdown(self):
        print("[ScreenESP] Shutting down...")
        self.timer.stop()
        self.detector.close()
        self.capture.close()
        QApplication.instance().quit()
        print("[ScreenESP] Closed cleanly.")


def main():
    app = QApplication(sys.argv)
    esp_app = App()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
