"""Generic comparison validators."""
from anthrax.exc import FormValidationError

def equals(self, *values):
    first_value = values[0]
    for value in values[1:]:
        if value != first_value:
            raise FormValidationError(
                fields=[], message='Fields should be equal.'
            )
