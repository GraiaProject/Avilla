from dataclasses import dataclass


@dataclass
class BaseProfile:
    @classmethod
    def get_ability_id(cls):
        return f"profile::{cls.__name__}"
