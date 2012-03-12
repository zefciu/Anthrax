import abc
import weakref
from collections import Sequence, Mapping, OrderedDict

from decorator import decorator

from anthrax.field.base import Field
from anthrax.frontend import Frontend
from anthrax.exc import FormValidationError

@decorator
def traverse(fun, self, key, *args, **kwargs):
    if isinstance(key, str) and '-' in key:
        key = key.split('-')
    if isinstance(key, Sequence) and not isinstance(key, str):
        if len(key) == 1:
            key = key[0]
        else:
            return getattr(self._fields[key[-1]], fun.__name__)
    return fun(self, key, *args, **kwargs)

class ContainerMeta(abc.ABCMeta):
    @classmethod
    def __prepare__(mcls, clsname, bases):
        return OrderedDict()

    def __init__(cls, clsname, bases, dict_):
        fields = OrderedDict()
        subcontainers = []
        for itemname, item in dict_.items():
            if isinstance(item, Field):
                item.name = itemname
                fields[itemname] = item
            if isinstance(item, ContainerMeta):
                item = ContainerMeta(
                    itemname, (item,), {
                        '__name__': itemname
                    }
                )
                fields[itemname] = item
                subcontainers.append(item)
        if fields:
            for base in bases:
                if hasattr(base, 'fields'):
                    raise AttributeError(
                        'Only one class in inheritance chain can define fields'
                        ' consider using unnamed fieldsets for more dynamic'
                        ' form creation.'
                    )
            cls.__fields__ = fields
            cls.__subcontainers__ = subcontainers
        super(ContainerMeta, cls).__init__(clsname, bases, dict_)

class RawDict(Mapping):
    def __init__(self, owner):
        self.owner = owner
        self._fields = owner._fields

    @traverse
    def __getitem__(self, key):
        field = self.owner.fields[key]
        value = self.owner.get(key, None)
        if isinstance(value, Container):
            return value
        if value:
            return field._python2raw(value)
        return ''


    def __iter__(self):
        return iter(self.owner)

    def __len__(self):
        return len(self.owner)

class FieldsDict(Mapping):
    def __init__(self, owner):
        self.owner = weakref.proxy(owner)

    @property
    def _fields(self):
        return self.owner._fields

    @traverse
    def __getitem__(self, key):
        return self._fields[key]

    def __iter__(self):
        return iter(self.owner)

    def __len__(self):
        return len(self.owner)

class Container(Mapping, metaclass=ContainerMeta):
    __validators__ = []

    def __init__(self):
        self._load_validators()
        fields = OrderedDict()
        for fname, field in type(self).__fields__.items():
            field.__parent__ = weakref.proxy(self)
            if isinstance(field, ContainerMeta):
                field = field()
            fields[fname] = field
        self._fields = fields
        self.__fields__ = FieldsDict(self)
        self.__reset__()

    def _negotiate_widgets(self):
        for field in self._fields:
            if isinstance(field, Field):
                w = self._frontend.negotiate_widget(field)
                field.widget = w
                w.field = weakref.proxy(field)
            if isinstance(field, Container):
                field._frontend = self._frontend
                field._negotiate_widgets()

    @property
    def __valid__(self):
        """Returns true if form is valid"""
        return (
            not bool(self.__errors__) and 
            all (sub.__valid__ for sub in self.__subcontainers__)
        )

    @property
    def __raw__(self):
        return RawDict(self)

    def __reset__(self):
        """Resets the container. Clears all fields and errors"""
        self._values = {}
        self.__errors__ = {}
        (f.__reset__() for f in self.__subcontainers__)

    def __iter__(self):
        return iter(self._fields)

    def __len__(self):
        return len(self._fields)

    @traverse
    def __getitem__(self, key):
        return self._values[key]

    @traverse
    def __delitem__(self, key):
        del self._values[key]

    @traverse
    def __setitem__(self, key, value):
        field = self.__fields__[key]
        self._raw_values[key] = field._python2raw(value) # First as it can fail
        self._values[key] = value

    def _run_validators(self):
        valid = True
        self._load_validators()
        for validator in self._validators:
            try:
                validator(self)
            except FormValidationError as err:
                for field in err.fields:
                    self.__errors__[field] = err
                valid = False
        for subcontainer in self.__subcontainers__:
            subcontainer._run_validators()
        return valid