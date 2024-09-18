from datetime import datetime
from datetime import timedelta
from typing import Iterable
from typing import Tuple

import dateutil.parser


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


def calculate_intervals(
    start: datetime,
    end: datetime,
    disable_alignment: bool = False,
    disable_splitting: bool = False,
) -> Iterable[Tuple[datetime, datetime]]:
    # if true, do not split into 1-hour segments
    # Caution: this can cause the Protect application to crash and restart!
    if disable_splitting:
        yield start, end - timedelta(milliseconds=1)  # yield everything at once
        return  # exit early

    # if true, disable alignment to absolute hours
    if disable_alignment:
        # divide total duration by 60 min, yield 1-hour segments
        for _ in range(int((end - start).seconds / 3600)):
            yield start, start + timedelta(minutes=59, seconds=59, milliseconds=999)
            start = start + timedelta(hours=1)
        yield start, end - timedelta(milliseconds=1)  # yield remaining segment
        return  # exit early

    #####
    # if none of the options above were used, calculate 1-hour segments and align them with absolute hours
    #####

    # calculate time differences to next or past full hour
    start_diff_to_next_full_hour = diff_round_up_to_full_hour(start) - start
    end_diff_to_past_full_hour = end - diff_round_down_to_full_hour(end)

    # save original start and end for later
    original_start = start
    original_end = end

    # yield interval from start to first full hour and align start to full hours
    # but only if the end datetime is past the next full hour after start datetime
    if (
        start_diff_to_next_full_hour.seconds != 0
        and (original_end - original_start) >= start_diff_to_next_full_hour
    ):
        yield start, start + (start_diff_to_next_full_hour - timedelta(milliseconds=1))
        start = start + start_diff_to_next_full_hour  # update start time

    # yield all remaining full-hour intervals
    for _ in range(int((end - start).total_seconds() / 3600)):
        yield start, start + timedelta(minutes=59, seconds=59, milliseconds=999)
        start = start + timedelta(minutes=60)  # update start time

    # if end is not on full hour, yield remaining segment
    if end_diff_to_past_full_hour.seconds != 0:
        yield start, original_end - timedelta(milliseconds=1)


print(
    list(
        calculate_intervals(
            dateutil.parser.parse("01.01.1970 08:56:00"),
            dateutil.parser.parse("01.01.1970 13:21:00"),
            disable_splitting=True,
        )
    )
)

# 15 min within the hour: OK
print(
    list(
        calculate_intervals(
            dateutil.parser.parse("01.01.1970 08:30:00"),
            dateutil.parser.parse("01.01.1970 08:45:00"),
            False,
        )
    )
)

# 30 min crossing the hour: OK
print(
    list(
        calculate_intervals(
            dateutil.parser.parse("01.01.1970 08:30:00"),
            dateutil.parser.parse("01.01.1970 09:15:00"),
            False,
        )
    )
)

# 15 min to full hour: OK
print(
    list(
        calculate_intervals(
            dateutil.parser.parse("01.01.1970 08:30:00"),
            dateutil.parser.parse("01.01.1970 09:00:00"),
            False,
        )
    )
)

# 15 min and 1 sec after the hour: FAIL
print(
    list(
        calculate_intervals(
            dateutil.parser.parse("01.01.1970 08:30:00"),
            dateutil.parser.parse("01.01.1970 09:00:01"),
            False,
        )
    )
)
print(
    list(
        calculate_intervals(
            dateutil.parser.parse("01.01.1970 08:30:00"),
            dateutil.parser.parse("01.01.1970 09:00:08"),
            False,
        )
    )
)


print(
    list(
        calculate_intervals(
            dateutil.parser.parse("01.01.1970 08:30:00"),
            dateutil.parser.parse("01.01.1970 13:45:00"),
            False,
        )
    )
)

print(
    list(
        calculate_intervals(
            dateutil.parser.parse("01.01.1970 21:30:00"),
            dateutil.parser.parse("01.02.1970 02:45:00"),
            False,
        )
    )
)

print(
    list(
        calculate_intervals(
            dateutil.parser.parse("1/8/2020 23:00:00"),
            dateutil.parser.parse("1/8/2020 23:59:00"),
            False,
        )
    )
)

print(int(dateutil.parser.parse("01.01.1970 08:30:00.995").timestamp() * 1e3))
# print(diff_round_up_to_full_hour(dateutil.parser.parse('01.01.1970 08:30:00')))
# print(diff_round_up_to_full_hour(dateutil.parser.parse('01.01.1970 08:59:00')))
# print(diff_round_up_to_full_hour(dateutil.parser.parse('01.01.1970 08:59:52')))
# print(diff_round_up_to_full_hour(dateutil.parser.parse('01.01.1970 08:59:59')))

# print(diff_round_down_to_full_hour(dateutil.parser.parse('01.01.1970 08:30:00')))
# print(diff_round_down_to_full_hour(dateutil.parser.parse('01.01.1970 08:59:00')))
# print(diff_round_down_to_full_hour(dateutil.parser.parse('01.01.1970 08:59:52')))
# print(diff_round_down_to_full_hour(dateutil.parser.parse('01.01.1970 08:59:59')))
