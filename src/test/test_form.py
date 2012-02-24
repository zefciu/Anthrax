import unittest

from anthrax.form import Form
from anthrax.field import TextField

class Test(unittest.TestCase):
    """Test basic form features"""

    def setUp(self):
        self.form = Form(fields = [
            TextField(
                name='name',
                regexp=r'^[A-Z][a-z]+$',
                regexp_message='Write your name with a capital',
                max_len=20,
                max_len_message='You must be kidding!',
            ),
            TextField('nickname', max_len=30),
        ])

    def test_valid(self):
        """Testing a completely valid flow"""
        result = self.form.handle_raw_input({
            'name': 'Galahad', 'nickname': 'the Pure'
        })
        self.assertTrue(result)
        self.assertTrue(self.form.valid)
        self.assertDictEqual(dict(self.form), {
            'name': 'Galahad', 'nickname': 'the Pure'
        })

    def test_invalid_regexp(self):
        """Testing an error with input unmatching regexp"""
        result = self.form.handle_raw_input({
            'name': 'galahad', 'nickname': 'the Pure'
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
            'name': 'Galahahahahahahahahaahahaddd', 'nickname': 'the Pure'
        })
        self.assertFalse(result)
        self.assertFalse(self.form.valid)
        self.assertEqual(
            self.form.errors['name'].message,
            'You must be kidding!'
        )
