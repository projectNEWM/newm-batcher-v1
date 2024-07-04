from dataclasses import dataclass


@dataclass
class Value:
    inner: dict[str, dict[str, int]]

    def __str__(self):
        return f"Value({self.inner}"
