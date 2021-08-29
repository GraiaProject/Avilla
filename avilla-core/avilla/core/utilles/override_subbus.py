from typing import Any, Dict, Type

from avilla.core.execution import Execution
from avilla.core.protocol import BaseProtocol


def proto_ensure_exec_params(execution):
    return {"execution": execution}


def network_method_subbus(proto: BaseProtocol, params: Dict[str, Any]) -> str:
    if "ws" in proto.using_networks:
        return "ws"
    elif "http" in proto.using_networks:
        return "http"
    return "http"


def execution_subbus(proto: BaseProtocol, params: Dict[str, Any]) -> Type[Execution]:
    return params["execution"].__class__
