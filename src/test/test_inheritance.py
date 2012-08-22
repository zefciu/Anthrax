import unittest

from anthrax.container.form import Form
from anthrax.exc import FormValidationError
from anthrax.field import TextField, IntegerField
from util import dummy_frontend

class Test(unittest.TestCase):
    """Testing inheritance of forms."""

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
        self.TestForm = TestForm

    def testRemoveField(self):
        class FormWithoutAge(self.TestForm):
            age = None
        form = FormWithoutAge()
        assert 'age' not in form.__fields__

    def testOverrideField(self):
        class FormWithDifferentAge(self.TestForm):
            age = IntegerField(min=12, max=30)
        form = FormWithDifferentAge()
        assert 'age' in form.__fields__
        self.assertEqual(form.__fields__['age'].min, 12)
        self.assertEqual(form.__fields__['age'].max, 30)
