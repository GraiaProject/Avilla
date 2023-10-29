from __future__ import annotations

from avilla.core import Resource, Selector


class TelegramResource(Resource[bytes]):
    file_id: str
    file_unique_id: str
    file_size: int | None = None

    def __init__(self, file_id: str, file_unique_id: str, file_size: int | None = None):
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.file_size = file_size

    @property
    def selector(self) -> Selector:
        return (
            Selector()
            .land("telegram")
            .file_id(str(self.file_id))
            .file_unique_id(str(self.file_unique_id))
            .file_size(str(self.file_size))
        )
