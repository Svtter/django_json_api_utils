import os
from django.test import LiveServerTestCase
from django.shortcuts import reverse
from djapi.error.error_code import ProjectError
from djapi.req import JSONRequester


class TestFunctional(LiveServerTestCase):
    def setUp(self) -> None:
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)
        os.environ.pop('all_proxy', None)

    def test_json(self):
        view = reverse('json')
        data = {'a': 1, 'b': 'abc'}
        res = self.client.post(view, data, content_type='application/json')
        self.assertEqual(res.json()['data'], data)
        res = self.client.post(view, {}, content_type='application/json')
        self.assertEqual(res.json()['code'], ProjectError.FIELD_MISSING.code)

    def test_param(self):
        view = reverse('param')
        data = {'a': 2, 'b': 'abc'}
        res = self.client.get(view, data)
        self.assertEqual(res.json()['data'], data)
        res = self.client.get(view, {})
        self.assertEqual(res.json()['code'], ProjectError.FIELD_MISSING.code)

    def test_multipart(self):
        with open('.gitignore', 'rb') as fp:
            view = reverse('multipart')
            data = {'a': 1, 'b': 'b', 'file': fp}
            res = self.client.post(view, data)
            self.assertEqual(res.json()['code'], 0)
            fp.seek(0)
            self.assertEqual(res.json()['data']['file'], fp.read().decode())

    def test_other(self):
        view = reverse('other')
        res = self.client.get(view, data={'project_exception': True})
        self.assertEqual(res.json()['code'], ProjectError.BAD_REQUEST.code)
        self.assertEqual(res.status_code, ProjectError.BAD_REQUEST.status_code)
        res = self.client.get(view)
        self.assertEqual(res.json()['code'], ProjectError.UNKNOWN_ERROR.code)
        self.assertEqual(res.status_code, 500)
        # TODO 检查日志

    def test_json_requester(self):
        view = reverse('json_requester')
        j = JSONRequester()
        url = f"{self.live_server_url}{view}"
        data = {'a': 'afsdfsdfsdf'}
        j.post(url, json=data)
        self.assertTrue(j.data, data)
