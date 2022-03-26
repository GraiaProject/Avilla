from abc import ABCMeta, abstractmethod
import inspect
from typing import Any, Dict, Generic, List, Tuple, Type, TypeVar, Optional
from dataclasses import Field, dataclass
import stringcase

T = TypeVar("T")  # 返回值


class MetadataModifies(Generic[T]):
    metadata_type: Type["Metadata"]


M = TypeVar("M", bound=MetadataModifies)

SPECIALLISTS = {"modifies", "fields"}

EMPTY = object()


@dataclass
class MetaField:
    id: "str | ..." = ...
    annotation: Any = None
    default: Any = EMPTY
    attr: "str | None" = None

    def empty(self) -> bool:
        return self.default is EMPTY

class Metadata(Generic[M], metaclass=ABCMeta):
    @abstractmethod
    def modifies(self) -> M:
        pass

    @classmethod
    def fields(cls) -> List[MetaField]:
        fields = []
        annotations = getattr(cls, "__annotations__", {})
        _exists = set()
        for name, field in inspect.getmembers(cls):
            if not name.startswith("_") and not callable(field) and name not in SPECIALLISTS:
                common_id = f"{stringcase.snakecase(cls.__name__)}.{stringcase.snakecase(name)}"
                if not isinstance(field, MetaField):
                    field = MetaField(
                        id=common_id,
                        annotation=annotations.get(name, None),
                        default=field,
                        attr=name,
                    )
                else:
                    field.attr = name
                    field.id = field.id or common_id
                    field.annotation = field.annotation or annotations.get(name, None)
                fields.append(field)
                _exists.add(name)
        fields.extend(
            MetaField(
                id=f"{stringcase.snakecase(cls.__name__)}.{stringcase.snakecase(name)}",
                annotation=annotation,
                attr=name,
            )
            for name, annotation in annotations.items()
            if name not in SPECIALLISTS and name not in _exists
        )

        return fields

    @classmethod
    def from_fields(cls, mapping: Dict[str, Any]):
        instance = super().__new__(cls)
        field_settings = cls.fields()
        for field in field_settings:
            if not field.attr:
                raise KeyError(f"{field.id} cannot be referred to a real attribute of {cls.__name__}")
            override_value = mapping.get(field.id)
            if field.id in mapping:
                value = override_value
            elif field.default is EMPTY:
                raise ValueError(f"{field.id} is required")
            else:
                value = field.default
            setattr(instance, field.attr, value)
        return instance

    def __repr__(self) -> str:
        values = ", ".join(f"{k}={repr(v)}" for k, v in self.__dict__.items() if not k.startswith("_"))
        return f"{self.__class__.__name__}({values})"

class Member(Metadata):
    name: str
    budget: Optional[str]

    def modifies(self) -> M:
        pass


print(Member.fields())
print(
    Member.from_fields(
        {
            "member.name": "2342312",
            "member.budget": "2342312",
        }
    )
)
