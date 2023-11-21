from datetime import datetime

import dateutil.parser

from .utils import calculate_intervals


def test_calculate_intervals_multiple_partial_no_alignment_1() -> None:
    start = dateutil.parser.parse("01/01/1970 08:30:00")
    end = dateutil.parser.parse("01/01/1970 08:45:00")

    result = list(calculate_intervals(start, end, disable_alignment=True))
    assert result == [(datetime(1970, 1, 1, 8, 30), datetime(1970, 1, 1, 8, 44, 59, 999000))]


def test_calculate_intervals_multiple_partial_no_alignment_2() -> None:
    start = dateutil.parser.parse("01/01/1970 08:30:00")
    end = dateutil.parser.parse("01/01/1970 13:45:00")

    result = list(calculate_intervals(start, end, disable_alignment=True))
    assert result == [
        (datetime(1970, 1, 1, 8, 30), datetime(1970, 1, 1, 9, 29, 59, 999000)),
        (datetime(1970, 1, 1, 9, 30), datetime(1970, 1, 1, 10, 29, 59, 999000)),
        (datetime(1970, 1, 1, 10, 30), datetime(1970, 1, 1, 11, 29, 59, 999000)),
        (datetime(1970, 1, 1, 11, 30), datetime(1970, 1, 1, 12, 29, 59, 999000)),
        (datetime(1970, 1, 1, 12, 30), datetime(1970, 1, 1, 13, 29, 59, 999000)),
        (datetime(1970, 1, 1, 13, 30), datetime(1970, 1, 1, 13, 44, 59, 999000)),
    ]


def test_calculate_intervals_multiple_partial_no_alignment_3() -> None:
    start = dateutil.parser.parse("01/01/1970 08:53:00")
    end = dateutil.parser.parse("01/01/1970 13:45:00")

    result = list(calculate_intervals(start, end, disable_alignment=True))
    assert result == [
        (datetime(1970, 1, 1, 8, 53), datetime(1970, 1, 1, 9, 52, 59, 999000)),
        (datetime(1970, 1, 1, 9, 53), datetime(1970, 1, 1, 10, 52, 59, 999000)),
        (datetime(1970, 1, 1, 10, 53), datetime(1970, 1, 1, 11, 52, 59, 999000)),
        (datetime(1970, 1, 1, 11, 53), datetime(1970, 1, 1, 12, 52, 59, 999000)),
        (datetime(1970, 1, 1, 12, 53), datetime(1970, 1, 1, 13, 44, 59, 999000)),
    ]


def test_calculate_intervals_no_splitting() -> None:
    start = dateutil.parser.parse("01/01/1970 08:56:00")
    end = dateutil.parser.parse("01/01/1970 13:21:00")

    result = list(calculate_intervals(start, end, disable_splitting=True))
    assert result == [(datetime(1970, 1, 1, 8, 56), datetime(1970, 1, 1, 13, 20, 59, 999000))]


def test_calculate_intervals_15m_within_hour() -> None:
    start = dateutil.parser.parse("01/01/1970 08:30:00")
    end = dateutil.parser.parse("01/01/1970 08:45:00")

    result = list(calculate_intervals(start, end))
    assert result == [(datetime(1970, 1, 1, 8, 30), datetime(1970, 1, 1, 8, 44, 59, 999000))]


def test_calculate_intervals_30m_crossing_hour() -> None:
    start = dateutil.parser.parse("01/01/1970 08:30:00")
    end = dateutil.parser.parse("01/01/1970 09:15:00")

    result = list(calculate_intervals(start, end))
    assert result == [
        (datetime(1970, 1, 1, 8, 30), datetime(1970, 1, 1, 8, 59, 59, 999000)),
        (datetime(1970, 1, 1, 9, 0), datetime(1970, 1, 1, 9, 14, 59, 999000)),
    ]


def test_calculate_intervals_15m_to_full_hour() -> None:
    start = dateutil.parser.parse("01/01/1970 08:30:00")
    end = dateutil.parser.parse("01/01/1970 09:00:00")

    result = list(calculate_intervals(start, end))
    assert result == [(datetime(1970, 1, 1, 8, 30), datetime(1970, 1, 1, 8, 59, 59, 999000))]


def test_calculate_intervals_15m_1s_after_the_hour() -> None:
    start = dateutil.parser.parse("01/01/1970 08:30:00")
    end = dateutil.parser.parse("01/01/1970 09:00:01")

    result = list(calculate_intervals(start, end))
    assert result == [
        (datetime(1970, 1, 1, 8, 30), datetime(1970, 1, 1, 8, 59, 59, 999000)),
        (datetime(1970, 1, 1, 9, 0), datetime(1970, 1, 1, 9, 0, 0, 999000)),
    ]


def test_calculate_intervals_15m_8s_after_the_hour() -> None:
    start = dateutil.parser.parse("01/01/1970 08:30:00")
    end = dateutil.parser.parse("01/01/1970 09:00:08")

    result = list(calculate_intervals(start, end))
    assert result == [
        (datetime(1970, 1, 1, 8, 30), datetime(1970, 1, 1, 8, 59, 59, 999000)),
        (datetime(1970, 1, 1, 9, 0), datetime(1970, 1, 1, 9, 0, 7, 999000)),
    ]


def test_calculate_intervals_5h_15m_same_day() -> None:
    start = dateutil.parser.parse("01/01/1970 08:30:00")
    end = dateutil.parser.parse("01/01/1970 13:45:00")

    result = list(calculate_intervals(start, end))
    assert result == [
        (datetime(1970, 1, 1, 8, 30), datetime(1970, 1, 1, 8, 59, 59, 999000)),
        (datetime(1970, 1, 1, 9, 0), datetime(1970, 1, 1, 9, 59, 59, 999000)),
        (datetime(1970, 1, 1, 10, 0), datetime(1970, 1, 1, 10, 59, 59, 999000)),
        (datetime(1970, 1, 1, 11, 0), datetime(1970, 1, 1, 11, 59, 59, 999000)),
        (datetime(1970, 1, 1, 12, 0), datetime(1970, 1, 1, 12, 59, 59, 999000)),
        (datetime(1970, 1, 1, 13, 0), datetime(1970, 1, 1, 13, 44, 59, 999000)),
    ]


def test_calculate_intervals_5h_15m_next_day() -> None:
    start = dateutil.parser.parse("01/01/1970 21:30:00")
    end = dateutil.parser.parse("01/02/1970 02:45:00")

    result = list(calculate_intervals(start, end))
    assert result == [
        (datetime(1970, 1, 1, 21, 30), datetime(1970, 1, 1, 21, 59, 59, 999000)),
        (datetime(1970, 1, 1, 22, 0), datetime(1970, 1, 1, 22, 59, 59, 999000)),
        (datetime(1970, 1, 1, 23, 0), datetime(1970, 1, 1, 23, 59, 59, 999000)),
        (datetime(1970, 1, 2, 0, 0), datetime(1970, 1, 2, 0, 59, 59, 999000)),
        (datetime(1970, 1, 2, 1, 0), datetime(1970, 1, 2, 1, 59, 59, 999000)),
        (datetime(1970, 1, 2, 2, 0), datetime(1970, 1, 2, 2, 44, 59, 999000)),
    ]
