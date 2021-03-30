from django.test.client import Client
from djapi.error.error_code import ProjectException


class _ProjectErrorTester:
    def __init__(self, error: ProjectException = None, msg: str = None):
        self._error = error
        self._msg = msg

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val: ProjectException, exc_tb):
        if exc_type is None:
            raise AssertionError("测试失败！未抛出任何异常！")
        if exc_type == ProjectException:
            if self._error is None:
                return True
            if exc_val.code != self._error.code:
                msg = f"测试失败！未抛出{self._error.msg} ({self._error.__class__})，抛出的异常为{exc_val.msg} ({exc_val.__class__})"
                raise AssertionError(msg) from None
            elif self._msg and self._msg not in str(exc_val):
                raise AssertionError(f'测试失败！不包含错误信息"{self._msg}"')
        else:
            raise AssertionError("测试失败！未抛出ProjectException！")
        return True


def assert_error(error: ProjectException, msg: str = None) -> _ProjectErrorTester:
    """
    生成一个_projectErrorTester上下文管理器，用来
    断言with块内的代码一定抛出包含给定的ProjectError的ProjectException异常，
    如果指定msg则要求抛出的异常中一定包含msg字符串

    :param error: ProjectError枚举
    :param msg: 要求必须包含的错误信息，用以区分具体的error
    """
    return _ProjectErrorTester(error, msg)


class JSONClient(Client):

    def __getattr__(self, item):
        # suppresses 'Unresolved attribute' in Pycharm
        pass

    def _set_response(self, response):
        try:
            data = response.json()
            self.__dict__.update(data)
            return response
        except Exception:
            try:
                raise ValueError(f'Response is not a json object. Response is "{response.content.decode()}"')
            except UnicodeDecodeError:
                raise ValueError("Response is binary instead of a json object.")

    def get(self, path, data: dict = None, follow: bool = False, secure: bool = False, **extra):
        res = super().get(path=path, data=data, follow=follow, secure=False, **extra)
        self._set_response(res)
        return res

    def post(self, path, data=None, content_type='application/json',
             follow=False, secure=False, **extra):
        res = super().post(path, data, content_type, follow, secure, **extra)
        self._set_response(res)
        return res

    def post_file(self, path, data: dict, follow=False, secure=False, **extra):
        res = super().post(path, data, follow=follow, secure=secure, **extra)
        self._set_response(res)
        return res
