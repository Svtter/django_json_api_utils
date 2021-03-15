import traceback
from typing import Union
from ..error.error_code import ProjectError, ProjectException, ProjectErrorDetail


class _ProjectErrorTester:
    def __init__(self, error: ProjectError = None, msg: str = None):
        self._error = error
        self._msg = msg

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val: ProjectException, exc_tb):
        if exc_type is None:
            raise AssertionError("测试失败！未抛出异常")
        if exc_type == ProjectException:
            if self._error is None:
                return True
            if exc_val.error != self._error:
                msg = f"测试失败！未抛出{self._error.name}，抛出的异常为{str(exc_val)}"
                raise AssertionError(msg)
            elif self._msg and self._msg not in str(exc_val):
                raise AssertionError(f'测试失败！不包含错误信息"{self._msg}"')
        else:
            raise AssertionError("测试失败！未抛出ProjectException！")
        return True


def assert_error(error: ProjectError, msg: str = None):
    """
    断言with块内的代码一定抛出包含给定的ProjectError的ProjectException异常，
    如果指定msg则要求抛出的异常中一定包含msg字符串

    :param error: ProjectError枚举
    :param msg: 要求必须包含的错误信息，用以区分具体的error
    """
    if isinstance(error, ProjectErrorDetail):
        msg = error.error_detail
        error = error.error
    return _ProjectErrorTester(error, msg)
