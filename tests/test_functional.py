from django.test import TestCase
from django.shortcuts import reverse
from django_utils.error.error_code import ProjectError


class TestFunctional(TestCase):
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
