from src.allowlist import allowed, asset_names, policy_ids, priority


def test_check_if_in_policy():
    assert policy_ids == list(allowed.keys())
    assert asset_names == [next(iter(allowed[key])) for key in allowed]
    assert allowed[""].get(next(iter(allowed[""])), {}).get('priority', None) == priority("")
