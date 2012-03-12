import unittest

from anthrax.form import Form
from anthrax.exc import FormValidationError
from anthrax.field import TextField, IntegerField
from util import dummy_frontend

class Test(unittest.TestCase):
    """Test basic form features"""

    def setUp(self):
        def purity_test(form):
            if form['name'] == 'Galahad' and form['nickname'] != 'the Pure':
                raise FormValidationError(
                    ['name', 'nickname'], 
                    'Sir Galahad must be pure',
                )
        class TestForm(Form):
            __frontend__ = dummy_frontend
            __validators__ = [purity_test]
            name = TextField(
                regexp=r'^[A-Z][a-z]+$',
                regexp_message='Write your name with a capital',
                max_len=20, max_len_message='You must be kidding!',
            )
            nickname = TextField(max_len=30)
            age = IntegerField(min=7, max=99)
        self.form = TestForm()

    def test_valid(self):
        """Testing a completely valid flow"""
        self.form.__raw__ = {
            'name': 'Galahad', 'nickname': 'the Pure', 'age': '25',
        }
        self.assertTrue(self.form.__valid__)
        self.assertDictEqual(dict(self.form), {
            'name': 'Galahad', 'nickname': 'the Pure', 'age': 25,
        })

    def test_invalid_regexp(self):
        """Testing an error with input unmatching regexp"""
        self.form.__raw__ = {
            'name': 'galahad', 'nickname': 'the Pure', 'age': '25'
        }
        self.assertFalse(self.form.__valid__)
        self.assertEqual(
            self.form.__errors__['name'].message,
            'Write your name with a capital'
        )

    def test_too_long(self):
        """Testing an error with input too long"""
        self.form.__raw__ = {
            'name': 'Galahahahahahahahahaahahaddd', 'nickname': 'the Pure',
            'age': '25'
        }
        self.assertFalse(self.form.__valid__)
        self.assertEqual(
            self.form.__errors__['name'].message,
            'You must be kidding!'
        )

    def test_too_much(self):
        """Testing an error with input too high"""
        self.form.__raw__ = {
            'name': 'Galahad', 'nickname': 'the Pure', 'age': '120'
        }
        self.assertFalse(self.form.__valid__)
        self.assertEqual(
            self.form.__errors__['age'].message,
            "Value can't be higher than 99."
        )
        self.assertListEqual(self.form.__errors__['age'].suggestions, [99])

    def test_impure(self):
        """Testing the formwise validator"""
        self.form.__raw__ = {
            'name': 'Galahad', 'nickname': 'the Promiscuous', 'age': '25'
        }
        self.assertFalse(self.form.__valid__)
        self.assertEqual(
            self.form.__errors__['name'].message,
            'Sir Galahad must be pure'
        )
        self.assertEqual(
            self.form.__errors__['nickname'].message,
            'Sir Galahad must be pure'
        )
