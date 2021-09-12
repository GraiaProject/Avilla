from dataclasses import dataclass


@dataclass
class BaseProfile:
    __annotations__ = {}

    @classmethod
    def get_ability_id(cls):
        return f"profile::{cls.__name__}"
