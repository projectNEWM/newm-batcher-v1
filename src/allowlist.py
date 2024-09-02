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
    # tNEWM
    "769c4c6e9bc3ba5406b9b89fb7beb6819e638ff2e2de63f008d5bcff": {
        "744e45574d": {
            "priority": 0,
            "threshold": 10000000,
        },
    },
    # tADA
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
