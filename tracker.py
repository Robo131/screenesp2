"""
Simple IOU-based multi-object tracker so boxes/skeletons stay assigned
to the "same" person across frames instead of flickering IDs.

Also computes a normalized "activity" score per track from how much
the person's keypoints have moved recently. This is purely a motion
metric (pixels moved per frame, normalized by box size) - it is not
emotion, mood, or intent inference.
"""

from dataclasses import dataclass, field
from collections import deque
import numpy as np

import config


def iou(box_a, box_b) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1, inter_y1 = max(ax1, bx1), max(ay1, by1)
    inter_x2, inter_y2 = min(ax2, bx2), min(ay2, by2)
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    union = area_a + area_b - inter_area
    return inter_area / union if union > 0 else 0.0


@dataclass
class Track:
    track_id: int
    box: tuple[int, int, int, int]
    keypoints: list[tuple[float, float, float]]
    misses: int = 0
    motion_history: deque = field(default_factory=lambda: deque(maxlen=config.MOTION_HISTORY_LEN))
    activity_score: float = 0.0


class PersonTracker:
    def __init__(self):
        self._tracks: dict[int, Track] = {}
        self._next_id = 1

    def update(self, detections: list) -> list[Track]:
        unmatched_dets = list(range(len(detections)))
        matched_track_ids = set()

        # greedy IOU matching
        for track_id, track in self._tracks.items():
            best_iou, best_det_idx = 0.0, None
            for det_idx in unmatched_dets:
                score = iou(track.box, detections[det_idx].box)
                if score > best_iou:
                    best_iou, best_det_idx = score, det_idx

            if best_iou >= config.TRACK_IOU_MATCH_THRESHOLD and best_det_idx is not None:
                det = detections[best_det_idx]
                self._apply_motion(track, det)
                track.box = det.box
                track.keypoints = det.keypoints
                track.misses = 0
                matched_track_ids.add(track_id)
                unmatched_dets.remove(best_det_idx)

        # age out unmatched tracks
        for track_id, track in list(self._tracks.items()):
            if track_id not in matched_track_ids:
                track.misses += 1
                if track.misses > config.TRACK_MAX_MISSES:
                    del self._tracks[track_id]

        # spawn new tracks for leftover detections
        for det_idx in unmatched_dets:
            det = detections[det_idx]
            track = Track(track_id=self._next_id, box=det.box, keypoints=det.keypoints)
            self._tracks[self._next_id] = track
            self._next_id += 1

        return list(self._tracks.values())

    def _apply_motion(self, track: Track, det) -> None:
        """Compare new keypoints to previous ones, normalize by box diagonal
        so a person standing close to the camera doesn't automatically
        register as 'more urgent' than someone farther away."""
        if not track.keypoints or not det.keypoints or len(track.keypoints) != len(det.keypoints):
            return

        x1, y1, x2, y2 = det.box
        diag = max(1.0, ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)

        deltas = []
        for (ox, oy, ov), (nx, ny, nv) in zip(track.keypoints, det.keypoints):
            if ov < 0.4 or nv < 0.4:
                continue
            dist = ((nx - ox) ** 2 + (ny - oy) ** 2) ** 0.5
            deltas.append(dist / diag)

        if deltas:
            track.motion_history.append(float(np.mean(deltas)))
            track.activity_score = float(np.mean(track.motion_history))
