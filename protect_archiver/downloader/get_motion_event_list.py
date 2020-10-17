# get motion events list
import logging
import requests

from datetime import datetime
from typing import List

from protect_archiver.auth import Auth
from protect_archiver.dataclasses import MotionEvent


def get_motion_event_list(
    self, start: datetime, end: datetime, auth: Auth
) -> List[MotionEvent]:
    motion_events_uri = (
        f"https://{self.address}:{self.port}/api/events?type=motion"
        f"&start={int(start.timestamp()) * 1000}&end={int(end.timestamp()) * 1000}"
    )
    response = requests.get(
        motion_events_uri,
        headers={"Authorization": "Bearer " + auth.get_api_token()},
        verify=self.verify_ssl,
    )
    if response.status_code != 200:
        return []

    logging.info("Successfully retrieved data from /api/events")
    motion_events = response.json()

    motion_event_list = []
    for motion_event in motion_events:
        motion_event_list.append(
            MotionEvent(
                id=motion_event["id"],
                start=datetime.utcfromtimestamp(motion_event["start"] / 1000),
                end=datetime.utcfromtimestamp(motion_event["end"] / 1000),
                camera_id=motion_event["camera"],
                score=motion_event["score"],
                thumbnail_id=motion_event["thumbnail"],
                heatmap_id=motion_event["heatmap"],
            )
        )

    logging.info(
        f"{len(motion_event_list)} motion events found between {start} and {end}"
    )

    return motion_event_list
