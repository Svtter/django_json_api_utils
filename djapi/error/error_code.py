class ProjectException(Exception):
    """
    异常类，必须指定产生的异常的ProjectError枚举值
    """
    _code_set = set()

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, msg: str, code: int, status_code: int = 422):
        self.msg = msg
        self.code = code
        self.status_code = status_code
        self.error_detail = None

    def to_dict(self):
        d = {'msg': self.msg, 'code': self.code, 'data': {}}
        if self.error_detail:
            d['error_detail'] = self.error_detail
        return d

    def __str__(self):
        msg = self.msg
        if self.error_detail:
            msg += f"({str(self.error_detail)})"
        return msg

    def __call__(self, error_detail):
        self.error_detail = error_detail
        return self


class ProjectErrorMetaClass(type):
    _error_code_dict = {}
    _enum_members = set()

    def __new__(mcs, cls_name, bases, class_dict):
        for member, value in class_dict.items():
            if isinstance(value, ProjectException):
                if value.code in ProjectErrorMetaClass._error_code_dict:
                    prev_class, prev_member = ProjectErrorMetaClass._error_code_dict[value.code]
                    raise ValueError(
                        f"Both {prev_class}.{prev_member} and {cls_name}.{member} have error code {value.code}")
                ProjectErrorMetaClass._error_code_dict[value.code] = cls_name, member
                ProjectErrorMetaClass._enum_members.add(member)
        return super().__new__(mcs, cls_name, bases, class_dict)

    def __getattribute__(self, item):
        super_item = super().__getattribute__(item)
        if item in ProjectErrorMetaClass._enum_members:
            return ProjectException(msg=super_item.msg, code=super_item.code, status_code=super_item.status_code)
        return super_item

    def __setattr__(self, key, value):
        raise ValueError("Cannot set attributes to ProjectError")


e = ProjectException


class ProjectError(metaclass=ProjectErrorMetaClass):
    """
    错误类枚举
    每个错误的值为一个元组，（错误名，自定义错误码, HTTP状态码）
    其中HTTP状态码可以省略
    HTTP状态码默认为422
    """

    SUCCESS = e("Success", 0, 200)
    UNKNOWN_ERROR = e("Unknown error", 500, 500)
    BAD_REQUEST = e("Bad request", 400, 400)
    PERMISSION_DENIED = e("Permission denied", 403, 403)
    NOT_FOUND = e("Resource not found", 404, 404)
    METHOD_NOT_ALLOWED = e("Method not allowed", 405, 405)
    UNPROCESSABLE = e("Unprocessable entity", 422, 422)
    FIELD_MISSING = e("Field missing", 2)
    WRONG_FIELD_TYPE = e("Invalid field type", 3)
    NOT_ACCEPTABLE = e("Invalid content-type", 4)
    INVALID_FIELD_VALUE = e("Invalid field value", 5)

    def __new__(cls, *args, **kwargs):
        raise TypeError("Cannot instantiate ProjectError or its subclasses")
