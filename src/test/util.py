from collections import OrderedDict
import pkg_resources as pr

from anthrax.frontend import Frontend
from anthrax.field import TextField, IntegerField
from anthrax.widget import FileUpload
from anthrax.reflector import Reflector
from anthrax.util import bind_fields

def form_view(*args, **kwargs):
    return 'form'

def input_view(*args, **kwargs):
    return 'input'

dummy_frontend = Frontend({
    'text_input': input_view,
    'not_installed': input_view,
}, form_view)

class UnsupportedField(TextField):
    widgets = ['file_upload']


class SwallowReflector(Reflector):
    """Dummy reflector that ignores input and always return same thing."""

    def get_fields(self, form):
        result = OrderedDict([
            ('continent', TextField()),
            ('strength', IntegerField()),
        ])
        bind_fields(result, form)
        return result

def inject_entry_points():
    dist = pr.get_distribution('Anthrax')
    pr.get_entry_map(dist).setdefault('anthrax.reflector', {}) 
    pr.get_entry_map(dist)['anthrax.reflector']['swallow'] = pr.EntryPoint.parse(
        'swallow = util:SwallowReflector', dist=dist
    )
