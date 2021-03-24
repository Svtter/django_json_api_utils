from django.test import TestCase
from django_utils.test import assert_error
from django_utils.error import ProjectError
from django_utils.req import param_field_getter, json_field_getter
from django.test.client import RequestFactory


class HTTPRequestTest(TestCase):
    factory = RequestFactory()

    def test_get_json_field(self):
        request = self.factory.get('')
        with assert_error(ProjectError.NOT_ACCEPTABLE):
            json_field_getter(request)("fsd")
        request.content_type = 'a'
        with assert_error(ProjectError.NOT_ACCEPTABLE, "application/json"):
            json_field_getter(request)("fsd")
        test_json = {
            'a': 0, 'b': 'b',
            'c': '', 'd': None, 'e': [], 'f': [1, 2, 3],
            'g': {}, 'h': {'a': 1}
        }
        request = self.factory.post('', test_json, content_type='application/json')
        # field missing
        with assert_error(ProjectError.FIELD_MISSING, "abc"):
            json_field_getter(request)('abc')
        # field empty
        with assert_error(ProjectError.FIELD_MISSING, "d"):
            json_field_getter(request)('d')
        with assert_error(ProjectError.FIELD_MISSING, "g"):
            json_field_getter(request)('g')
        with assert_error(ProjectError.FIELD_MISSING, "e"):
            json_field_getter(request)('e')

        # wrong field type
        with assert_error(ProjectError.WRONG_FIELD_TYPE, "a"):
            json_field_getter(request)('a', str)
        # allow none
        self.assertEqual(json_field_getter(request)('d', allow_empty=True), None)
        # allowed_values
        with assert_error(ProjectError.INVALID_FIELD_VALUE, '1, 2, 3'):
            json_field_getter(request)('a', allowed_values=(1, 2, 3))
        self.assertEqual(json_field_getter(request)('a', allowed_values=(0, 2, 3)), 0)
        self.assertEqual(json_field_getter(request)('f'), [1, 2, 3])
        self.assertEqual(json_field_getter(request)('h'), {'a': 1})
        self.assertEqual(json_field_getter(request)('d', allow_empty=True, default=100), 100)

    def test_get_param(self):
        request = self.factory.get('', {'a': 0, 'b': "abc", 'c': '', 'd': 'true'})
        getter = param_field_getter(request)
        # field missing
        with assert_error(ProjectError.FIELD_MISSING, '123'):
            getter('123', allow_empty=False)
        # empty field
        with assert_error(ProjectError.FIELD_MISSING, 'c'):
            getter('c', allow_empty=False)
        # wrong field type
        with assert_error(ProjectError.WRONG_FIELD_TYPE, '字段"b"的类型必须是integer'):
            getter('b', convert_to=int)
        # invalid value
        with assert_error(ProjectError.INVALID_FIELD_VALUE, '[a, b, c]'):
            getter('b', allowed_values=['a', 'b', 'c'])
        with assert_error(ProjectError.INVALID_FIELD_VALUE, '[1, 2, 3]'):
            getter('a', allowed_values=[1, 2, 3])
        self.assertEqual(getter('c', convert_to=int, default=10), 10)
        self.assertEqual(getter('a', convert_to=int, allow_empty=False), 0)
        self.assertEqual(getter('d', convert_to=bool), True)
        self.assertEqual(getter('b', convert_to=bool), False)
