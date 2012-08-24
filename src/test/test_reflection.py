import unittest

from anthrax.container import Form
from anthrax.field import TextField

import util
util.inject_entry_points()


class Test(unittest.TestCase):
    def setUp(self):
        class SwallowForm(Form):
            __reflect__ = ('swallow', None)
        self.form = SwallowForm

    def test_fields(self):
        self.assertListEqual(
            list(self.form.__fields__), ['continent', 'strength']
        )

    def test_conflict(self):
        def wrong():
            class Knight(Form):
                name = TextField()
            class SwallowForm(Knight):
                __reflect__ = ('swallow', None)

        self.assertRaises(AttributeError, wrong)
            

