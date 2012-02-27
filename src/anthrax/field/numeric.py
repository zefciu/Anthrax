from gettext import gettext as _
from anthrax.field.ordered import OrderedField

class IntegerField(OrderedField):
    """Field that represents integer numbers"""
    regexp = r' *-?[\d ]+'
    regexp_message = _('Valid integer required')

    def to_python(self, value):
        return int(value)

    def from_python(self, value):
        return str(value)
