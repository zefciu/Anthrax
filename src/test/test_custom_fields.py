import unittest

from anthrax.field import IntegerField
from anthrax.container import Form
from anthrax.exc import ValidationError

class EvenInteger(IntegerField):
    """This field only accepts even integers"""

    def validate_python(self, value):
        if value % 2:
            raise ValidationError('You must provide even number')

class Test(unittest.TestCase):
    """Test field customization"""

    def testValidatePython(self):
        """Test a field with validate_python overridden"""

        class SwallowForm(Form):
            swallow_count = EvenInteger()

        form = SwallowForm()
        form.__raw__ = {'swallow_count': '4'}
        self.assertTrue(form.__valid__)
        form.__raw__ = {'swallow_count': '5'}
        self.assertFalse(form.__valid__)
        self.assertEqual(
            form.__errors__['swallow_count'].message,
            'You must provide even number'
        )
        def wrong():
            form['swallow_count'] = 7
        self.assertRaises(ValueError, wrong)
