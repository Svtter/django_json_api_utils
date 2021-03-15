import json
import os
import random
import string
from tempfile import mkdtemp as python_mkdtemp
from datetime import datetime
from functools import wraps
from django.utils import timezone
from django.http import HttpResponse, HttpRequest
from ..error import ProjectError, ProjectException, abort_response
from django.conf import settings


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


def json_response(data=None, msg: str = '', status_code: int = 200, **kwargs) -> HttpResponse:
    """
    将字典数据转为JSON返回
    :param data: 需要返回的数据
    :param msg: 提示消息
    :param status_code: req 状态码，默认 200
    :param kwargs: 附加信息，直接嵌入JSON第一级
    """
    result = {'code': ProjectError.SUCCESS, msg: ProjectError.SUCCESS.error_message,
              'data': data}
    if msg:
        result['msg'] = msg
    if kwargs:
        result.update(kwargs)
    return HttpResponse(json.dumps(result, ensure_ascii=False),
                        content_type='application/json; charset=utf-8',
                        status=status_code)


def get_json_field(request: HttpRequest, field, required_type=object, allow_empty=False, allowed_values=None,
                   default=None):
    """
    获取JSON中的字段值，若发生错误则终止响应

    :param request: HttpRequest对象
    :param field: JSON字段名
    :param required_type: 要求的数据类型，python类，例如int， dict， list，str
    :param allow_empty: 是否可以为null或者为空白
    :param allowed_values: field的可取值范围，为一个list或元组，field只能选取中的值。为None或者空时不限制取值
    :param default: 如果field不存在时的默认值
    :return: 字段的值
    """

    attr = '__Project_json_data'
    json_data = {}
    if hasattr(request, attr):
        json_data = getattr(request, attr)
    else:
        try:
            json_data = json.loads(request.body)
            if not isinstance(json_data, dict):
                raise TypeError
            setattr(request, attr, json_data)
        except (json.JSONDecodeError, TypeError):
            abort_response(ProjectError.NOT_ACCEPTABLE("Content-Type必须为application/json"))

    value = json_data.get(field)
    if isinstance(value, (dict, list, str)) and not value and not allow_empty:
        if isinstance(value, required_type):
            value = None  # 空白值也认为是None
    if value is None:
        if not allow_empty:
            abort_response(ProjectError.FIELD_MISSING,
                           error_detail=f"字段{field}缺失或者值为空")
        return default
    elif isinstance(value, required_type):
        if allowed_values:
            if value not in allowed_values:
                msg = f'字段"{field}"的值只能是[{", ".join(map(lambda x: str(x), allowed_values))}]之一'
                abort_response(ProjectError.INVALID_FIELD_VALUE, error_detail=msg)

        return value
    else:
        abort_response(ProjectError.WRONG_FIELD_TYPE,
                       error_detail=f'字段"{field}"的类型必须是{_get_type_name(required_type)}')


def get_multipart_field(request: HttpRequest, field, required_type=str, allow_empty=False, allowed_values=None,
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
    assert required_type != dict, "不支持dict"
    if not request.content_type.startswith('multipart/form-data'):
        abort_response(ProjectError.NOT_ACCEPTABLE, "Content-Type must be multipart/form-data")
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
        abort_response(ProjectError.FIELD_MISSING,
                       error_detail='field "%(field_name)s" is missing') % {'field_name': field}
    elif value is None and allow_empty:
        return default
    if required_type not in (str, bytes):
        try:
            value = required_type(value)
            if allowed_values is not None and value not in allowed_values:
                abort_response(ProjectError.WRONG_FIELD_TYPE,
                               error_detail='Value of field "%(field)s" should be one of [%(allowed_values)s].') % {
                    'field': field, 'allowed_values': ','.join(allowed_values)}
        except (ValueError, TypeError):
            abort_response(ProjectError.WRONG_FIELD_TYPE,
                           error_detail='Field "%(field)s" should be %(required_type)s.') % {
                'field': field, 'required_type': _get_type_name(required_type)}
        return value
    return value


def get_param_value(request: HttpRequest, field: str, allow_empty=True, allowed_values=None, convert_to=None,
                    default=None):
    """
    获取GET参数，若发生错误则中止响应

    :param request: HttpRequest对象
    :param field: 字段名
    :param allow_empty: 是否允许为空
    :param allowed_values: 允许的取值
    :param convert_to: 要求必须能转换成的类型（因为GET参数都是字符串）。
            只支持int，float，和bool（字符串true为True，其余为False）
    :param default: 默认值
    """

    value = request.GET.get(field)
    if default is not None and convert_to:
        assert isinstance(default, convert_to)
    if not value:
        value = None
    if convert_to:
        assert convert_to in (int, float, bool)
        if value is not None:
            try:
                if convert_to is bool:
                    value = value == str('true')
                else:
                    value = convert_to(value)
            except (TypeError, ValueError):
                abort_response(ProjectError.WRONG_FIELD_TYPE,
                               error_detail=f'字段"{field}"的类型必须是{_get_type_name(convert_to)}')

    if value is None:
        if allow_empty:
            return default
        abort_response(ProjectError.FIELD_MISSING, error_detail=f"字段{field}缺失")
    elif allowed_values is not None and value not in allowed_values:
        msg = f'字段{field}的值只能是[{", ".join(map(lambda x: str(x), allowed_values))}]之一'
        abort_response(ProjectError.INVALID_FIELD_VALUE, error_detail=msg)
    else:
        return value


def require_methods_api(request_methods_list):
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method not in request_methods_list:
                abort_response(error=ProjectError.METHOD_NOT_ALLOWED,
                               error_detail=f"不允许{request.method}方法")
            return func(request, *args, **kwargs)

        return inner

    return decorator


require_GET_api = require_methods_api(["GET"])
require_POST_api = require_methods_api(["POST"])
require_PATCH_api = require_methods_api(["PATCH"])
require_PUT_api = require_methods_api(["PUT"])
require_DELETE_api = require_methods_api(["DELETE"])
