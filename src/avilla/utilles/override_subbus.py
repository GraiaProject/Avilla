from typing import Any, Dict, Type

from avilla.execution import Execution
from avilla.protocol import BaseProtocol


def proto_ensure_exec_params(relationship, execution):
    return {"relationship": relationship, "execution": execution}


def network_method_subbus(proto: BaseProtocol, params: Dict[str, Any]) -> str:
    if "ws" in proto.using_networks:
        return "ws"
    elif "http" in proto.using_networks:
        return "http"
    return "http"


def execution_subbus(proto: BaseProtocol, params: Dict[str, Any]) -> Type[Execution]:
    return params["execution"].__class__
