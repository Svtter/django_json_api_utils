import logging
import pytz
import json

from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from .error_code import ProjectError, ProjectException

logger = logging.getLogger('django')


class ProjectExceptionMiddleware:

    def process_exception(self, request, exception: Exception):

        if not isinstance(exception, ProjectException):
            # 未知异常，记录异常栈
            logger.error(str(exception.__traceback__))
            if settings.DEBUG:  # DEBUG模式下重新抛出
                raise
            exception = ProjectException(ProjectError.UNKNOWN_ERROR)
        else:
            # 异常栈记为DEBUG级别
            logger.debug(str(exception.__traceback__))
        r = HttpResponse(json.dumps(exception.to_dict(), ensure_ascii=False),
                         content_type='application/json; charset=utf-8')
        r.status_code = exception.status_code
        return r
