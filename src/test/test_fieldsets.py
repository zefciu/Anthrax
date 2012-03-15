import unittest

from anthrax.field import TextField, IntegerField
from anthrax.container import Container, Form
from anthrax.exc import FormValidationError
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
            class personals(Container):
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
            'personals-name': 'Galahad', 'personals-nickname': 'the Pure',
            'age': '25',
        }
        self.assertTrue(self.form.__valid__)
        self.assertEqual(self.form['personals-name'], 'Galahad')
        self.assertEqual(self.form['age'], 25)
        
    def test_invalid(self):
        """Testing a completely valid flow"""
        self.form.__raw__ = {
            'personals-name': 'Galahad', 'personals-nickname': 'the Dirty',
            'age': '25',
        }
        self.assertFalse(self.form.__valid__)
        self.assertEqual(
             self.form.__errors__['personals-name'].message,
            'Sir Galahad must be pure'
        )
