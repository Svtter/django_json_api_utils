from djapi.error.error_code import ProjectError
from django.db import IntegrityError
from django.db.models import ObjectDoesNotExist


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
            raise ProjectError.NOT_FOUND(f"{self._display_name}不存在")
        if exc_type == IntegrityError:
            # TODO 其他数据库的duplicate信息
            if 'UNIQUE' in exc_val or 'Duplicate' in exc_val or 'duplicate' in exc_val:
                raise ProjectError.UNPROCESSABLE(f"{self._display_name}已经存在")
            return False
        return False
