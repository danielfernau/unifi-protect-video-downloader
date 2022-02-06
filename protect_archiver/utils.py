from datetime import datetime
from datetime import timedelta
from typing import Iterable
from typing import Tuple

from protect_archiver.dataclasses import Camera


def json_encode(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


# return time difference between given date_time_object and next full hour
def diff_round_up_to_full_hour(date_time_object: datetime) -> datetime:
    if date_time_object.minute != 0 or date_time_object.second != 0:
        return date_time_object.replace(
            second=0, microsecond=0, minute=0, hour=date_time_object.hour
        ) + timedelta(hours=1, minutes=0)
    else:
        return date_time_object.replace(
            second=0, microsecond=0, minute=0, hour=date_time_object.hour
        ) + timedelta(hours=0, minutes=0)


# return time difference between given date_time_object and past full hour
def diff_round_down_to_full_hour(date_time_object: datetime) -> datetime:
    return date_time_object.replace(
        second=0, microsecond=0, minute=0, hour=date_time_object.hour
    ) + timedelta(hours=0, minutes=0)


# calculate and yield the intervals between the given start and end datetime objects
# example:
#   start = 01.01.1970 08:30:00
#   end = 01.01.1970 13:15:00
#
#   returns:
#       01.01.1970 08:30:00 - 01.01.1970 08:59:59
#       01.01.1970 09:00:00 - 01.01.1970 09:59:59
#       01.01.1970 10:00:00 - 01.01.1970 10:59:59
#       01.01.1970 11:00:00 - 01.01.1970 11:59:59
#       01.01.1970 12:00:00 - 01.01.1970 12:59:59
#       01.01.1970 13:00:00 - 01.01.1970 13:14:59
def calculate_intervals(start: datetime, end: datetime) -> Iterable[Tuple[datetime, datetime]]:
    # calculate time differences to next or past full hour
    start_diff_to_next_full_hour = diff_round_up_to_full_hour(start) - start
    end_diff_to_past_full_hour = end - diff_round_down_to_full_hour(end)

    if start_diff_to_next_full_hour.seconds != 0:
        # start is not on full hour, yield interval from start to first full hour
        yield start, start + start_diff_to_next_full_hour
        start = start + start_diff_to_next_full_hour

    original_end = end
    if end_diff_to_past_full_hour.seconds != 0:
        # end is not on full hour
        full_hour_end = end - end_diff_to_past_full_hour
        end = end - end_diff_to_past_full_hour
    else:
        full_hour_end = end

    # yield all full-hour intervals
    for n in range(int((end - start).total_seconds() / 3600)):
        yield start + timedelta(seconds=n * 3600), start + timedelta(seconds=((n + 1) * 3600) - 1)

    if original_end != full_hour_end:
        # if end is not on full hour, yield the interval between the last full hour and the end
        yield full_hour_end, original_end - timedelta(seconds=1)


def format_bytes(size: int) -> str:
    # 2**10 = 1024
    power = 2**10
    n = 0
    power_labels = {0: "", 1: "k", 2: "m", 3: "g", 4: "t"}
    while size > power:
        size /= power
        n += 1
    return f"{int(size * 100) / 100} {power_labels[n]}b"


def make_camera_name_fs_safe(camera: Camera) -> str:
    return (
        "".join([c for c in camera.name if c.isalpha() or c.isdigit() or c == " "]).rstrip()
        + f" ({str(camera.id)[-4:]})"
    )


def print_download_stats(client):
    files_total = client.files_downloaded + client.files_skipped + client.files_failed
    print(
        f"{client.files_downloaded} files downloaded ({format_bytes(client.bytes_downloaded)}), "
        f"{client.files_skipped} files skipped, "
        f"{client.files_failed} files failed, "
        f"{files_total} files total"
    )
