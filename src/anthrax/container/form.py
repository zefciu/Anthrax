import abc
import weakref

from collections import Mapping, OrderedDict
from anthrax.exc import ValidationError, FormValidationError
from anthrax.field.base import Field
from anthrax.util import load_entry_point
from anthrax.frontend import Frontend
from anthrax.container.base import Container

class Form(Container):

    __stop_on_first__ = False

    def __init__(self):
        self._frontend_name_cache = None
        self._load_frontend()
        super(Form, self).__init__()

    @Container.__raw__.setter
    def __raw__(self, dict_):
        """Accepts a dictionary of raw values. Returns True on success and
        False on errors"""
        valid = True
        self.raw_values = dict_
        for k, v in dict_.items():
            field = self.__fields__[k]    
            field_parent = field.__parent__
            key = k.rsplit('-', 1)[-1]
            try:
                field_parent._values[key] = field._raw2python(v, self)
            except ValidationError as err:
                field_parent._errors[key] = err
                if self.__stop_on_first__:
                    return False
                valid = False
        if valid:
            self._run_validators()
        return valid

    def _load_frontend(self):
        if isinstance(self.__frontend__, Frontend):
            self._frontend = self.__frontend__
        elif self._frontend_name_cache != self.__frontend__:
            self._frontend_name_cache = self.__frontend__
            self._frontend = load_entry_point(
                'anthrax.frontend', self.__frontend__, 'frontend'
            )

    def render(self):
        self._load_frontend()
        return self._frontend.form_view(self)
