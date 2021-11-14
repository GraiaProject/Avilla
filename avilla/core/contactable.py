from typing import Any, Dict, Generic, List, Tuple, TypeVar, Union

from pydantic.main import BaseModel

from .profile import BaseProfile

T = TypeVar("T", BaseProfile, Any)


class Contactable(Generic[T], BaseModel):
    id: str
    profile: T

    def __init__(self, id: str, profile: T):
        super().__init__(id=id, profile=profile)


class ref:
    path: List[Tuple[str, str]]

    def __init__(self, **type_and_endpoints: str) -> None:
        self.path = list(type_and_endpoints.items())

    def __repr__(self) -> str:
        return f"ref({', '.join([f'{_type, value}' for _type, value in self.path])})"

    def __truediv__(self, other: Union[str, "ref"]) -> "ref":
        if isinstance(other, str):
            _type, _, value = str.partition(other, ":")
            self.path.append((_type, value))
            return self
        elif isinstance(other, ref):
            self.path.extend(other.path)
            return self
        else:
            raise TypeError(
                f"unsupported operand type(s) for /: '{self.__class__.__name__}' and '{other.__class__.__name__}'"
            )

    def __getitem__(self, item: str) -> str:
        return self.mapping()[item]

    def __contains__(self, item: str) -> bool:
        return item in self.mapping()

    def mapping(self) -> Dict[str, str]:
        return dict(self.path)

    @classmethod
    def group(cls, _id: str):
        return cls(group=_id)

    @classmethod
    def member(cls, _id: str):
        return cls(member=_id)

    @classmethod
    def friend(cls, _id: str):
        return cls(friend=_id)

    @classmethod
    def stranger(cls, _id: str):
        return cls(stranger=_id)

    @classmethod
    def channel(cls, _id: str):
        return cls(channel=_id)

    @classmethod
    def server(cls, _id: str):
        return cls(server=_id)
