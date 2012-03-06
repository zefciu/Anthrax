import abc
import weakref

from collections import Mapping, OrderedDict
from anthrax.exc import ValidationError
from anthrax.field.base import Field
from anthrax.util import load_entry_point
from anthrax.frontend import Frontend

class FormMeta(abc.ABCMeta):

    @classmethod
    def __prepare__(mcls, clsname, bases):
        return OrderedDict()

    def __init__(cls, clsname, bases, dict_):
        cls.fields = OrderedDict()
        for fname, field in dict_.items():
            if not isinstance(field, Field):
                continue
            field.name = fname
            cls.fields[fname] = field
        super(FormMeta, cls).__init__(clsname, bases, dict_)

class RawDict(Mapping):
    def __init__(self, form):
        self.form = form

    def __getitem__(self, key):
        field = self.form.fields[key]
        value = self.form.get(key, None)
        if value:
            return field._python2raw(self.form[key])
        else:
            return ''

    def __iter__(self):
        return iter(self.form)

    def __len__(self):
        return len(form)

class Form(Mapping, metaclass=FormMeta):

    __frontend__ = abc.abstractproperty()
    __stop_on_first__ = False

    def __init__(self):
        self._frontend_name_cache = ''
        self._load_frontend()
        for fname, field in self.fields.items():
            w = self._frontend.negotiate_widget(field)
            field.widget = w
            field.form = weakref.proxy(self)
            w.field = field # weakref.proxy(field)
        self.raw = RawDict(self)
        self.reset()

    def __iter__(self):
        return iter(self.values)

    def __len__(self):
        return len(self.values)

    def __getitem__(self, key):
        return self.values[key]

    def __setitem__(self, key, value):
        field = self.fields[key]
        self.raw_values[key] = field._python2raw(value) # First as it can fail
        self.values[key] = value

    def __delitem__(self, key):
        del self.values[key]

    def _load_frontend(self):
        if isinstance(self.__frontend__, Frontend):
            self._frontend = self.__frontend__
            return
        if self._frontend_name_cache == self.__frontend__:
            return
        self._frontend = load_entry_point(
            'anthrax.frontend', self.__frontend__, 'frontend'
        )
        self._frontend_name_cache = self.__frontend__

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
                if self.__stop_on_first__:
                    return False
                valid = False
        return valid

    def render(self):
        self._load_frontend()
        return self._frontend.form_view(self)
