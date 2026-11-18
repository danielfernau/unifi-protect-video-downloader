from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any
from typing import List
from typing import Optional


@dataclass
class Stream:
    """One of a camera's video streams ("channels" in the Protect API), e.g. High/Medium/Low"""

    id: int
    name: str
    enabled: bool = True
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[int] = None
    bitrate: Optional[int] = None  # bits per second

    @property
    def resolution(self) -> str:
        if self.width and self.height:
            return f"{self.width}x{self.height}"
        return "unknown"


@dataclass
class Camera:
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    id: str
    name: str
    recording_start: datetime
    streams: List[Stream] = field(default_factory=list)
    recording_mode: Optional[str] = None
    # stream to request when exporting video; None leaves the choice to Protect (High)
    selected_stream: Optional[int] = None

    def get_stream(self, stream_id: int) -> Optional[Stream]:
        return next((s for s in self.streams if s.id == stream_id), None)


@dataclass
class MotionEvent:
    id: str
    start: datetime
    end: datetime
    camera_id: str
    score: int
    thumbnail_id: str
    heatmap_id: str
