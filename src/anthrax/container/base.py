import abc
import weakref
from collections import Sequence, Mapping, OrderedDict

from decorator import decorator

from anthrax.field.base import Field, BoundField
from anthrax.frontend import Frontend
from anthrax.exc import FormValidationError
from anthrax.reflector import TOP, BOTTOM, BEFORE, AFTER
from anthrax.util import load_entry_point

def add_child(parent, name, item, mode):
    attr = 'place' if mode == 'field' else '__place__'
    if name in parent:
        del parent[name]
    place = getattr(item, attr, BOTTOM)
    if place == BOTTOM:
        parent[name] = item
    elif place == TOP:
        parent[name] = item
        parent.move_to_end(name, False)
    elif isinstance(place, tuple):
        place, rel = place
        #Copy the keys, so we can modify them while iterating on the fly
        keys = list(parent.keys())
        if rel not in keys:
            raise ValueError("Field with name '{}' doesn't exist".format(rel))
        if place == AFTER:
            for key in keys: 
                parent.move_to_end(key)
                if key == rel:
                    parent[rel] = item
        elif place == BEFORE:
            for key in reversed(keys): 
                parent.move_to_end(key, False)
                if key == rel:
                    parent[rel] = item
                    parent.move_to_end(rel, False)

def traverse(attrib=None):
    def wrap(fun):
        def do_traverse(fun, self, key, *args, **kwargs):
            if '-' in key:
                first, rest = key.split('-', 1)
                subcontainer = self._fields[first]
                if attrib is not None:
                    subcontainer = getattr(subcontainer, attrib)
                return getattr(
                    subcontainer, fun.__name__
                )(rest, *args, **kwargs)
            else:
                return fun(self, key, *args, **kwargs)
        return decorator(do_traverse, fun)
    return wrap


class ContainerMeta(abc.ABCMeta):
    @classmethod
    def __prepare__(mcls, clsname, bases):
        return OrderedDict()

    def __init__(cls, clsname, bases, dict_):
        subcontainers = []
        fields = None
        for base in bases:
            if hasattr(base, '__fields__'):
                if fields is None:
                    fields = base.__fields__.copy()
                else:
                    raise AttributeError(
                        "Sorry, can't handle this multiple inheritance"
                    )
        reflector = dict_.pop('__reflect__', None)
        if reflector is not None:
            if fields is not None:
                raise AttributeError(
                    "Sorry, can't use both inheritance and reflection"
                )
            if isinstance(reflector, tuple):
                name, source = reflector
                ReflectorClass = load_entry_point(
                    'anthrax.reflector', name, 'reflector'
                )
                reflector = ReflectorClass(source)
            fields = reflector.get_fields(cls)
        if fields is None:
            fields = OrderedDict()
        
        for itemname, item in dict_.items():
            if item is None and itemname in fields:
                del fields[itemname]
            if isinstance(item, Field):
                item.name = itemname
                add_child(fields, itemname, item, 'field')
            if isinstance(item, ContainerMeta):
                item = ContainerMeta(
                    itemname, (item,), {
                        '__name__': itemname
                    }
                )
                add_child(fields, itemname, item, 'container')
                subcontainers.append(item)
            if isinstance(item, Mapping) and not isinstance(item, Container):
                # This is a configuration for a previously reflected field.
                field = fields[itemname]
                for k, v in item.items():
                    setattr(field, k, v)
        cls.__fields__ = fields
        cls.__subcontainers__ = subcontainers
        super(ContainerMeta, cls).__init__(clsname, bases, dict_)




class ErrorDict(Mapping):
    def __init__(self, owner):
        self.owner = weakref.proxy(owner)
        self._fields = owner._fields

    @traverse('__errors__')
    def __getitem__(self, key):
        return self.owner._errors.get(key)

    def __iter__(self):
        return iter(self.owner)

    def __len__(self):
        return len(self.owner)


class RawDict(Mapping):
    def __init__(self, owner):
        self.owner = owner
        self._fields = owner._fields

    @traverse('__raw__')
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

    @traverse('__fields__')
    def __getitem__(self, key):
        return self._fields[key]

    def __iter__(self):
        return iter(self.owner)

    def __len__(self):
        return len(self.owner)

class Container(Mapping, metaclass=ContainerMeta):
    __validators__ = []

    def __init__(self, mode=None):
        self._load_validators()
        self._mode = mode
        fields = OrderedDict()
        subcontainers = []
        for fname, field in type(self).__fields__.items():
            if isinstance(field, Field):
                if (
                    mode is not None and
                    field.mode is not None and
                    mode != field.mode
                ):
                    continue
                field = BoundField(field, self)
            if isinstance(field, ContainerMeta):
                field = field(mode)
                subcontainers.append(field)
            fields[fname] = field
        self._fields = fields
        self.__fields__ = FieldsDict(self)
        self.__errors__ = ErrorDict(self)
        self.__subcontainers__ = subcontainers
        self.__reset__()

    def _load_validators(self):
        self._validators = []
        for validator in self.__validators__:
            if isinstance(validator, tuple):
                validator_name = validator[0]
                if isinstance(validator[-1], Mapping):
                    kwargs = validator[-1]
                    fields = validator[1:-1]
                else:
                    kwargs = {}
                    fields = validator[1:]
                validator_callable = load_entry_point(
                    'anthrax.validator', validator_name, 'validator'
                )
                def validator_wrapper(form):
                    try:
                        values = [form[field] for field in fields]
                        validator_callable(form, *values, **kwargs)
                    except FormValidationError as err:
                        err.fields = fields
                        raise err
                validator_wrapper.__name__ = validator_name
                self._validators.append(validator_wrapper)

            else:
                self._validators.append(validator)


    def _negotiate_widgets(self):
        for field in self._fields.values():
            if isinstance(field, Field):
                w = self._frontend.negotiate_widget(field)
                field.widget = w
                w.field = weakref.proxy(field)
            if isinstance(field, Container):
                field._frontend = self._frontend
                field._negotiate_widgets()

    @property
    def mode(self):
        return self._mode

    @property
    def __valid__(self):
        """Returns true if form is valid"""
        return (
            not bool(self._errors) and 
            all (sub.__valid__ for sub in self.__subcontainers__)
        )

    @property
    def __raw__(self):
        return RawDict(self)

    def __reset__(self):
        """Resets the container. Clears all fields and errors"""
        self._values = {}
        self._errors = {}
        (f.__reset__() for f in self.__subcontainers__)

    def __iter__(self):
        return iter(self._fields)

    def __len__(self):
        return len(self._fields)

    @traverse()
    def __getitem__(self, key):
        return self._values[key]

    @traverse()
    def __delitem__(self, key):
        del self._values[key]

    @traverse()
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
                    self._errors[field] = err
                valid = False
        for subcontainer in self.__subcontainers__:
            subcontainer._run_validators()
        return valid
