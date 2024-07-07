from src.redeemer import empty


def test_zeroth_empty_redeemer():
    index = 0
    result = empty(index)
    assert isinstance(result, dict)
    assert len(result) == 2
    assert result["constructor"] == index
    assert result["fields"] == []
