import json

from src.value import Value


def test_remove_zeros():
    result = Value({"lovelace": 0, "acab": {"beef": 1, "face": 0}})
    answer = Value({"acab": {"beef": 1}})
    result._remove_zero_entries()
    assert result == answer


def test_remove_zeros_into_empty():
    result = Value({"lovelace": 0})
    answer = Value({})
    result._remove_zero_entries()
    assert result == answer


def test_add_lovelace_together():
    v1 = Value({"lovelace": 1})
    v2 = Value({"lovelace": 1})
    answer = Value({"lovelace": 2})
    v = v1 + v2
    assert v == answer


def test_add_lovelace_together_into_empty():
    v1 = Value({"lovelace": 1})
    v2 = Value({"lovelace": -1})
    answer = Value({"lovelace": 0})
    v = v1 + v2
    assert v == answer


def test_add_multiple_lovelace_together():
    v1 = Value({"lovelace": 1})
    v2 = Value({"lovelace": 1})
    v3 = Value({"lovelace": 1})
    answer = Value({"lovelace": 3})
    v = v1 + v2 + v3
    assert v == answer


def test_add_values_together():
    v1 = Value({"lovelace": 1, "acab": {"beef": 1}})
    v2 = Value({"lovelace": 1, "cafe": {"fade": 1}})
    v3 = Value({"lovelace": 1, "acab": {"beef": 1}})
    answer = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
    v = v1 + v2 + v3
    assert v == answer


def test_value_contains_in_value():
    v1 = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
    v2 = Value({"lovelace": 1, "acab": {"beef": 1}})
    assert v1.contains(v2)


def test_value_not_contains_in_value():
    v2 = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
    v1 = Value({"lovelace": 1, "acab": {"beef": 1}})
    assert v1.contains(v2) is False


def test_if_policy_does_exists():
    v1 = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
    assert v1.exists("acab")


def test_if_policy_doesnt_exists():
    v1 = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
    assert v1.exists("fade") is False


def test_value_dump():
    v1 = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
    v1_dump = json.dumps(v1.inner)
    assert v1.dump() == v1_dump