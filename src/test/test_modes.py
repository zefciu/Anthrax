import unittest

from anthrax.field import MD, TextField, IntegerField
from anthrax.container import Container, Form
from util import dummy_frontend

KNIGHT = 'KNIGHT'
PEASANT = 'PEASANT'

class Test(unittest.TestCase):
    """Test basic form features"""

    def setUp(self):
        class TestForm(Form):
            __frontend__ = dummy_frontend
            class personals(Container):
                name = TextField(
                    regexp=MD({KNIGHT: r'^[A-Z][a-z]+$'}),
                    regexp_message='Write your name with a capital',
                    max_len=20, max_len_message='You must be kidding!',
                )
                nickname = TextField(max_len=30, mode=KNIGHT)
            age = IntegerField(min=7, max=99)
        self.TestForm = TestForm

    def test_no_mode(self):
        """Testing a form with no mode"""
        form = self.TestForm()
        self.assertTrue('personals-nickname' in form.__fields__)

    def test_mode_disabled(self):
        """Testing a form a mode disabling field"""
        form = self.TestForm(PEASANT)
        self.assertEqual(form.mode, PEASANT)
        self.assertFalse('personals-nickname' in form.__fields__)

    def test_mode_enabled(self):
        """Testing a form a mode enabling field"""
        form = self.TestForm(KNIGHT)
        self.assertTrue('personals-nickname' in form.__fields__)

    def test_mode_enabled_validation(self):
        """Test a situation when the mode enables validation"""
        form = self.TestForm(KNIGHT)
        form.__raw__ = {
            'personals-name': 'galahad', 'personals-nickname': 'the Pure',
            'age': '25',
        }
        self.assertFalse(form.__valid__)

    def test_mode_disabled_validation(self):
        """Test a situation when the mode enables validation"""
        form = self.TestForm(PEASANT)
        form.__raw__ = {
            'personals-name': 'patsy', 'age': '40',
        }
        self.assertTrue(form.__valid__)
