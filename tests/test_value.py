import json

from src.value import Value


def test_remove_zeros():
    result = Value({"lovelace": 0, "acab": {"beef": 1, "face": 0}})
    answer = Value({"acab": {"beef": 1}})
    result._remove_zero_entries()
    assert result == answer


def test_remove_zeros2():
    result = Value({"lovelace": 0, "acab": {"face": 0}})
    answer = Value({})
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
    answer = Value({})
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


def test_value_contains_exact():
    v1 = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
    v2 = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
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


def test_add_lovelace():
    result = Value({})
    answer = Value({"lovelace": 1})
    result.add_lovelace(1)
    assert result == answer


def test_add_lovelace_to_empty():
    v1 = Value({})
    v2 = Value({"lovelace": 1})
    answer = Value({"lovelace": 1})
    result = v1 + v2
    assert result == answer


def test_get_token():
    v1 = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
    tkn = v1.get_token("acab")
    assert tkn == "beef"


def test_to_output_only_lovelace():
    addr = "addr"
    v1 = Value({"lovelace": 3})
    answer = "addr + 3"
    assert v1.to_output(addr) == answer


def test_to_output():
    addr = "addr"
    v1 = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
    answer = "addr + 3 + 2 acab.beef + 1 cafe.fade"
    assert v1.to_output(addr) == answer


def test_does_not_meet_threshold():
    v1 = Value({"lovelace": 2})
    assert v1.meets_threshold() is False


def test_empty_does_not_meet_threshold():
    v1 = Value({})
    assert v1.meets_threshold() is False


def test_does_meet_threshold():
    v1 = Value({"lovelace": 100_000_000})
    assert v1.meets_threshold() is True


def test_subtract_tokes():
    v1 = Value({'20053b53f8f381892dc2fe8a2562f6b4a2fe076143b7d9c6558c98f9': {'5ca1ab1e000affab1e000ca11ab1e0005e77ab1e': 1}, '769c4c6e9bc3ba5406b9b89fb7beb6819e638ff2e2de63f008d5bcff': {'744e45574d': 100000000}, 'lovelace': 129617739})
    v2 = Value({'lovelace': 5000000, '20053b53f8f381892dc2fe8a2562f6b4a2fe076143b7d9c6558c98f9': {'5ca1ab1e000affab1e000ca11ab1e0005e77ab1e': 1}})
    v3 = Value({'lovelace': 350000})
    answer = Value({'769c4c6e9bc3ba5406b9b89fb7beb6819e638ff2e2de63f008d5bcff': {'744e45574d': 100000000}, 'lovelace': 124267739})
    assert answer == v1 - v2 - v3


def test_sub_lovelace_together():
    v1 = Value({"acab": {"cafe": 1}})
    v2 = Value({"acab": {"cafe": 1}})
    answer = Value({})
    v = v1 - v2
    assert v == answer


def test_multiply_by_one():
    v1 = Value({"acab": {"cafe": 1}})
    assert 1 * v1 == v1
    assert v1 * 1 == v1


def test_multiple_by_two():
    v1 = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
    answer = Value({"lovelace": 6, "acab": {"beef": 4}, "cafe": {"fade": 2}})
    assert 2 * v1 == answer
    assert v1 * 2 == answer


def test_has_no_negative_values():
    v1 = Value({"lovelace": 3, "acab": {"beef": 2}, "cafe": {"fade": 1}})
    assert v1.has_negative_entries() is False


def test_has_negative_values():
    v1 = Value({"lovelace": 3, "acab": {"beef": -2}, "cafe": {"fade": 1}})
    assert v1.has_negative_entries() is True
