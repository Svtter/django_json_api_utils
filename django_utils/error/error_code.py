from enum import Enum
from typing import Union


class ProjectError(Enum):
    """
    错误类枚举
    每个错误的值为一个元组，（错误名，HTTP状态码，自定义错误码）
    其中HTTP状态码和自定义错误码可以省略
    HTTP状态码默认为422，自定义错误默认为10000
    """
    SUCCESS = "Success", 200, 0
    UNKNOWN_ERROR = "Unknown error", 500,
    BAD_REQUEST = "Bad req", 400,
    PERMISSION_DENIED = "Permission denied", 403,
    METHOD_NOT_ALLOWED = "Method not allowed", 405,
    NOT_FOUND = "Resource not found", 404,
    FIELD_MISSING = "Field missing", 422, 2
    WRONG_FIELD_TYPE = "Invalid field type", 422, 3
    NOT_ACCEPTABLE = "Invalid content-type", 406,
    INVALID_FIELD_VALUE = "Invalid field value", 422, 4
    UNPROCESSABLE = "Unprocessable entity", 422, 422

    def __init__(self, *args, **kwargs):
        assert isinstance(self.value, tuple), "Each error enum must be a tuple"
        assert isinstance(self.value[0], str)

    @property
    def error_message(self) -> str:
        """
        错误名
        """
        return self.value[0]

    @property
    def status_code(self) -> int:
        """
        返回HTTP状态码，如果未指定，返回422。
        :return: HTTP状态码
        """
        if len(self.value) > 1:
            return self.value[1]
        return 422

    @property
    def error_code(self) -> int:
        if len(self.value) > 2:
            return self.value[2]
        return 10000

    def __call__(self, error_detail: str):
        return ProjectErrorDetail(self, error_detail)


class ProjectErrorDetail:
    """
    包含了详细错误的的WaterError
    """

    def __init__(self, error: 'ProjectError', error_detail: Union[dict, str]):
        self.error = error
        self.error_detail = error_detail

    def __getattr__(self, item):
        return getattr(self.error, item)


class ProjectException(Exception):
    """
    异常类，必须指定产生的异常的ProjectError枚举值
    """

    def __init__(self, error: Union[ProjectError, ProjectErrorDetail]):
        """
        :param error: ProjectError枚举值，或者ProjectErrorDetail对象
        """
        if isinstance(error, ProjectError):
            self.error = error
            self.error_detail = None
        else:
            self.error = error.error
            self.error_detail = error.error_detail
        self.code = self.error.error_code
        self.msg = self.error.error_message
        self.status_code = self.error.status_code

    def to_dict(self):
        d = {'msg': self.msg, 'code': self.code, 'data': {}}
        if self.error_detail:
            d['error_detail'] = self.error_detail
        return d

    def __str__(self):
        msg = self.error.error_message
        if self.error_detail:
            msg += f"({str(self.error_detail)})"
        return msg
