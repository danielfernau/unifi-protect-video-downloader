# get motion events list
import logging
from datetime import datetime
from typing import List

import requests

from protect_archiver.dataclasses import MotionEvent


def get_motion_event_list(session, start: datetime, end: datetime) -> List[MotionEvent]:
    motion_events_uri = (
        f"{session.authority}{session.base_path}/events?type=motion"
        f"&start={int(start.timestamp()) * 1000}&end={int(end.timestamp()) * 1000}"
    )
    response = requests.get(
        motion_events_uri,
        cookies={"TOKEN": session.get_api_token()},
        verify=session.verify_ssl,
    )
    if response.status_code != 200:
        print(f"Error while loading motion events list: {response.status_code}")
        return []

    logging.info(f"Successfully retrieved data from {motion_events_uri}")
    motion_events = response.json()

    motion_event_list = []
    for motion_event in motion_events:
        motion_event_list.append(
            MotionEvent(
                id=motion_event["id"],
                start=datetime.fromtimestamp(motion_event["start"] / 1000),
                end=datetime.fromtimestamp(motion_event["end"] / 1000),
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
