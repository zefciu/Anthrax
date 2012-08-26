import unittest
from anthrax.container import Form
from anthrax.field import TextField, IntegerField

class Test(unittest.TestCase):
    def setUp(self):
        class TestForm(Form):
            __validators__ = [
                ('equals', 'password', 'repeat_password'), 
                # This offer is only for people that started looking for Graal
                # between 7 and 18
                (
                    'difference', 'looking_for_graal', 'age',
                    {'min': 7, 'max': 18}
                ), 
            ]
            name = TextField()
            password = TextField()
            repeat_password = TextField()
            # This offer is only for people that started looking for Graal
            # between 7 and 18
            age = IntegerField()
            looking_for_graal = IntegerField()
        self.form = TestForm()

    def test_valid(self):
        self.form.__raw__ = {
            'name': 'Sir Lancelot', 'password': 'Guinevre69',
            'repeat_password': 'Guinevre69', 'age': '25',
            'looking_for_graal': '17',
        }
        self.assertTrue(self.form.__valid__)

    def test_password_mismatch(self):
        self.form.__raw__ = {
            'name': 'Sir Lancelot', 'password': 'Guinevre69',
            'repeat_password': 'Giunevre69', 'age': '25',
            'looking_for_graal': '17',

        }
        self.assertFalse(self.form.__valid__)

    def test_diff_too_low(self):
        self.form.__raw__ = {
            'name': 'Sir Lancelot', 'password': 'Guinevre69',
            'repeat_password': 'Guinevre69', 'age': '25',
            'looking_for_graal': '21',

        }
        self.assertFalse(self.form.__valid__)

    def test_diff_too_high(self):
        self.form.__raw__ = {
            'name': 'Sir Lancelot', 'password': 'Guinevre69',
            'repeat_password': 'Guinevre69', 'age': '25',
            'looking_for_graal': '2',

        }
        self.assertFalse(self.form.__valid__)
