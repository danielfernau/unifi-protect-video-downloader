import json
import logging

from datetime import datetime
from os import path

import dateutil.parser

from .client import ProtectClient
from .utils import calculate_intervals, json_encode


class ProtectSync(object):
    def __init__(self, client: ProtectClient, destination_path: str, statefile: str):
        self.client = client
        self.statefile = path.abspath(path.join(destination_path, statefile))

    def readstate(self) -> dict:
        if path.isfile(self.statefile):
            with open(self.statefile, "r") as fp:
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
                # TODO(dcramer): the default start date wont work, as if the file doesnt exist it seems to just
                # cause a read timeout. We need to try to query the API more safely
                start = (
                    dateutil.parser.parse(camera_state["last"])
                    if "last" in camera_state
                    else camera.recording_start
                )
                end = datetime.now().replace(minute=0, second=0)
                for interval_start, interval_end in calculate_intervals(start, end):
                    self.client.download_footage(interval_start, interval_end, camera)
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
