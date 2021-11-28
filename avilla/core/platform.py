from dataclasses import dataclass
from typing import Literal, Union


@dataclass(frozen=True)
class Platform:

    "对接的平台的名称"  # Tencent/QQ
    name: str

    "协议实现的名称"  # miraijvm, miraigo etc., use ',' or 'universal'
    protocol_provider_name: Union[str, Literal["universal"]]

    "对接平台使用的协议, 或者API的名称"  # OneBot
    implementation: str

    "对接平台的协议/API的版本"  # v11
    supported_impl_version: str

    "协议/API 的迭代版本"  # 11
    generation: str

    @property
    def universal_identifier(self) -> str:
        return (
            f"{self.name}/{self.protocol_provider_name}:{self.implementation}@{self.supported_impl_version}"
        )
