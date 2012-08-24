import unittest

from anthrax.container import Form, Container
from anthrax.field import TextField, IntegerField
from util import dummy_frontend

class Test(unittest.TestCase):

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
        class TestForm2(Form):
            __frontend__ = dummy_frontend
            class personals(Container):
                name = TextField(
                    regexp=r'^[A-Z][a-z]+$',
                    regexp_message='Write your name with a capital',
                    max_len=20, max_len_message='You must be kidding!',
                )
                nickname = TextField(max_len=30)
            age = IntegerField(min=7, max=99)
        self.form2 = TestForm2()

    def test_conversion(self):
        """Test a 'to raw' conversion."""
        self.form['name'] = 'Sir Galahad'
        self.form['nickname'] = 'The Pure'
        self.form['age'] = 20
        self.assertDictEqual(dict(self.form.__raw__), {
            'name': 'Sir Galahad', 'nickname': 'The Pure', 'age': '20'
        })

    def test_nested_conversion(self):
        """Test a 'to raw' conversion with fieldsets."""
        self.form2['personals-name'] = 'Sir Galahad'
        self.form2['personals-nickname'] = 'The Pure'
        self.form2['age'] = 20
        self.assertDictEqual(dict(self.form2.__raw__), {
            'personals': {'name': 'Sir Galahad', 'nickname': 'The Pure'},
            'age': '20'
        })

    def test_empty(self):
        """Test a raw value of an empty form."""
        self.assertEqual(len(self.form.__raw__), 3)
        self.assertDictEqual(dict(self.form.__raw__), {
            'name': '', 'nickname': '', 'age': ''
        })
