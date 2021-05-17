import json

import os

from djapi.error.error_code import ProjectError, ProjectException
from djapi.error.error_handler import ModelExceptionHandler
from djapi.error.middleware import ProjectExceptionMiddleware
from django.test import TestCase, RequestFactory
from tests_djapi.models import ModelForTesting
from djapi.test.testcase import assert_error


class TestError(TestCase):

    def test_exception(self):
        try:
            raise ProjectError.FIELD_MISSING("This is a test")
        except ProjectException as e:
            self.assertTrue(ProjectError.FIELD_MISSING.msg in str(e))
            self.assertTrue("This is a test" in str(e))
        e = ProjectError.REMOTE_SERVER_ERROR
        self.assertTrue(e.code, ProjectError[e.code].code)

    def test_middleware(self):
        request = RequestFactory()
        middleware = ProjectExceptionMiddleware(lambda x: x)
        os.environ['RE_RAISE_UNKNOWN_EXCEPTIONS'] = "True"
        self.assertRaises(ValueError, middleware.process_exception,
                          request, ValueError)
        os.environ['RE_RAISE_UNKNOWN_EXCEPTIONS'] = "False"
        error = ProjectError.UNKNOWN_ERROR
        res = middleware.process_exception(request,
                                           ProjectError.UNKNOWN_ERROR("Test Error", data={"files": ['1', '2 ']}))
        res = json.loads(res.content.decode())
        self.assertTrue(res['code'], error.code)
        self.assertTrue(res['msg'], error.msg)
        self.assertTrue(res['error_detail'], "Test Error")
        self.assertTrue(res['data'], {"files": ['1', '2 ']})
        # TODO 检查日志

    def test_model_exception_handler(self):
        handler = ModelExceptionHandler("hello")
        new = ModelForTesting(a='abc', b=1)
        new.save()
        with assert_error(ProjectError.ALREADY_EXISTS, "hello"):
            with handler:
                new = ModelForTesting(a='fas', b=1)
                new.save()
