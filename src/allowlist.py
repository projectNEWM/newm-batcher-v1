"""
A Token that is allowed to be used as an incentive exists in the allowed
dictionary. Each entry has the same form as shown below.

"policy_id": {
    "asset_name": {
        "priority": priority_number,
        "threshold": threshold_number,
    }
}

The lower the priority number, the higher the priority. The threshold number
is in the base unit of the token.
"""
allowed = {
    # NEWM
    "682fe60c9918842b3323c43b5144bc3d52a23bd2fb81345560d73f63": {
        "4e45574d": {
            "priority": 0,
            "threshold": 10000000,
        },
    },
    # ADA
    "": {
        "": {
            "priority": 1,
            "threshold": 10000000,
        },
    },
}


def priority(pid: str) -> int:
    # assumes a policy id has a single token name
    return allowed[pid].get(next(iter(allowed[pid])), {}).get('priority', None)


policy_ids = list(allowed.keys())

asset_names = [next(iter(allowed[key])) for key in allowed]
