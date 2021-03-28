from django_utils.error import ProjectError
from django_utils.req import json_field_getter, json_response, param_field_getter, multipart_getter


def functional_test_json_view(request):
    getter = json_field_getter(request)
    a = getter('a', int)
    b = getter('b')
    return json_response({'a': a, 'b': b})


def functional_test_param_view(request):
    getter = param_field_getter(request)
    a = getter('a', required_type=int, allow_empty=False)
    b = getter('b')
    return json_response({'a': a, 'b': b})


def functional_test_multipart_view(request):
    getter = multipart_getter(request)
    a = getter('a', required_type=int, allow_empty=False)
    b = getter('b')
    return json_response({'a': a, 'b': b})


def functional_test_other_view(request):
    getter = param_field_getter(request)
    t = getter('project_exception')
    if t:
        raise ProjectError.BAD_REQUEST
    raise FileExistsError("Unknown Exception")


def test_json_client(request):
    getter = json_field_getter(request)
    a = getter('a', allow_empty=True)
    b = getter('b', allow_empty=True)
    c = getter('c', allow_empty=True)
    return json_response(dict(a=a, b=b, c=c))


def functional_test_multipart(request):
    getter = multipart_getter(request)
    a = getter('a', required_type=int)
    b = getter('b', required_type=str)
    c = getter('file')
    return json_response(dict(a=a, b=b, file=c.read().decode()))
