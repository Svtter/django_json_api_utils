from django.test import TestCase
from django_utils.env import get_var


class TestEnv(TestCase):
    def test(self):
        a = get_var('a', is_string=False)
        b = get_var('b', is_string=False)
        c = get_var('c')
        d = get_var('safsdf', is_string=False, default=100)
        self.assertEqual(a, 1)
        self.assertEqual(b, True)
        self.assertEqual(c, 'asdfasdf')
        self.assertEqual(d, 100)
