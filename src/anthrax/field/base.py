import abc
import re
from gettext import gettext as _

from anthrax.exc import ValidationError

class BoundField(object):
    def __init__(self, form):
        self.field = form


    def __getattr__(self, key):
        return getattr(self.field, key)


class Field(object, metaclass=abc.ABCMeta):
    """Abstract Field class. Fields encapsulate validation and
encoding/decoding logic. Non-abstract children of Field class should
override at least to_python() and from_python() methods. Constructor arguments:
        
label:
    The label to display before the field

regexp:
    The regular expression that raw values should match. Don't pass a compiled
    regexp here. The string will be compiled at creation.

regexp_message:
    An error message to display when the value doesn't match the regexp.
    It can contain a {regexp} placeholder.

min_len:
    Minimum length of raw value

min_len_message:
    An error message to display when the value is shorter than min_len. 
    Can contain a {min_len} placeholder.

max_len:
    Maximum length of raw value

max_len_message:
    An error message to display when the value is longer than max_len. 
    Can contain a {max_len} placeholder.

widgets:
    Widgets that can represent this field. Preferred ones should be put in
    front.
    """

    regexp = None
    regexp_message = _('Value should match regexp {regexp}')
    _regexp_compiled = None
    min_len = None
    min_len_message = _("Value can't be shorter than {min_len}")
    max_len = None
    max_len_message = _("Value can't be longer than {max_len}")
    label = _('')

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __get__(self, inst, cls):
        return BoundField(inst)

    @property
    def value(self):
        if not hasattr(self, 'form'):
            raise AttributeError('Unbound field')
        return self.form.get(self.name, None)

    @property
    def raw_value(self):
        v = self.value
        if self.value is None:
            return ''
        else:
            return self._python2raw(self.value)

    @property
    def regexp_compiled(self):
        if self._regexp_compiled is None and self.regexp is not None:
            self._regexp_compiled = re.compile(self.regexp)
        return self._regexp_compiled
        
    widgets = abc.abstractproperty()
    
    @abc.abstractmethod
    def to_python(self, value):
        """Transform the raw, string value into a python object possibly
        raising ValidationError. This method is meant to be overridden by
        child classes"""
        return value

    @abc.abstractmethod
    def from_python(self, value):
        """Transform a python object into renderable string. This method is
        meant to be overridden by child classes."""
        return str(value)

    def validate_raw(self, value):
        """Validate raw value. Don't return anything. Possibly raise
        ValidationError."""
        pass


    def validate_python(self, value):
        """Validate python object. Don't return anything. Possibly raise
        ValidationError."""
        pass

    def _declarative_raw_validation(self, value):
        """This method is called as a part of validation process on the raw
        value. You should override it if you add more declarative validation
        parameters (like regexp or min_len)."""
        len_ = len(value)
        if self.regexp is not None:
            if not self.regexp_compiled.match(value):
                raise ValidationError(
                    message = self.regexp_message.format(regexp=self.regexp)
                )
        if self.min_len is not None and len_ < self.min_len:
            raise ValidationError(
                message=self.min_len_message.format(min_len=self.min_len)
            )
        if self.max_len is not None and len_ > self.max_len:
            raise ValidationError(
                message=self.max_len_message.format(max_len=self.max_len)
            )

    def _declarative_python_validation(self, value):
        """This method is called as a part of validation process on the python
        object. You should override it if you add more declarative validation
        parameters."""
        pass 

    def _raw2python(self, rvalue, form):
        """This method shouldn't normally be overridden. It is called by Form
        object to process the raw value."""
        self._declarative_raw_validation(rvalue)
        self.validate_raw(rvalue)
        pvalue = self.to_python(rvalue)
        self._declarative_python_validation(pvalue)
        self.validate_python(pvalue)
        return pvalue

    def _python2raw(self, pvalue):
        """This method shouldn't normally be overridden. It is called by Form
        object to process the python object."""
        try:
            self.validate_python(pvalue)
        except ValidationError as err:
            raise ValueError(
                'This value is invalid. Validator said: {0}'.format(
                    err.message
                )
            )
        return self.from_python(pvalue)

    def render(self):
        return self.widget.render()
