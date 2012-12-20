import unittest
import datetime

from anthrax.container import Form
from anthrax.field import ChoiceField

class Test(unittest.TestCase):

    def setUp(self):
        class TestForm(Form):
            occupation = ChoiceField(
                choices = [
                    ('KNG', 'Kings'),
                    ('KNI', 'Knights'),
                    ('PEA', 'Peasants'),
                ]
            )
            looking_for = ChoiceField(
                choices = ['Love', 'Grail']
            )

        self.form = TestForm()

    def test_get_choices(self):
        self.assertListEqual(
            list(self.form.__fields__['occupation'].get_system_choices()),
            ['KNG', 'KNI', 'PEA']
        )
        self.assertListEqual(
            list(self.form.__fields__['occupation'].get_display_choices()),
            ['Kings', 'Knights', 'Peasants']
        )

    def test_valid(self):
        """Test a valid submission"""
        self.form.__raw__ = {'occupation': 'KNI', 'looking_for': 'Love'}
        self.assertTrue(self.form.__valid__)
        self.assertEqual(self.form['occupation'], 'KNI')
        self.assertEqual(self.form['looking_for'], 'Love')

    def test_invalid_typo(self):
        """Test an invalid submission. Typo"""
        self.form.__raw__ = {'occupation': 'KNI', 'looking_for': 'Lve'}
        self.assertFalse(self.form.__valid__)

    def test_invalid_display(self):
        """Test an invalid submission. Display value given"""
        self.form.__raw__ = {'occupation': 'Knights', 'looking_for': 'Love'}
        self.assertFalse(self.form.__valid__)
