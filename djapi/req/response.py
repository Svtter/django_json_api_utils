from djapi.error import ProjectError
from django.http import JsonResponse

__all__ = ['json_response']


def json_response(data=None, status_code: int = 200) -> JsonResponse:
    """
    将字典数据转为JSON返回
    :param data: 需要返回的数据
    :param status_code: req 状态码，默认 200
    """
    result = ProjectError.SUCCESS.to_dict()
    if data:
        result['data'] = data
    return JsonResponse(result, json_dumps_params={'ensure_ascii': False}, status=status_code)
