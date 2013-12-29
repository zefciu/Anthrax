"""Boolean field definition."""

from anthrax.field.base import Field
from anthrax.exc import ValidationError
from anthrax import widget as w


class BoolField(Field):
    """Boolean field's python value is ``True`` or ``False``. It's raw value
    can be defined as a list of possible vals for ``True``."""

    true_values = ['true']
    widgets = [w.Checkbox]

    def to_python(self, value, bf):
        return value in self.true_values

    def from_python(self, value, bf):
        if value:
            return self.true_values[0]

    def validate_python(self, value, bf):
        if self.required and not value:
            raise ValidationError(self.required_message)
        super(BoolField, self).validate_python(value, bf)
