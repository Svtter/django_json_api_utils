from django.shortcuts import reverse
from django.test import TestCase, Client
from django_utils.test.testcase import assert_error, JSONClient
from django_utils.error.error_code import ProjectError, ProjectException


class TestTestCase(TestCase):
    def test_assert_error(self):
        try:
            with assert_error(ProjectError.BAD_REQUEST):
                raise ProjectException(ProjectError.BAD_REQUEST)
        except ProjectException:
            self.fail("assert_error failed to catch ProjectException!")

        try:
            with assert_error(ProjectError.BAD_REQUEST):
                raise ProjectException(ProjectError.UNKNOWN_ERROR)
        except AssertionError:
            pass
        except Exception:
            self.fail("assert_error failed to raise AssertError")
        else:
            self.fail("assert_error failed to raise AssertError")

        try:
            with assert_error(ProjectError.UNPROCESSABLE, "abc"):
                raise ProjectException(ProjectError.UNPROCESSABLE("123123abc123123"))
        except Exception:
            self.fail("assert_error failed to process error message")

        try:
            with assert_error(ProjectError.UNPROCESSABLE, "abc"):
                raise ProjectException(ProjectError.UNPROCESSABLE("123"))
        except AssertionError:
            pass
        except Exception:
            self.fail("assert_error failed to process error message")
        else:
            self.fail("assert_error failed to process error message")

    def test_json_client(self):
        client = JSONClient()
        view = reverse('json_client')
        default_client = Client()
        post = {'a': 1, 'b': [1, 2, 3], 'c': {'a': 1, 'b': 'b'}}
        res = client.post(view, data=post)
        res_expected = default_client.post(view, data=post, content_type='application/json')
        self.assertEqual(str(res), str(res_expected))
        self.assertEqual(str(res), str(res_expected))
        self.assertEqual(res.content, res_expected.content)
        self.assertTrue(hasattr(client, 'code'))
        self.assertTrue(hasattr(client, 'msg'))
        self.assertTrue(hasattr(client, 'data'))
        self.assertEqual(client.code, 0)
        self.assertEqual(res.content, res_expected.content)
        self.assertEqual(client.data, {'a': 1, 'b': [1, 2, 3], 'c': {'a': 1, 'b': 'b'}})
