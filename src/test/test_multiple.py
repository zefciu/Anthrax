import unittest

from anthrax.container.form import Form
from anthrax.field import TextField, IntegerField
from util import dummy_frontend

class Test(unittest.TestCase):
    """Testing if two forms of same class are handled correctly"""

    def setUp(self):
        class TestForm(Form):
            __frontend__ = dummy_frontend
            name = TextField(
                regexp=r'^[A-Z][a-z]+$',
                regexp_message='Write your name with a capital',
                max_len=20, max_len_message='You must be kidding!',
            )
            nickname = TextField(max_len=30)
            age = IntegerField(min=7, max=99)
        self.form1 = TestForm()
        self.form2 = TestForm()

    def test_valid(self):
        """Testing a valid flow in two forms"""
        self.form1.__raw__ = {
            'name': 'Galahad', 'nickname': 'the Pure', 'age': '25',
        }
        self.form2.__raw__ = {
            'name': 'Lancelot', 'nickname': 'the Brave', 'age': '28',
        }
        self.assertTrue(self.form1.__valid__)
        self.assertTrue(self.form2.__valid__)
        self.assertDictEqual(dict(self.form1), {
            'name': 'Galahad', 'nickname': 'the Pure', 'age': 25,
        })
        self.assertDictEqual(dict(self.form2), {
            'name': 'Lancelot', 'nickname': 'the Brave', 'age': 28,
        })
