import unittest
from anthrax.container import Form
from anthrax.field import TextField

class Test(unittest.TestCase):
    def setUp(self):
        class TestForm(Form):
            __validators__ = [('equals', 'password', 'repeat_password')]
            name = TextField()
            password = TextField()
            repeat_password = TextField()
        self.form = TestForm()

    def test_valid(self):
        self.form.__raw__ = {
            'name': 'Sir Lancelot', 'password': 'Guinevre69',
            'repeat_password': 'Guinevre69'
        }
        self.assertTrue(self.form.__valid__)

    def test_invalid(self):
        self.form.__raw__ = {
            'name': 'Sir Lancelot', 'password': 'Guinevre69',
            'repeat_password': 'Giunevre69'
        }
        self.assertFalse(self.form.__valid__)
