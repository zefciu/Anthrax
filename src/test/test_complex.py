import unittest

from anthrax.container.form import Form
from anthrax.field import ListField, TextField
from util import dummy_frontend

class Test(unittest.TestCase):
    """Testing complex fields"""

    def setUp(self):
        class TestForm(Form):
            __frontend__ = dummy_frontend
            names = ListField(subfield=TextField(
                regexp=r'^[A-Z][a-z]+$',
                regexp_message='Write your name with a capital',
                max_len=20, max_len_message='You must be kidding!',
            ))
        self.form1 = TestForm()

    def test_valid(self):
        """Testing a valid flow in two forms"""
        self.form1.__raw__ = {
            'names': 'Galahad\n\nLancelot\n\rArthur\rPansy',
        }
        self.assertTrue(self.form1.__valid__)
        self.assertDictEqual(dict(self.form1), {
            'names': ['Galahad', 'Lancelot', 'Arthur', 'Pansy']
        })

    def test_invalid(self):
        self.form1.__raw__ = {
            'names': 'Galahad\n\nlancelot\n\rArthur\rPansy',
        }
        self.assertFalse(self.form1.__valid__)
        self.assertEqual(
            self.form1.__errors__['names'].message,
            'Write your name with a capital'
        )
