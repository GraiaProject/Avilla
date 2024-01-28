from __future__ import annotations

from itertools import cycle
from typing import Any, Generic, Iterable, MutableMapping, MutableSequence, TypeVar
from typing_extensions import Self

from .layout import DetailedArtifacts, LayoutT

T = TypeVar("T")
S = TypeVar("S")
E = TypeVar("E")
K = TypeVar("K")


class Topic(Generic[T]):
    def merge(self, inbound: MutableSequence[T], outbound: MutableSequence[T]) -> None:
        ...

    def new_record(self) -> T:
        ...


class PileTopic(Generic[T, S, E], Topic[T]):
    def iter_entities(self, record: T) -> MutableMapping[S, E]:
        ...

    def has_entity(self, record: T, signature: S) -> bool:
        ...

    def get_entity(self, record: T, signature: S) -> E:
        ...

    def flatten_record(self, record: T, target: T) -> None:
        ...

    def flatten_entity(self, record: T, signature: S, entity: E, replacement: E | None) -> None:
        ...

    def merge(self, inbound: list[T], outbound: list[DetailedArtifacts[Self, T]]) -> None:
        outbound_depth = len(outbound)

        grouped: dict[S, list[tuple[T, E] | None]] = {}
        record_update_tasks = []

        for record in inbound:
            for identity, entity in self.iter_entities(record).items():
                if identity in grouped:
                    group = grouped[identity]
                else:
                    group = grouped[identity] = []

                group.append((record, entity))

        for identity, group in grouped.items():
            outbound_index = 0
            for group_index in cycle(range(len(group))):
                twin = group[group_index]

                if twin is None:
                    break

                record, entity = twin

                if outbound_index == outbound_depth:
                    v = DetailedArtifacts({self: self.new_record()})
                    outbound.insert(outbound_index, v)
                    outbound_depth += 1
                else:
                    v = outbound[outbound_index]

                if self not in v:
                    v[self] = self.new_record()

                target_record = v[self]

                if self.has_entity(target_record, identity):
                    e = self.get_entity(target_record, identity)
                    group[group_index] = (target_record, e)
                    record_update_tasks.append((lambda x, y: lambda: self.flatten_record(x, y))(record, target_record))
                    self.flatten_entity(target_record, identity, entity, e)
                else:
                    group[group_index] = None
                    self.flatten_entity(target_record, identity, entity, None)

                outbound_index += 1

        for i in record_update_tasks[::-1]:
            i()


def merge_topics_if_possible(
    inbounds: Iterable[MutableMapping[Any, Any] | DetailedArtifacts[Any, Any]],
    outbound: LayoutT,
    *,
    replace_non_topic: bool = True,
) -> None:
    for index, value in enumerate(outbound):
        if not isinstance(value, DetailedArtifacts) or value.protected:
            outbound_depth = index
            break
    else:
        outbound_depth = len(outbound)

    protected = outbound[outbound_depth:]
    outbound[outbound_depth:] = []

    topic_pair_records: dict[Topic, list[Any]] = {}

    done_replace = set()

    for pairs in inbounds:
        for maybe_topic, record in pairs.items():
            if isinstance(maybe_topic, Topic):
                if maybe_topic not in topic_pair_records:
                    pair_v = topic_pair_records[maybe_topic] = []
                else:
                    pair_v = topic_pair_records[maybe_topic]

                pair_v.append(record)
            elif replace_non_topic and maybe_topic not in done_replace:
                if not isinstance(outbound[0], MutableMapping):
                    outbound.insert(0, DetailedArtifacts())
                outbound[0][maybe_topic] = record  # type: ignore
                done_replace.add(maybe_topic)

    for topic, records in topic_pair_records.items():
        topic.merge(records, outbound)

    outbound.extend(protected)
