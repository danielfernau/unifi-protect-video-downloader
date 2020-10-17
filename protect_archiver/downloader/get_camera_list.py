# get camera list
import logging
import requests

from datetime import datetime
from typing import List

from protect_archiver.auth import Auth
from protect_archiver.dataclasses import Camera


def get_camera_list(self, auth: Auth, connected=True) -> List[Camera]:
    cameras_uri = f"https://{self.address}:{self.port}/api/cameras"
    response = requests.get(
        cameras_uri,
        headers={"Authorization": "Bearer " + auth.get_api_token()},
        verify=self.verify_ssl,
    )
    if response.status_code != 200:
        return []

    logging.info("Successfully retrieved data from /api/cameras")
    cameras = response.json()

    camera_list = []
    for camera in cameras:
        if connected and camera["state"] != "CONNECTED":
            continue
        camera_list.append(
            Camera(
                id=camera["id"],
                name=camera["name"],
                recording_start=datetime.utcfromtimestamp(
                    camera["stats"]["video"]["recordingStart"] / 1000
                ),
            )
        )

    logging.info(
        "Cameras found:\n{}".format(
            "\n".join(f"- {camera.name} ({camera.id})" for camera in camera_list)
        )
    )

    return camera_list
