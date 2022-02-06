from datetime import datetime

from .utils import calculate_intervals


def test_calculate_intervals_single_result() -> None:
    start = datetime(2020, 1, 8, 23, 0, 0)
    end = datetime(2020, 1, 9, 0, 0, 0)

    result = list(calculate_intervals(start, end))
    assert result == [
        (datetime(2020, 1, 8, 23, 0, 0), datetime(2020, 1, 8, 23, 59, 59)),
    ]


def test_calculate_intervals_multiple_partial() -> None:
    start = datetime(2020, 1, 8, 23, 0, 0)
    end = datetime(2020, 1, 9, 2, 30, 0)

    result = list(calculate_intervals(start, end))
    assert result == [
        (datetime(2020, 1, 8, 23, 0, 0), datetime(2020, 1, 8, 23, 59, 59)),
        (datetime(2020, 1, 9, 0, 0), datetime(2020, 1, 9, 0, 59, 59)),
        (datetime(2020, 1, 9, 1, 0), datetime(2020, 1, 9, 1, 59, 59)),
        (datetime(2020, 1, 9, 2, 0), datetime(2020, 1, 9, 2, 29, 59)),
    ]
