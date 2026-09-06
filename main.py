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
        self.capture = ScreenCapture(config.CAPTURE_REGION)
        self.detector = PersonDetector()
        self.tracker = PersonTracker()

        origin_x, origin_y = self.capture.region_origin()
        mon = self.capture.monitor
        self.overlay = OverlayWindow(mon["width"], mon["height"])
        self.overlay.move(origin_x, origin_y)
        self.overlay.show()

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

    def shutdown(self):
        self.timer.stop()
        self.detector.close()
        self.capture.close()
        QApplication.instance().quit()


def main():
    app = QApplication(sys.argv)
    esp_app = App()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
