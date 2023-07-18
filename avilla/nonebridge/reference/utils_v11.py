"""OneBot v11 杂项。

FrontMatter:
    sidebar_position: 9
    description: onebot.v11.utils 模块
"""

from typing import Any, Dict, Optional

from nonebot.utils import logger_wrapper

from .exception import ActionFailed

log = logger_wrapper("OneBot V11")


def handle_api_result(result: Optional[Dict[str, Any]]) -> Any:
    """处理 API 请求返回值。

    参数:
        result: API 返回数据

    返回:
        API 调用返回数据

    异常:
        ActionFailed: API 调用失败
    """
    if isinstance(result, dict):
        if result.get("status") == "failed":
            raise ActionFailed(**result)
        return result.get("data")
