import abc
import weakref

from collections import Mapping, OrderedDict
from anthrax.exc import ValidationError, FormValidationError
from anthrax.util import load_entry_point
from anthrax.frontend import Frontend
from anthrax.container.base import Container


class Form(Container):
    """A form is a top-level container. It is on the form where the raw 
    data should be assigned and which should be rendered."""

    def __init__(self, mode=None, **kwargs):
        self._frontend_name_cache = None
        self.kwargs = kwargs
        super(Form, self).__init__(mode)

    @Container.__raw__.setter
    def __raw__(self, dict_):
        """Accepts a dictionary of raw values. Returns True on success and
        False on errors"""
        self.raw_values = {}
        state = {'valid': True}
        def set_value(key, field):
            value = dict_.get(key, '')
            if key.endswith('s[]'): # e.g. dojo does this
                key = key[:-3]
            field_parent = field.parent
            key_proper = key.rsplit('-', 1)[-1]
            try:
                field_parent._values[key_proper] = field._raw2python(value)
            except ValidationError as err:
                field_parent._errors[key] = err
                state['valid'] = False
        for key, field in self.__fields__.iter_fields():
            set_value(key, field)
        if state['valid']:
            self._run_validators()
        return state['valid']

    def _load_frontend(self):
        if isinstance(self.__frontend__, Frontend):
            self._frontend = self.__frontend__
        elif self._frontend_name_cache != self.__frontend__:
            self._frontend_name_cache = self.__frontend__
            self._frontend = load_entry_point(
                'anthrax.frontend', self.__frontend__, 'frontend'
            )
        else:
            return
        self._negotiate_widgets()

    def render(self):
        """Render the form in configured frontend."""
        self._load_frontend()
        return self._frontend.form_view(self)
