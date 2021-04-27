from django.shortcuts import reverse
from django.test import TestCase, Client
from djapi.test.testcase import assert_error, JSONClient
from djapi.error.error_code import ProjectError


class TestTestCase(TestCase):
    def test_assert_error(self):
        with assert_error(ProjectError.BAD_REQUEST):
            raise ProjectError.BAD_REQUEST

        with self.assertRaises(AssertionError):
            with assert_error(ProjectError.BAD_REQUEST):
                raise ProjectError.UNKNOWN_ERROR
        with assert_error(ProjectError.INVALID_FIELD_VALUE, ["a", "b", "c"]):
            raise ProjectError.INVALID_FIELD_VALUE("abc")
        with self.assertRaises(AssertionError):
            with assert_error(ProjectError.INVALID_FIELD_VALUE, ["a", "b", "c"]):
                raise ProjectError.INVALID_FIELD_VALUE("ab123")

        with assert_error(ProjectError.UNPROCESSABLE, "供应商"):
            raise ProjectError.UNPROCESSABLE("找不到供应商(sap_code=123)")
        with assert_error(ProjectError.INVALID_FIELD_VALUE, ["a", "b", "c"]):
            raise ProjectError.INVALID_FIELD_VALUE("abc")
        with assert_error(ProjectError.INVALID_FIELD_VALUE, msg_pattern=r"供应商.+123.*\!+"):
            raise ProjectError.INVALID_FIELD_VALUE("找不到供应商(sap_code=123)!")
        with self.assertRaises(AssertionError):
            with assert_error(ProjectError.INVALID_FIELD_VALUE, msg_pattern="a.*b"):
                raise ProjectError.INVALID_FIELD_VALUE("123")

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
