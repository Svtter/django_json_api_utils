from django_utils.error import ProjectError, ProjectException
from django.http import JsonResponse


def json_response(data=None, status_code: int = 200) -> JsonResponse:
    """
    将字典数据转为JSON返回
    :param data: 需要返回的数据
    :param msg: 提示消息
    :param status_code: req 状态码，默认 200
    """
    result = ProjectException(ProjectError.SUCCESS).to_dict()
    if data:
        result['data'] = data
    return JsonResponse(result, json_dumps_params={'ensure_ascii': False}, status=status_code)
