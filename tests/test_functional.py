from django_utils.req import param_field_getter, json_field_getter, json_response
from django_utils.error.error_handler import abort_with_error
from django.test import TestCase
from django.shortcuts import reverse
from django_utils.error.error_code import ProjectError


def functional_test_json_view(request):
    getter = json_field_getter(request)
    a = getter('a', int)
    b = getter('b')
    return json_response({'a': a, 'b': b})


def functional_test_param_view(request):
    getter = param_field_getter(request)
    a = getter('a', convert_to=int, allow_empty=False)
    b = getter('b')
    return json_response({'a': a, 'b': b})


def functional_test_other_view(request):
    getter = param_field_getter(request)
    t = getter('project_exception')
    if t:
        abort_with_error(ProjectError.BAD_REQUEST)
    raise FileExistsError("Unknown Exception")


class TestFunctional(TestCase):
    def test_json(self):
        view = reverse('json')
        data = {'a': 1, 'b': 'abc'}
        res = self.client.post(view, data, content_type='application/json')
        self.assertEqual(res.json()['data'], data)
        res = self.client.post(view, {}, content_type='application/json')
        self.assertEqual(res.json()['code'], ProjectError.FIELD_MISSING.error_code)

    def test_param(self):
        view = reverse('param')
        data = {'a': 2, 'b': 'abc'}
        res = self.client.get(view, data)
        self.assertEqual(res.json()['data'], data)
        res = self.client.get(view, {})
        self.assertEqual(res.json()['code'], ProjectError.FIELD_MISSING.error_code)

    def test_other(self):
        view = reverse('other')
        res = self.client.get(view, data={'project_exception': True})
        self.assertEqual(res.json()['code'], ProjectError.BAD_REQUEST.error_code)
        self.assertEqual(res.status_code, ProjectError.BAD_REQUEST.status_code)
        res = self.client.get(view)
        self.assertEqual(res.json()['code'], ProjectError.UNKNOWN_ERROR.error_code)
        self.assertEqual(res.status_code, 500)
        # TODO 检查日志
