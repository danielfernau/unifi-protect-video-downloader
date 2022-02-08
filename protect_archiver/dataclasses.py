from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Camera:
    def __getitem__(self, key: str) -> Any:
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
