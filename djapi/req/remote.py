import requests
from djapi.error import ProjectError

__all__ = ['JSONRequester']


class JSONRequester:
    """
    Calls remote json API and return data. If the remote server uses djapi, automatically processes error.
    """

    def __init__(self, djapi=True, raise_on_error_code=True):
        """
        :param djapi: whether remote server uses djapi. if not, "code", "data" and "msg"
                    will not be available, and response data can only be accessed by calling json()
        :param raise_on_error_code: if remote server uses djapi,
                    raise ProjectError when 'code' in response is not 0 (Success).
                    if code is not defined in ProjectError, ProjectError.REMOTE_SERVER_ERROR will be raised,
                    with original remote error message and error detail
        """
        if not djapi and raise_on_error_code:
            raise ValueError("Cannot use raise_on_error_code when djapi is False")
        self._djapi = djapi
        self._raise_on_error_code = raise_on_error_code
        self._resp = {}
        self._code = None
        self._data = None
        self._msg = None
        self._error_detail = None

    @property
    def json(self):
        return self._resp

    @property
    def code(self):
        if not self._djapi:
            raise ValueError("Cannot use attribute code when djapi is False")
        return self._code

    @property
    def data(self):
        if not self._djapi:
            raise ValueError("Cannot use attribute data when djapi is False")
        return self._data

    @property
    def msg(self):
        if not self._djapi:
            raise ValueError("Cannot use attribute msg when djapi is False")
        return self._msg

    def _clean(self):
        self._code = None
        self._msg = None
        self._data = None
        self._resp = None

    def _process_response(self, requests_func, args, kwargs):
        try:
            res = requests_func(*args, **kwargs)
        except Exception as e:
            self._clean()
            raise ProjectError.REMOTE_SERVER_ERROR(str(e))
        try:
            res = res.json()
        except Exception as e:
            self._clean()
            try:
                msg = res.content.decode()
            except UnicodeDecodeError:
                msg = str(res.content)
            raise ProjectError.REMOTE_SERVER_ERROR(
                secret_detail=f"{e.__class__.__name__}: {str(e)} (server response was: {msg})")
        self._resp = res
        if self._djapi:
            self._code = res['code']
            self._msg = res['msg']
            self._data = res['data']
            self._error_detail = res.get('error_detail')
        if self._raise_on_error_code:
            if self._code != ProjectError.SUCCESS.code:
                try:
                    raise ProjectError[self._code](self._error_detail)
                except KeyError:
                    raise ProjectError.REMOTE_SERVER_ERROR(self._error_detail)

    def get(self, url, params=None, **kwargs):
        kwargs['params'] = params
        self._process_response(requests.get, [url], kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        kwargs['json'] = json
        kwargs['data'] = data
        self._process_response(requests.post, [url], kwargs)

    def patch(self, url, data=None, json=None, **kwargs):
        kwargs['json'] = json
        kwargs['data'] = data
        self._process_response(requests.patch, [url], kwargs)

    def delete(self, url, **kwargs):
        self._process_response(requests.delete, [url], kwargs)
