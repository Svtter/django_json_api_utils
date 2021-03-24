from django_utils.error import ProjectError
from django.http import JsonResponse


def json_response(data=None, msg: str = ProjectError.SUCCESS.error_message,
                  status_code: int = 200,
                  ) -> JsonResponse:
    """
    将字典数据转为JSON返回
    :param data: 需要返回的数据
    :param msg: 提示消息
    :param status_code: req 状态码，默认 200
    """
    result = {'code': ProjectError.SUCCESS.error_code, 'msg': msg,
              'data': data}
    if msg:
        result['msg'] = msg
    return JsonResponse(result, json_dumps_params={'ensure_ascii': False}, status=status_code)
