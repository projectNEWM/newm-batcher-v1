import json
from dataclasses import dataclass


@dataclass
class Value:
    inner: dict[str, dict[str, int]]

    def __str__(self):
        return f"Value({self.inner}"

    def __eq__(self, other):
        if not isinstance(other, Value):
            return NotImplemented
        return self.inner == other.inner

    def __add__(self, other):
        if not isinstance(other, Value):
            return NotImplemented
        for policy, assets in other.inner.items():
            if policy in self.inner:
                if isinstance(assets, dict):
                    # If both values are dictionaries, add their values
                    for asset, quantity in assets.items():
                        if asset in self.inner[policy]:
                            self.inner[policy][asset] += quantity
                        else:
                            self.inner[policy][asset] = quantity
                else:
                    # Otherwise its lovelace
                    self.inner[policy] += assets
            else:
                # If the key doesn't exist in the first dictionary, add it to the result
                self.inner[policy] = assets
        self._remove_zero_entries
        return Value(self.inner)

    def dump(self) -> str:
        return json.dumps(self.inner)

    def exists(self, policy) -> bool:
        if not isinstance(policy, str):
            return NotImplemented
        return policy in self.inner

    def contains(self, other) -> bool:
        """
        Checks if other is at least contained inside of self.
        """
        if not isinstance(other, Value):
            return NotImplemented
        for policy, assets in other.inner.items():
            if policy not in self.inner:
                return False
            if isinstance(assets, dict):
                for asset, quantity in assets.items():
                    if self.inner[policy][asset] < quantity:
                        return False
            else:
                if self.inner[policy] < assets:
                    return False
        return True

    def _remove_zero_entries(self):
        """
        Removes zero entries from self.
        """
        inner_copy = self.inner.copy()  # create a copy so we can delete
        for policy, assets in inner_copy.items():
            if isinstance(assets, dict):
                # this is for tokens
                assets_to_remove = [asset for asset, amount in assets.items() if amount == 0]
                for asset in assets_to_remove:
                    del self.inner[policy][asset]
            else:
                # this is lovelace
                if inner_copy[policy] == 0:
                    del self.inner[policy]
