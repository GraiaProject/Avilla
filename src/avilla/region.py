from dataclasses import dataclass

_REGIONS = {}


class Region:
    name: str

    def __new__(cls, name: str) -> "Region":
        if name in _REGIONS:
            return _REGIONS[name]
        result = super().__new__(cls)
        result.name = name
        _REGIONS[name] = result
        return result
