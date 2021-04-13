import os
from django.test import LiveServerTestCase
from djapi.test import assert_error, patch_json
from djapi.error import ProjectError
from djapi.req import param_field_getter, json_field_getter, multipart_getter, JSONRequester
from django.test.client import RequestFactory
from django.shortcuts import reverse
from unittest.mock import patch, MagicMock


class HTTPRequestTest(LiveServerTestCase):
    factory = RequestFactory()

    def setUp(self) -> None:
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)
        os.environ.pop('all_proxy', None)

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
        with assert_error(ProjectError.WRONG_FIELD_TYPE, "str"):
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
        with assert_error(ProjectError.WRONG_FIELD_TYPE, 'integer'):
            getter('b', required_type=int)
        # invalid value
        with assert_error(ProjectError.INVALID_FIELD_VALUE, '[a, b, c]'):
            getter('b', allowed_values=['a', 'b', 'c'])
        with assert_error(ProjectError.INVALID_FIELD_VALUE, '[1, 2, 3]'):
            getter('a', allowed_values=[1, 2, 3])
        self.assertEqual(getter('c', required_type=int, default=10), 10)
        self.assertEqual(getter('a', required_type=int, allow_empty=False), 0)
        self.assertEqual(getter('d', required_type=bool), True)
        self.assertEqual(getter('b', required_type=bool), False)

    def test_multipart_getter(self):
        with open('.gitignore', 'rb') as fp:
            data = {'a': 1, 'b': 'b', 'file': fp, 'c': [1, 2, 3]}
            req = self.factory.post('', data)
            getter = multipart_getter(req)
            a = getter('a', required_type=int)
            c = getter('c', required_type=list)
            self.assertEqual(a, 1)
            self.assertEqual(c, ['1', '2', '3'])
            with assert_error(ProjectError.WRONG_FIELD_TYPE):
                getter('b', required_type=int)
            with assert_error(ProjectError.INVALID_FIELD_VALUE):
                getter('b', allowed_values=['1', '2'], required_type=str)
            with assert_error(ProjectError.FIELD_MISSING):
                getter('abc')
            fp.seek(0)
            d = fp.read()
            self.assertEqual(d, getter('file', required_type=bytes).read())

    @patch("requests.delete")
    @patch("requests.patch")
    @patch("requests.post")
    @patch("requests.get")
    def test_json_requester_mocked(self, get: MagicMock, post: MagicMock, patch: MagicMock, delete: MagicMock):
        self.assertRaises(ValueError, JSONRequester, False, True)
        success = {'code': 0, 'msg': 'success', 'data': {'a': 1}}
        patch_json(get, success)
        patch_json(post, success)
        patch_json(delete, success)
        patch_json(patch, success)
        j = JSONRequester()
        j.get('')
        j.post('', json={})
        j.delete('')
        j.patch('')
        error = ProjectError.PERMISSION_DENIED.to_dict()
        patch_json(get, error)
        patch_json(post, error)
        patch_json(delete, error)
        patch_json(patch, error)
        with assert_error(ProjectError.PERMISSION_DENIED):
            j.get('')
        with assert_error(ProjectError.PERMISSION_DENIED):
            j.post('')
        with assert_error(ProjectError.PERMISSION_DENIED):
            j.delete('')
        with assert_error(ProjectError.PERMISSION_DENIED):
            j.patch('')
        self.assertEqual(j.msg, error['msg'])

        error = ProjectError.WRONG_FIELD_TYPE.to_dict()
        error['code'] = 1312321312321
        patch_json(get, error)
        patch_json(post, error)
        patch_json(delete, error)
        patch_json(patch, error)
        with assert_error(ProjectError.REMOTE_SERVER_ERROR):
            j.get('')
        with assert_error(ProjectError.REMOTE_SERVER_ERROR):
            j.post('')
        with assert_error(ProjectError.REMOTE_SERVER_ERROR):
            j.delete('')
        with assert_error(ProjectError.REMOTE_SERVER_ERROR):
            j.patch('')

        j = JSONRequester(raise_on_error_code=False)
        j.get('')
        j.post('')
        j.patch('')
        j.delete('')

    def test_json_requester_live(self):
        view = reverse('json_requester')
        j = JSONRequester()
        url = f"{self.live_server_url}{view}"
        j.post(url, json={'a': 'fnf23oif'})
        self.assertTrue(j.data, {'a': 'fnf23oif'})
        with assert_error(ProjectError.FIELD_MISSING, "a"):
            j.post(url, json={})

        with assert_error(ProjectError.REMOTE_SERVER_ERROR):
            j.post('http://fasfdsfasd')
