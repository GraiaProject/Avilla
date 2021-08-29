import sys

if sys.version_info <= (3, 7):
    from typing_extensions import Protocol
else:
    from typing import Protocol


class AbilityDescriptionProtocol(Protocol):
    def has_ability(self, ability: str) -> bool:
        ...


class AbilityIdProtocol(Protocol):
    @classmethod
    def get_ability_id(cls) -> str:
        ...
