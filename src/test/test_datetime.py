import unittest
import datetime

from anthrax.container import Form
from anthrax.field import DateField

class Test(unittest.TestCase):

    def setUp(self):
        class TestForm(Form):
            born = DateField()

        self.form = TestForm()

    def test_valid(self):
        """Test a valid submission"""
        self.form.__raw__ = {'born': '29-03-1982'}
        self.assertTrue(self.form.__valid__)
        self.assertEqual(self.form['born'], datetime.date(1982, 3, 29))

    def test_misformed(self):
        """Test an invalid submission"""
        self.form.__raw__ = {'born': '299-03-1982'}
        self.assertFalse(self.form.__valid__)

    def test_to_raw(self):
        """Test to-raw conversion."""
        self.form['born'] = datetime.date(1982, 3, 29) 
        self.assertEqual(self.form.__raw__['born'], '29-03-1982')
        self.form['born'] = None
        self.assertEqual(self.form.__raw__['born'], '')
