import logging
import traceback
import json

from django.http import HttpResponse
from djapi.env import get_var
from djapi.error.error_code import ProjectError, ProjectException

__all__ = ['ProjectError', 'ProjectException', 'ProjectExceptionMiddleware']

logger = logging.getLogger('django')


class ProjectExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_exception(self, request, exception: Exception):
        if not isinstance(exception, ProjectException):
            # 未知异常，记录异常栈
            logger.error(traceback.format_exc())
            if get_var("RE_RAISE_UNKNOWN_EXCEPTIONS", is_string=False, default=False):
                raise exception
            exception = ProjectError.UNKNOWN_ERROR
        else:
            msg = traceback.format_exc()
            if exception.secret_detail:
                msg += f'\n{exception.secret_detail}'
            logger.info(msg)
        r = HttpResponse(json.dumps(exception.to_dict(), ensure_ascii=False),
                         content_type='application/json; charset=utf-8')
        r.status_code = exception.status_code
        return r
