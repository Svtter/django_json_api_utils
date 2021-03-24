import json
from django_utils.error.error_code import ProjectError, ProjectException
from django_utils.error.error_handler import abort_with_error, ModelExceptionHandler
from django_utils.error.middleware import ProjectExceptionMiddleware
from django.test import TestCase, RequestFactory
from django.conf import settings
from django_utils.tests.models import TestModel
from django_utils.test.testcase import assert_error


class TestError(TestCase):

    def test_exception(self):
        try:
            abort_with_error(ProjectError.FIELD_MISSING("This is a test"))
        except ProjectException as e:
            self.assertTrue(ProjectError.FIELD_MISSING.error_message in str(e))
            self.assertTrue("This is a test" in str(e))

    def test_middleware(self):
        request = RequestFactory()
        middleware = ProjectExceptionMiddleware(lambda x: x)
        settings.DEBUG = True
        self.assertRaises(ValueError, middleware.process_exception,
                          request, ValueError)
        settings.DEBUG = False
        error = ProjectError.UNKNOWN_ERROR
        res = middleware.process_exception(request, ProjectException(error("Test Error")))
        res = json.loads(res.content.decode())
        self.assertTrue(res['code'], error.error_code)
        self.assertTrue(res['msg'], error.error_message)
        self.assertTrue(res['error_detail'], "Test Error")
        # TODO 检查日志

    def test_model_exception_handler(self):
        handler = ModelExceptionHandler("hello")
        new = TestModel(a='abc', b=1)
        new.save()
        with assert_error(ProjectError.UNPROCESSABLE, "hello"):
            with handler:
                new = TestModel(a='fas', b=1)
                new.save()
