import inspect
from contextvars import ContextVar
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    List,
    NoReturn,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from graia.broadcast.typing import T_Dispatcher
from graia.broadcast.utilles import dispatcher_mixin_handler
from pydantic.typing import DictStrAny

T = TypeVar("T")


def gen_subclass(cls: Type[T]) -> Generator[Type[T], None, None]:
    """生成某个类的所有子类 (包括其自身)

    Args:
        cls (Type[T]): 类

    Yields:
        Type[T]: 子类
    """
    yield cls
    for sub_cls in cls.__subclasses__():
        if TYPE_CHECKING:
            assert issubclass(sub_cls, cls)
        yield from gen_subclass(sub_cls)


def const_call(val: T) -> Callable[[], T]:
    """生成一个返回常量的 Callable

    Args:
        val (T): 常量

    Returns:
        Callable[[], T]: 返回的函数
    """
    return lambda: val


def assert_on_(pre_condition: Union[bool, Any], condition: bool, *message: Any) -> Union[None, NoReturn]:
    """检查条件是否成立, 如果不成立则抛出 ValueError

    Args:
        pre_condition (bool): 前置条件
        condition (bool): 条件语句
        message (Any, optional): 附带的消息.

    Returns:
        Union[None, NoReturn]: 无返回值
    """
    if pre_condition:
        if not condition:
            raise ValueError(*message)


def assert_(condition: bool, *message: Any) -> Union[None, NoReturn]:
    """引发 ValueError 的断言

    Args:
        condition (bool): 条件语句
        *message (Any): 附带的消息.

    Returns:
        Union[None, NoReturn]: 无返回值
    """
    if not condition:
        raise ValueError(*message)


def assert_not_(condition: bool, *message: Any) -> Union[None, NoReturn]:
    """检查条件是否成立, 如果不成立则抛出 ValueError

    Args:
        condition (bool): 条件语句
        *message (Any): 附带的消息.

    Returns:
        Union[None, NoReturn]: 无返回值
    """
    if condition:
        raise ValueError(*message)


def eval_ctx(
    layer: int = 0, globals_: Optional[DictStrAny] = None, locals_: Optional[DictStrAny] = None
) -> Tuple[DictStrAny, DictStrAny]:
    """获取一个上下文的全局和局部变量

    Args:
        layer (int, optional): 层数. Defaults to 0.
        globals_ (Optional[DictStrAny], optional): 全局变量. Defaults to None.
        locals_ (Optional[DictStrAny], optional): 局部变量. Defaults to None.

    Returns:
        Tuple[DictStrAny, DictStrAny]: 全局和局部变量字典.
    """
    frame = inspect.stack()[layer + 1].frame  # add the current frame
    global_dict, local_dict = frame.f_globals, frame.f_locals
    global_dict.update(globals_ or {})
    local_dict.update(locals_ or {})
    return global_dict, local_dict


def resolve_dispatchers_mixin(dispatchers: List[T_Dispatcher]) -> List[T_Dispatcher]:
    """解析 dispatcher list 的 mixin

    Args:
        dispatchers (List[T_Dispatcher]): dispatcher 列表

    Returns:
        List[T_Dispatcher]: 解析后的 dispatcher 列表
    """
    result = []
    for dispatcher in dispatchers:
        result.extend(dispatcher_mixin_handler(dispatcher))
    return result


class ConstantDispatcher(BaseDispatcher):
    """分发常量给指定名称的参数"""

    def __init__(self, context: ContextVar[Dict[str, Any]]) -> None:
        self.ctx_var = context

    async def catch(self, interface: DispatcherInterface):
        content = self.ctx_var.get()
        if interface.name in content:
            return content[interface.name]
