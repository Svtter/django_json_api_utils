import json
from functools import partial
from functools import wraps
from django.http import HttpRequest
from djapi.error import ProjectError
from django.core.exceptions import TooManyFieldsSent

__all__ = ['get_param_value', 'get_json_field', 'get_multipart_field',
           'param_field_getter', 'json_field_getter',
           'multipart_getter', 'require_methods_api', 'require_GET_api',
           'require_DELETE_api', 'require_PATCH_api',
           'require_POST_api', 'require_PUT_api']


def _get_type_name(class_type):
    if class_type == str:
        return 'string'
    if class_type == int:
        return 'integer'
    if class_type == float:
        return 'float'
    if class_type == bool:
        return 'boolean'
    if class_type == object:
        return 'object'
    if class_type == list:
        return 'array'

    return str(class_type)


def get_json_field(request, field, required_type=object, allow_empty=False, allowed_values=None,
                   default=None):
    """
    获取JSON中的字段值，若发生错误则终止响应
    :param request: HttpRequest
    :param field: JSON字段名
    :param required_type: 要求的数据类型，python类，例如int， dict， list，str
    :param allow_empty: 是否可以为null或者为空白
    :param allowed_values: field的可取值范围，为一个list或元组，field只能选取中的值。为None或者空时不限制取值
    :param default: 如果field不存在时的默认值
    :return: 字段的值
    """
    attr = '__project_json_data__'
    if not hasattr(request, attr):
        json_data = {}
        try:
            if request.content_type != 'application/json':
                raise TypeError
            if request.body:
                json_data = json.loads(request.body)
                if not isinstance(json_data, dict):
                    raise ProjectError.NOT_ACCEPTABLE("Request body must be a valid json object")
        except TypeError:
            raise ProjectError.NOT_ACCEPTABLE("Content-Type must be application/json")
        except json.JSONDecodeError:
            raise ProjectError.NOT_ACCEPTABLE("Invalid json object")
    else:
        json_data = getattr(request, attr)
    value = json_data.get(field)
    if isinstance(value, (dict, list, str)) and not value and not allow_empty:
        if isinstance(value, required_type):
            value = None  # 空白值也认为是None
    if value is None:
        if not allow_empty:
            raise ProjectError.FIELD_MISSING(f"Field {field} is either missing or empty")
        return default
    else:
        if isinstance(value, int) and required_type == float:
            value = float(value)
        if isinstance(value, required_type):
            if allowed_values:
                if value not in allowed_values:
                    allowed_values_msg = ", ".join(map(lambda x: str(x), allowed_values))
                    msg = f'Value of field "{field}" should be one of [{allowed_values_msg}]'
                    raise ProjectError.INVALID_FIELD_VALUE(msg)

            return value
        raise ProjectError.WRONG_FIELD_TYPE(f'Field "{field}" should be {_get_type_name(required_type)}')


def json_field_getter(request: HttpRequest):
    """
    :param
    request: HttpRequest对象
    """

    return partial(get_json_field, request)


def get_multipart_field(request: HttpRequest, field, required_type=bytes, allow_empty=False, allowed_values=None,
                        default=None):
    """
    获取multipart/form-data中的字段值，若发生错误则终止响应

    :param request: HttpRequest
    :param field: JSON字段名
    :param required_type: 要求的数据类型，可以是int, str, list, float和bytes
    :param allow_empty: 是否可以为null或者为空白
    :param allowed_values: 可选值，如果不为空则value只能是此列表中指定的值，否则报错
    :param default: 默认值
    :return: 字段的值
    """
    try:
        if required_type not in (int, str, list, float, bytes):
            raise TypeError(f"{_get_type_name(required_type)} is not supported")
        if required_type == list and allowed_values:
            raise TypeError('Cannot use "allowed_values" when required_type is list')
        if not request.content_type.startswith('multipart/form-data'):
            raise ProjectError.NOT_ACCEPTABLE("Content-Type must be multipart/form-data")
        if required_type == bytes:
            value = request.FILES.get(field)
        elif required_type == list:
            value = request.POST.getlist(field)
            if not value and not allow_empty:
                value = None
        else:
            value = request.POST.get(field)
            if not value:
                value = None
        if value is None and not allow_empty:
            raise ProjectError.FIELD_MISSING(f'field "{field}" is missing')
        elif value is None and allow_empty:
            return default
        if required_type not in (list, bytes):
            try:
                value = required_type(value)
                if allowed_values is not None and value not in allowed_values:
                    msg = f'Value of field "{field}" should be one of [{",".join(allowed_values)}].'
                    raise ProjectError.INVALID_FIELD_VALUE(msg)
            except (ValueError, TypeError):
                raise ProjectError.WRONG_FIELD_TYPE(f'Field "{field}" should be {_get_type_name(required_type)}.')
            return value
        return value
    except TooManyFieldsSent:
        raise ProjectError.UNPROCESSABLE("Too many fields sent")


def multipart_getter(request: HttpRequest):
    return partial(get_multipart_field, request)


def get_param_value(request: HttpRequest, field: str, allow_empty=True, allowed_values=None, required_type=None,
                    default=None):
    """
    Get URL parameters from HttpRequest
    :param request: HttpRequest
    :param field: field name
    :param allow_empty:
    :param allowed_values: a list or a tuple of values
    :param required_type: cast the value to this type
    :param default:
    """

    value = request.GET.get(field)
    if default is not None and required_type:
        assert isinstance(default, required_type)
    if not value:
        value = None
    if required_type:
        assert required_type in (int, float, bool)
        if value is not None:
            try:
                if required_type is bool:
                    value = value == str('true')
                else:
                    value = required_type(value)
            except (TypeError, ValueError):
                raise ProjectError.WRONG_FIELD_TYPE(f'Field "{field}" must be {_get_type_name(required_type)}')

    if value is None:
        if allow_empty:
            return default
        raise ProjectError.FIELD_MISSING(f"Field {field} is either missing of empty")
    elif allowed_values is not None and value not in allowed_values:
        choices = ", ".join(map(lambda x: str(x), allowed_values))
        msg = f"""Value of field {field} can only be one of [{choices}], but {value} was given."""
        raise ProjectError.INVALID_FIELD_VALUE(msg)
    else:
        return value


def param_field_getter(request: HttpRequest):
    return partial(get_param_value, request)


def require_methods_api(request_methods_list):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method not in request_methods_list:
                raise ProjectError.METHOD_NOT_ALLOWED(f"不允许{request.method}方法")
            return func(request, *args, **kwargs)

        return inner

    return decorator


require_GET_api = require_methods_api(["GET"])
require_POST_api = require_methods_api(["POST"])
require_PATCH_api = require_methods_api(["PATCH"])
require_PUT_api = require_methods_api(["PUT"])
require_DELETE_api = require_methods_api(["DELETE"])
