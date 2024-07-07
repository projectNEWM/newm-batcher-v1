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
            "threshold": 100_000_000,
        },
    },
    # tADA
    "": {
        "": {
            "priority": 1,
            "threshold": 100_000_000,
        },
    },
    # tDRIP
    "698a6ea0ca99f315034072af31eaac6ec11fe8558d3f48e9775aab9d": {
        "7444524950": {
            "priority": 2,
            "threshold": 100_000_000,
        },
    },
}


def priority(pid: str) -> int:
    # assumes a policy id has a single token name
    return allowed[pid].get(next(iter(allowed[pid])), {}).get('priority', None)


policy_ids = list(allowed.keys())

asset_names = [next(iter(allowed[key])) for key in allowed]
