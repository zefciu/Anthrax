import unittest

from anthrax.container.form import Form
from anthrax.field import TextField, SlugField, IntegerField
from util import dummy_frontend

class Test(unittest.TestCase):
    """Test the slug field."""

    def setUp(self):
        class TestForm(Form):
            __frontend__ = dummy_frontend
            name = TextField(
                regexp=r'^[A-Z][a-z]+$',
                regexp_message='Write your name with a capital',
                max_len=20, max_len_message='You must be kidding!',
                min_len=3, min_len_message='Your name is kinda short!',
            )
            nickname = TextField(max_len=30)
            slug = SlugField(mirrored=nickname)
            age = IntegerField(min=7, max=99)
        self.form = TestForm()
        
    def test_auto(self):
        """Test an automatic slugification."""
        self.form.__raw__ = {
            'name': 'Galahad', 'nickname': 'the  Pure', 'age': '25',
            'slug': ''
        }
        self.assertEqual(self.form.__fields__['slug'].value, 'the-pure')

    def test_override(self):
        """Test if user can manually enter slug."""
        self.form.__raw__ = {
            'name': 'Galahad', 'nickname': 'the  Pure', 'age': '25',
            'slug': 'pure'
        }
        self.assertEqual(self.form.__fields__['slug'].value, 'pure')
