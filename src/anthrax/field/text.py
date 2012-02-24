""""""
from anthrax.field.base import Field

class TextField(Field):
    """Simple field that represents a string. Inherits
    regexp, min_len, and max_len arguents available."""

    def to_python(self, value):
        return super(TextField, self).to_python(value)

    def from_python(self, value):
        return super(TextField, self).from_python(value)
