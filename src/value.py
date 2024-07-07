import json
from dataclasses import dataclass

from src.allowlist import allowed


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

    def __mul__(self, scale):
        if not isinstance(scale, int):
            return NotImplemented
        for policy, assets in self.inner.items():
            if isinstance(assets, dict):
                for asset, quantity in assets.items():
                    self.inner[policy][asset] = quantity * scale
            else:
                self.inner[policy] = assets * scale

    def __rmul__(self, other):
        return self.__mul__(other)

    def meets_threshold(self):
        for pid in allowed:
            for tkn in allowed[pid]:
                threshold = allowed[pid][tkn]["threshold"]
                if self.get_quantity(pid, tkn) >= threshold:
                    return True
        return False

    def to_output(self, address):
        if not isinstance(address, str):
            return NotImplemented

        lovelace_value = str(self.inner['lovelace'])

        # Get the values of the nested dictionary and combine them into a string
        nested_dict_values = []
        for policy, assets in self.inner.items():
            if policy != 'lovelace':
                for asset, quantity in assets.items():
                    nested_dict_values.append(f"{quantity} {policy}.{asset}")

        # just add in the lovelace else do the assets too
        if len(nested_dict_values) == 0:
            # combine the address with the lovelace amount
            return address + " + " + lovelace_value
        else:
            nested_dict_values = " + ".join(nested_dict_values)
            # Combine the address with the lovelace and the dictionary values
            return address + " + " + lovelace_value + " + " + nested_dict_values

    def add_lovelace(self, quantity):
        if not isinstance(quantity, int):
            return NotImplemented
        self.inner["lovelace"] = quantity

    def get_token(self, policy):
        if not isinstance(policy, str):
            return NotImplemented
        return list(self.inner[policy].keys())[0]

    def get_quantity(self, policy, asset):
        if not isinstance(policy, str):
            return NotImplemented
        if not isinstance(asset, str):
            return NotImplemented
        return self.inner[policy][asset]

    def dump(self) -> str:
        """
        Do a json dumps of the self.
        """
        return json.dumps(self.inner)

    def exists(self, policy) -> bool:
        """
        Checks if a policy exists in self.
        """
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
