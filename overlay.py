"""
A fullscreen, transparent, click-through, always-on-top window that draws
boxes + skeletons on top of whatever is on your screen (e.g. a YouTube
video playing in your browser underneath it).

Click-through is done via the Windows extended window style
WS_EX_LAYERED | WS_EX_TRANSPARENT, set through pywin32 after the Qt
window handle exists. This only works on Windows.
"""

import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtCore import Qt, QTimer

import win32gui
import win32con
import win32api

import config
from detector import POSE_CONNECTIONS


def make_click_through(hwnd: int) -> None:
    ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
    ex_style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)


def activity_to_color(score: float) -> QColor:
    if score < config.URGENCY_LOW_THRESHOLD:
        r, g, b = config.BOX_COLOR_CALM
    elif score < config.URGENCY_HIGH_THRESHOLD:
        r, g, b = config.BOX_COLOR_MEDIUM
    else:
        r, g, b = config.BOX_COLOR_HIGH
    return QColor(b, g, r)  # BGR tuples in config -> QColor wants RGB order args reversed


class OverlayWindow(QWidget):
    def __init__(self, screen_width: int, screen_height: int):
        super().__init__()
        self.tracks = []  # updated externally each frame by main.py

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool  # keeps it out of the taskbar/alt-tab
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, screen_width, screen_height)

        self.font = QFont("Consolas", 9)

    def showEvent(self, event):
        super().showEvent(event)
        make_click_through(int(self.winId()))

    def set_tracks(self, tracks) -> None:
        self.tracks = tracks
        self.update()  # trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self.font)

        for track in self.tracks:
            color = activity_to_color(track.activity_score)
            pen = QPen(color, config.BOX_THICKNESS)
            painter.setPen(pen)

            x1, y1, x2, y2 = track.box
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)

            if config.SHOW_LABELS:
                label = f"ID {track.track_id}  activity: {track.activity_score:.2f}"
                painter.drawText(x1, max(0, y1 - 6), label)

            self._draw_skeleton(painter, track.keypoints, color)

    def _draw_skeleton(self, painter: QPainter, keypoints, color: QColor) -> None:
        if not keypoints:
            return
        pen = QPen(color, config.SKELETON_THICKNESS)
        painter.setPen(pen)

        for a, b in POSE_CONNECTIONS:
            if a >= len(keypoints) or b >= len(keypoints):
                continue
            xa, ya, va = keypoints[a]
            xb, yb, vb = keypoints[b]
            if va < 0.4 or vb < 0.4:
                continue
            painter.drawLine(int(xa), int(ya), int(xb), int(yb))
