from typing import Union
from .error_code import ProjectError, ProjectErrorDetail, ProjectException


def abort_response(error: Union[ProjectError, ProjectErrorDetail], error_detail: str = None):
    """
    中断响应，并抛出ProjectException异常
    :param error: ProjectError枚举值或者ProjectErrorDetail对象
    :param error_detail: 详细错误信息，如果error是ProjectErrorDetail对象则忽略
    使用示例：
    1. abort_response(ProjectError.INVALID_FIELD_VALUE, "abc不是有效的int")
    2. abort_response(ProjectError.INVALID_FIELD_VALUE("abc不是有效的int"))
    """
    if isinstance(error, ProjectError):
        if error_detail:
            error = ProjectErrorDetail(error, error_detail)
    raise ProjectException(error)
