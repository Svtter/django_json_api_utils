from django.test import TestCase
from django.http import HttpResponse, HttpRequest
from django_utils.test.testcase import assert_error, ProjectError, ProjectException
from django_utils.req.request import get_json_field, get_multipart_field, get_param_value
from django.test.client import RequestFactory


class HTTPRequestTest(TestCase):
    factory = RequestFactory()

    def test_get_json_field(self):
        request = self.factory.get('')
        with assert_error(ProjectError.NOT_ACCEPTABLE):
            get_json_field(request, "fsd")
        request.content_type = 'a'
        with assert_error(ProjectError.NOT_ACCEPTABLE, "application/json"):
            get_json_field(request, "fsd")
        test_json = {
            'a': 0, 'b': 'b',
            'c': '', 'd': None, 'e': [], 'f': [1, 2, 3],
            'g': {}, 'h': {'a': 1}
        }
        request = self.factory.post('', test_json, content_type='application/json')
        # field missing
        with assert_error(ProjectError.FIELD_MISSING, "abc"):
            get_json_field(request, 'abc')
        # field empty
        with assert_error(ProjectError.FIELD_MISSING, "d"):
            get_json_field(request, 'd')
        with assert_error(ProjectError.FIELD_MISSING, "g"):
            get_json_field(request, 'g')
        with assert_error(ProjectError.FIELD_MISSING, "e"):
            get_json_field(request, 'e')

        # wrong field type
        with assert_error(ProjectError.WRONG_FIELD_TYPE, "a"):
            get_json_field(request, 'a', str)
        # allow none
        self.assertEqual(get_json_field(request, 'd', allow_empty=True), None)
        # allowed_values
        with assert_error(ProjectError.INVALID_FIELD_VALUE, '1, 2, 3'):
            get_json_field(request, 'a', allowed_values=(1, 2, 3))
        self.assertEqual(get_json_field(request, 'a', allowed_values=(0, 2, 3)), 0)
        self.assertEqual(get_json_field(request, 'f'), [1, 2, 3])
        self.assertEqual(get_json_field(request, 'h'), {'a': 1})
        self.assertEqual(get_json_field(request, 'd', allow_empty=True, default=100), 100)

    def test_get_param(self):
        request = self.factory.get('', {'a': 0, 'b': "abc", 'c': '', 'd': 'true'})
        # field missing
        with assert_error(ProjectError.FIELD_MISSING, '123'):
            get_param_value(request, '123', allow_empty=False)
        # empty field
        with assert_error(ProjectError.FIELD_MISSING, 'c'):
            get_param_value(request, 'c', allow_empty=False)
        # wrong field type
        with assert_error(ProjectError.WRONG_FIELD_TYPE, '字段"b"的类型必须是integer'):
            get_param_value(request, 'b', convert_to=int)
        # invalid value
        with assert_error(ProjectError.INVALID_FIELD_VALUE, '[a, b, c]'):
            get_param_value(request, 'b', allowed_values=['a', 'b', 'c'])
        with assert_error(ProjectError.INVALID_FIELD_VALUE, '[1, 2, 3]'):
            get_param_value(request, 'a', allowed_values=[1, 2, 3])
        self.assertEqual(get_param_value(request, 'c', convert_to=int, default=10), 10)
        self.assertEqual(get_param_value(request, 'a', convert_to=int, allow_empty=False), 0)
        self.assertEqual(get_param_value(request, 'd', convert_to=bool), True)
        self.assertEqual(get_param_value(request, 'b', convert_to=bool), False)
