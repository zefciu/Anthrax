import unittest

from anthrax.form import Form
from anthrax.field import TextField, IntegerField
from util import dummy_frontend

class Test(unittest.TestCase):
    """Test basic form features"""

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
        self.form = TestForm()

    def test_valid(self):
        """Testing a completely valid flow"""
        result = self.form.handle_raw_input({
            'name': 'Galahad', 'nickname': 'the Pure', 'age': '25',
        })
        self.assertTrue(result)
        self.assertTrue(self.form.valid)
        self.assertDictEqual(dict(self.form), {
            'name': 'Galahad', 'nickname': 'the Pure', 'age': 25,
        })

    def test_invalid_regexp(self):
        """Testing an error with input unmatching regexp"""
        result = self.form.handle_raw_input({
            'name': 'galahad', 'nickname': 'the Pure', 'age': '25'
        })
        self.assertFalse(result)
        self.assertFalse(self.form.valid)
        self.assertEqual(
            self.form.errors['name'].message,
            'Write your name with a capital'
        )

    def test_too_long(self):
        """Testing an error with input too long"""
        result = self.form.handle_raw_input({
            'name': 'Galahahahahahahahahaahahaddd', 'nickname': 'the Pure',
            'age': '25'
        })
        self.assertFalse(result)
        self.assertFalse(self.form.valid)
        self.assertEqual(
            self.form.errors['name'].message,
            'You must be kidding!'
        )

    def test_too_much(self):
        """Testing an error with input too high"""
        result = self.form.handle_raw_input({
            'name': 'Galahad', 'nickname': 'the Pure', 'age': '120'
        })
        self.assertFalse(result)
        self.assertFalse(self.form.valid)
        self.assertEqual(
            self.form.errors['age'].message,
            "Value can't be higher than 99."
        )
        self.assertListEqual(self.form.errors['age'].suggestions, [99])
