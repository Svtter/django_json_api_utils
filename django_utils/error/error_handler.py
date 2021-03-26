from typing import Union
from django_utils.error.error_code import ProjectError, ProjectErrorDetail, ProjectException
from django.db import IntegrityError
from django.db.models import ObjectDoesNotExist


def abort_with_error(error: Union[ProjectError, ProjectErrorDetail], error_detail: str = None, silent_chain=True):
    """
    中断响应，并抛出ProjectException异常
    使用示例：
    1. abort_response(ProjectError.INVALID_FIELD_VALUE, "abc不是有效的int")
    2. abort_response(ProjectError.INVALID_FIELD_VALUE("abc不是有效的int"))

    :param error: ProjectError枚举值或者ProjectErrorDetail对象
    :param error_detail: 详细错误信息，如果error是ProjectErrorDetail对象则忽略
    :param silent_chain: 在异常栈中不显示之前的异常，即”During handling of the above exception, another exception occurred'

    """
    if isinstance(error, ProjectError):
        if error_detail:
            error = ProjectErrorDetail(error, error_detail)
    if silent_chain:
        raise ProjectException(error) from None
    raise ProjectException(error)


class ModelExceptionHandler:
    def __init__(self, display_name: str):
        self._display_name = display_name

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        exc_val = str(exc_val)
        if not exc_type:
            return
        if issubclass(exc_type, ObjectDoesNotExist):
            # self._display_name = exc_val.split()[0]
            abort_with_error(ProjectError.NOT_FOUND(f"{self._display_name}不存在"))
        if exc_type == IntegrityError:
            if 'UNIQUE' in exc_val:
                abort_with_error(ProjectError.UNPROCESSABLE(f"{self._display_name}已经存在"))
            return False
        return False
