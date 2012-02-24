from collections import Mapping
from anthrax.exc import ValidationError

class Form(Mapping):
    def __init__(self, fields):
        if not isinstance(fields, Mapping):
            fields = dict((f.name, f) for f in fields)
        self.stop_on_first = False
        self.fields = fields
        self.reset()

    def __iter__(self):
        return iter(self.fields)

    def __len__(self):
        return len(self.fields)

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        field = self.fields[key]
        self.raw_values[key] = field._python2raw(value) # First as it can fail
        self.values[key] = value

    def __delitem__(self, key):
        del self.values[key]

    def reset(self):
        """Resets the form. Clears all fields and errors"""
        self.values = {}
        self.errors = {}

    @property
    def valid(self):
        """Returns true if form is valid"""
        return not bool(self.errors)

    def handle_raw_input(self, dict_):
        """Accepts a dictionary of raw values. Returns True on success and
        False on errors"""
        valid = True
        self.raw_values = dict_
        for k, v in dict_.items():
            field = self.fields[k]    
            try:
                self.values[k] = field._raw2python(v, self)
            except ValidationError as err:
                self.errors[k] = err
                if self.stop_on_first:
                    return False
                valid = False
        return valid
