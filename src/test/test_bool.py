import unittest

from anthrax.container import Form
from anthrax.field import BoolField


class TestBool(unittest.TestCase):
    """Tests for BoolField."""

    def setUp(self):
        class TestForm(Form):
            knight = BoolField(
                required=True, required_message='You must be a knight',
            )
            pure = BoolField(required=False)
        self.form = TestForm()

    def test_valid(self):
        """Test a valid submission"""
        self.form.__raw__ = {'knight': 'true'}
        self.assertEqual(self.form['knight'], True)
        self.assertEqual(self.form['pure'], False)

    def test_required_empty(self):
        """Test a submission without required checkbox"""
        self.form.__raw__ = {'pure': 'true'}
        self.assertFalse(self.form.__valid__)
        self.assertEqual(
            self.form.__errors__['knight'].message,
            'You must be a knight',
        )
