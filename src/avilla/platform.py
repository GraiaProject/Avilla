from dataclasses import dataclass


@dataclass(frozen=True)
class Platform:

    "对接的平台的名称"  # Tencent/QQ
    name: str

    "协议实现的名称"  # miraijvm, miraigo etc.
    protocol_provider_name: str

    "对接平台使用的协议, 或者API的名称"  # OneBot
    implementation: str

    "对接平台的协议/API的版本"  # v11
    supported_impl_version: str

    "协议/API 的迭代版本"  # v11
    generation: str

    @property
    def universal_identifier(self) -> str:
        return f"{self.protocol_provider_name}@{self.name}/\
            {self.implementation.lower()}@({self.generation}/\
                {self.supported_impl_version})"
