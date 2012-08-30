import unittest

from anthrax.container.form import Form
from anthrax.exc import FormValidationError
from anthrax.field import TextField, IntegerField
from util import dummy_frontend, UnsupportedField

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

    def test_render(self):
        self.assertEqual(self.form.render(), 'form')
        self.assertEqual(self.form.__fields__['name'].render(), 'input')

    def test_failed_negotiation(self):
        class WrongForm(Form):
            __frontend__ = dummy_frontend
            name = UnsupportedField()
        form = WrongForm()
        def wrong():
            form.render()
        self.assertRaises(NotImplementedError, wrong)
