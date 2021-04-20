import os
import dotenv
from ast import literal_eval
from django.conf import settings

__loaded = False


def get_var(name, is_string: bool = True, default=None):
    """
    get environment variable
    :param name: 变量名
    :param is_string: 是否返回原字符串，如果否则尝试evaluate值
    :default: 默认值，如果不提供且变量name不存在，报错
    """
    if is_string and default is not None:
        assert isinstance(default, str), "default must be a string"
    global __loaded
    if not __loaded:
        dotenv.load_dotenv(encoding='utf-8', dotenv_path=dotenv.find_dotenv(usecwd=settings.BASE_DIR))
        __loaded = True
    value = os.environ.get(name)
    if not value:
        if default is None:
            raise ValueError(f'"{name}" is not set. Please check your .env file.')
        return default
    if is_string:
        return value
    try:
        return literal_eval(value)
    except (ValueError, SyntaxError):
        raise ValueError(f'Cannot evaluate "{name}" (value: {value})')
