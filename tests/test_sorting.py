import pytest

from src.sorting import Sorting


@pytest.fixture
def single_sale_single_order():
    # (order hash, timestamp, tx idx, incentive)
    return {
        "acab": [("acab", 0, 0, 0, 0),]
    }


@pytest.fixture
def single_sale_fixed_incentive():
    # (order hash, timestamp, tx idx, incentive)
    return {
        "acab": [
            ("acab", 2, 4, 0, 0),
            ("acab", 0, 0, 0, 0),
            ("acab", 2, 0, 0, 0),
            ("acab", 2, 2, 0, 0),
            ("acab", 0, 1, 0, 0),
            ("acab", 1, 0, 0, 0),
        ]
    }


@pytest.fixture
def single_sale_variable_incentive():
    # (order hash, timestamp, tx idx, incentive)
    return {
        "acab": [
            ("acab", 2, 4, 4, 0),
            ("acab", 0, 0, 2, 0),
            ("acab", 2, 0, 1, 0),
            ("acab", 2, 2, 5, 0),
            ("acab", 0, 1, 1, 0),
            ("acab", 1, 0, 2, 0),
        ]
    }


@pytest.fixture
def single_sale_many_incentive():
    # (order hash, timestamp, tx idx, incentive)
    return {
        "acab": [
            ("acab", 2, 4, 4, 1),
            ("acab", 0, 0, 2, 0),
            ("acab", 2, 0, 1, 2),
            ("acab", 2, 2, 5, 0),
            ("acab", 0, 1, 1, 1),
            ("acab", 1, 0, 2, 0),
        ]
    }


def test_sort_empty_dict():
    result = Sorting.fifo_sort({})
    assert result == {}


def test_sort_single_dict(single_sale_single_order):
    result = Sorting.fifo_sort(single_sale_single_order)
    assert result == single_sale_single_order


def test_sort_fixed_incentive(single_sale_fixed_incentive):
    result = Sorting.fifo_sort(single_sale_fixed_incentive)
    answer = {
        "acab": [
            ("acab", 0, 0, 0, 0),
            ("acab", 0, 1, 0, 0),
            ("acab", 1, 0, 0, 0),
            ("acab", 2, 0, 0, 0),
            ("acab", 2, 2, 0, 0),
            ("acab", 2, 4, 0, 0),
        ]
    }
    assert result == answer


def test_sort_variable_incentive(single_sale_variable_incentive):
    result = Sorting.fifo_sort(single_sale_variable_incentive)
    answer = {
        "acab": [
            ("acab", 2, 2, 5, 0),
            ("acab", 2, 4, 4, 0),
            ("acab", 0, 0, 2, 0),
            ("acab", 1, 0, 2, 0),
            ("acab", 0, 1, 1, 0),
            ("acab", 2, 0, 1, 0),
        ]
    }
    assert result == answer


def test_sort_many_incentive(single_sale_many_incentive):
    result = Sorting.fifo_sort(single_sale_many_incentive)
    answer = {
        "acab": [
            ("acab", 2, 2, 5, 0),
            ("acab", 0, 0, 2, 0),
            ("acab", 1, 0, 2, 0),
            ("acab", 2, 4, 4, 1),
            ("acab", 0, 1, 1, 1),
            ("acab", 2, 0, 1, 2),
        ]
    }
    assert result == answer
