"""Choosing which video stream (High/Medium/Low) to export per camera.

A stream selection is a comma-separated list of entries. An entry is either a stream
for every camera ("low") or a stream for one camera ("<camera id or name>=medium").
Streams are named as Protect names them (High, Medium, Low) or given by number (0, 1, 2).

    --stream low                              every camera: Low
    --stream "6a9eef70004eed03e40003f8=medium" one camera: Medium, the rest unchanged (High)
    --stream "low,Theaterzaal=high"           Theaterzaal: High, every other camera: Low
"""

import logging

from dataclasses import dataclass
from dataclasses import field
from typing import Dict
from typing import List
from typing import Optional

from protect_archiver.dataclasses import Camera
from protect_archiver.dataclasses import Stream


class StreamSelectionError(ValueError):
    pass


@dataclass
class StreamSelection:
    default: Optional[str] = None
    per_camera: Dict[str, str] = field(default_factory=dict)


def parse_stream_selection(spec: Optional[str]) -> StreamSelection:
    selection = StreamSelection()
    if not spec:
        return selection

    for entry in spec.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if "=" in entry:
            camera_key, stream = (part.strip() for part in entry.rsplit("=", 1))
            if not camera_key or not stream:
                raise StreamSelectionError(
                    f"Invalid stream selection '{entry}': use '<camera>=<stream>'"
                )
            if camera_key.lower() in selection.per_camera:
                raise StreamSelectionError(f"Camera '{camera_key}' is given more than once")
            selection.per_camera[camera_key.lower()] = stream
        else:
            if selection.default is not None:
                raise StreamSelectionError(
                    f"More than one stream for all cameras given ('{selection.default}' and"
                    f" '{entry}')"
                )
            selection.default = entry

    return selection


def find_stream(camera: Camera, stream: str) -> Optional[Stream]:
    """Find a camera's stream by number or by name (case-insensitive)"""
    if stream.isdigit():
        return camera.get_stream(int(stream))
    return next((s for s in camera.streams if s.name.lower() == stream.lower()), None)


def _describe_streams(camera: Camera) -> str:
    if not camera.streams:
        return "this camera reports no streams"
    return "available: " + ", ".join(
        f"{s.id} {s.name}{'' if s.enabled else ' (disabled)'}" for s in camera.streams
    )


def apply_stream_selection(camera_list: List[Camera], spec: Optional[str]) -> None:
    """Set `selected_stream` on each camera according to `spec`.

    A stream chosen for one camera must exist on it, or this raises StreamSelectionError.
    A stream chosen for all cameras is skipped, with a warning, on cameras that don't have it.
    """
    selection = parse_stream_selection(spec)

    cameras_by_key: Dict[str, Camera] = {}
    for camera in camera_list:
        cameras_by_key[camera.id.lower()] = camera
        cameras_by_key.setdefault(camera.name.lower(), camera)

    explicit: Dict[str, str] = {}
    for camera_key, stream in selection.per_camera.items():
        matched_camera = cameras_by_key.get(camera_key)
        if matched_camera is None:
            raise StreamSelectionError(
                f"No selected camera matches '{camera_key}'. Use a camera ID or name as listed by"
                " the 'cameras' command"
            )
        if matched_camera.id in explicit:
            raise StreamSelectionError(f"Camera '{matched_camera.name}' is given more than once")
        explicit[matched_camera.id] = stream

    for camera in camera_list:
        if camera.id in explicit:
            found = find_stream(camera, explicit[camera.id])
            if found is None or not found.enabled:
                raise StreamSelectionError(
                    f"Camera '{camera.name}' has no enabled stream '{explicit[camera.id]}'"
                    f" ({_describe_streams(camera)})"
                )
            camera.selected_stream = found.id
        elif selection.default is not None:
            found = find_stream(camera, selection.default)
            if found is None or not found.enabled:
                logging.warning(
                    f"Camera '{camera.name}' has no enabled stream '{selection.default}'"
                    f" ({_describe_streams(camera)}) - using the default stream"
                )
                continue
            camera.selected_stream = found.id


def stream_query_param(camera: Camera) -> str:
    """The export query parameter for the camera's selected stream, if one was chosen"""
    if camera.selected_stream is None:
        return ""
    return f"&channel={camera.selected_stream}"


def stream_filename_suffix(camera: Camera) -> str:
    """Marks files exported from a stream other than the first (High) one, e.g. ' (Low)'.

    Keeps such files apart from full-quality downloads of the same time range, which
    matters with --skip-existing-files.
    """
    if not camera.selected_stream:  # None or 0 (High) keep the original file names
        return ""
    stream = camera.get_stream(camera.selected_stream)
    name = stream.name if stream else f"Stream {camera.selected_stream}"
    return f" ({name})"
