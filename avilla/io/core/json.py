from json import loads
from pathlib import Path
from typing import TYPE_CHECKING, Any, Type, Union

from avilla.core.config import ConfigProvider, TModel

if TYPE_CHECKING:
    from avilla.core import Avilla


class json_provide(ConfigProvider[TModel]):
    def __init__(self, config_file: Union[Path, str], raw_path: bool = False, json_loader=loads) -> None:
        self.config_file = config_file
        self.raw_path = raw_path
        self.json_loader = json_loader

    async def provide(self, avilla: "Avilla", config_model: Type[TModel], scope: Any):
        avilla_conf = avilla.get_config(avilla)
        if not avilla_conf:
            raise RuntimeError("Avilla config is not ready...maybe you deleted it on your own? it's too bad.")
        if not self.raw_path:
            path = avilla_conf.default_local_config_path.joinpath(self.config_file)
        else:
            if isinstance(self.config_file, Path):
                path = self.config_file
            else:
                path = Path(self.config_file)
        if not path.exists():
            raise FileNotFoundError(f"{path} not found.")
        self.config = config_model.parse_obj(self.json_loader(path.read_text()))
