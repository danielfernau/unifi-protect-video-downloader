from datetime import datetime

from .utils import calculate_intervals


def test_calculate_intervals():
    start = datetime(2020, 1, 8, 23, 0, 0)
    end = datetime(2020, 1, 9, 0, 0, 0)

    result = list(calculate_intervals(start, end))
    assert result == [
        (datetime(2020, 1, 8, 23, 0, 0), datetime(2020, 1, 8, 23, 59, 59)),
    ]
