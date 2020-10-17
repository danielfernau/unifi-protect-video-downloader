from dataclasses import dataclass
from datetime import datetime


@dataclass
class Camera:
    def __getitem__(self, key):
        return getattr(self, key)

    id: str
    name: str
    recording_start: datetime


@dataclass
class MotionEvent:
    id: str
    start: datetime
    end: datetime
    camera_id: str
    score: int
    thumbnail_id: str
    heatmap_id: str
