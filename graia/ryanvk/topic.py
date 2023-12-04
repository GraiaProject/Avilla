from __future__ import annotations

from itertools import cycle
from typing import Any, Generic, Iterable, MutableMapping, TypeVar

from typing_extensions import Self

T = TypeVar("T")
S = TypeVar("S")
E = TypeVar("E")
K = TypeVar("K")


class Topic(Generic[T]):
    def merge(self, inbound: list[T], outbound: list[T]) -> None:
        ...

    def new_record(self) -> T:
        ...


class PileTopic(Generic[T, S, E], Topic[T]):
    def iter_entities(self, record: T) -> MutableMapping[S, E]:
        ...

    def insist_objects(self, record: T) -> Iterable[Any]:
        ...

    def has_entity(self, record: T, signature: S) -> bool:
        ...

    def get_entity(self, record: T, signature: S) -> E:
        ...

    def flatten_record(self, record: T, target: T) -> None:
        ...

    def flatten_entity(self, record: T, signature: S, entity: E, replacement: E | None) -> None:
        ...

    def merge(self, inbound: list[T], outbound: list[MutableMapping[Self, T]]) -> None:
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
            # identity: 标记 entity 用的，对于 fn 的情况，就是 overload 的 harvest 了
            # group: list[E]
            outbound_index = 0
            for group_index in cycle(range(len(group))):
                twin = group[group_index]

                if twin is None:
                    break

                record, entity = twin

                if outbound_index == outbound_depth:
                    outbound_depth += 1
                    outbound.append({self: self.new_record()})

                if self not in outbound[outbound_index]:
                    outbound[outbound_index][self] = self.new_record()

                target_record = outbound[outbound_index][self]

                if self.has_entity(target_record, identity):
                    e = self.get_entity(target_record, identity)
                    group[group_index] = (target_record, e)
                    # FIXME: flatten_record 会把副作用加在 target_record 上，这会覆盖掉 group 内部缓存的同一个 target_record，
                    #        导致后面的 flatten_record 行为不是我们想要的。
                    #        我想这个应该可以缓存住，然后我全部干完了再说……似乎也不行，至少正序的不行，那么逆序的情况呢？
                    #        回去再说吧，至少你没用上 deepcopy。
                    # TODO: 显然，我们需要对这一部分进行 review。
                    record_update_tasks.append((lambda x, y: lambda: self.flatten_record(x, y))(record, target_record))
                    self.flatten_entity(target_record, identity, entity, e)
                else:
                    group[group_index] = None
                    self.flatten_entity(target_record, identity, entity, None)

                outbound_index += 1

        for i in record_update_tasks[::-1]:
            i()


def merge_topics_if_possible(
    inbounds: list[MutableMapping[Any, Any]],
    outbound: list[MutableMapping[Any, Any]],
    *,
    replace_non_topic: bool = True,
) -> None:
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
                outbound[0][maybe_topic] = record
                done_replace.add(maybe_topic)

    for topic, records in topic_pair_records.items():
        if topic not in outbound[0]:
            outbound[0][topic] = topic.new_record()

        topic.merge(records, outbound)
