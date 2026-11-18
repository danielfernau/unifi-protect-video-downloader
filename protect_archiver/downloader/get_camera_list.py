# get camera list
import logging

from datetime import datetime
from typing import Any
from typing import List

import requests

from protect_archiver.dataclasses import Camera
from protect_archiver.dataclasses import Stream


def get_camera_list(session: Any) -> List[Camera]:
    cameras_uri = f"{session.authority}{session.base_path}/cameras"

    response = (
        requests.get(
            cameras_uri,
            cookies={"TOKEN": session.get_api_token()},
            verify=session.verify_ssl,
        )
        if session.__class__.__name__ == "UniFiOSClient"
        else requests.get(
            cameras_uri,
            headers={"Authorization": f"Bearer {session.get_api_token()}"},
            verify=session.verify_ssl,
        )
    )

    if response.status_code != 200:
        print(f"Error while loading camera list: {response.status_code}")
        return []

    logging.info(f"Successfully retrieved data from {cameras_uri}")
    cameras = response.json()

    camera_list = []
    for camera in cameras:
        camera_data = Camera(
            id=camera["id"],
            name=camera["name"],
            recording_start=datetime.min,
            streams=[
                Stream(
                    id=channel["id"],
                    name=channel.get("name") or f"Stream {channel['id']}",
                    enabled=channel.get("enabled", True),
                    width=channel.get("width"),
                    height=channel.get("height"),
                    fps=channel.get("fps"),
                    bitrate=channel.get("bitrate"),
                )
                for channel in camera.get("channels") or []
            ],
            recording_mode=(camera.get("recordingSettings") or {}).get("mode"),
        )
        if camera["stats"]["video"]["recordingStart"]:
            camera_data.recording_start = datetime.utcfromtimestamp(
                camera["stats"]["video"]["recordingStart"] / 1000
            )
        camera_list.append(camera_data)

    logging.info(
        "Cameras found:\n{}".format(
            "\n".join(f"- {camera.name} ({camera.id})" for camera in camera_list)
        )
    )

    return camera_list
