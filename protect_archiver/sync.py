import json
import logging

from datetime import datetime
from os import path

import dateutil.parser

from .client import ProtectClient
from .downloader import Downloader
from .utils import calculate_intervals
from .utils import json_encode


class ProtectSync:
    def __init__(self, client: ProtectClient, destination_path: str, statefile: str):
        self.client = client
        self.statefile = path.abspath(path.join(destination_path, statefile))

    def readstate(self) -> dict:
        if path.isfile(self.statefile):
            with open(self.statefile) as fp:
                state = json.load(fp)
        else:
            state = {"cameras": {}}

        return state

    def writestate(self, state: dict):
        with open(self.statefile, "w") as fp:
            json.dump(state, fp, default=json_encode)

    def run(self, camera_list: list, ignore_state: bool = False):
        # noinspection PyUnboundLocalVariable
        logging.info(
            f"Synchronizing video files from 'https://{self.client.address}:{self.client.port}"
        )

        if not ignore_state:
            state = self.readstate()
        else:
            state = {"cameras": {}}
        for camera in camera_list:
            try:
                camera_state = state["cameras"].setdefault(camera.id, {})
                start = (
                    dateutil.parser.parse(camera_state["last"]).replace(
                        minute=0, second=0, microsecond=0
                    )
                    if "last" in camera_state
                    else camera.recording_start.replace(minute=0, second=0, microsecond=0)
                )
                end = datetime.now().replace(minute=0, second=0, microsecond=0)
                for interval_start, interval_end in calculate_intervals(start, end):
                    Downloader.download_footage(self.client, interval_start, interval_end, camera)
                    state["cameras"][camera.id] = {
                        "last": interval_end,
                        "name": camera.name,
                    }
            except Exception:
                logging.exception(
                    f"Failed to sync camera {camera.name} - continuing to next device"
                )
            finally:
                self.writestate(state)
