class ParamsUnmatched(Exception):
    """一个 text 没有被任何参数匹配成功"""


class InvalidOptionName(Exception):
    """option或subcommand的名字中填入了非法的字符"""


class NullName(Exception):
    """命令的名称写入了空字符"""


class InvalidFormatMap(Exception):
    """错误的格式化参数串"""


class NullTextMessage(Exception):
    """传入了不含有text的消息"""
