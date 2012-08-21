import cgi
import mimetypes

from gettext import gettext as _
from anthrax.field.base import Field
from anthrax.widget import FileUpload, TextInput
from anthrax.exc import ValidationError

class AnthraxFileWrapper(object):
    """A common interface for differently stored files."""
    def __init__(self, arg):
        if isinstance(arg, cgi.FieldStorage):
            self.file = arg.file
            self.mimetype = arg.type
            self.field_storage = arg
        elif isinstance(arg, str):
            self.filename = arg
            self.file = open(arg, 'r')
            self.mimetype = mimetypes.guess_type(arg)
        else:
            raise TypeError("Can't instantiate wrapper with {}!".format(
                type(arg)))
            

class FileField(Field):
    """Field that represents a file (uploaded or server side).
    * accept_mime - A mimetype or an iterable of them that are available for
    this field. Asterisks can be used.
    * directory - A directory on the disk that is available for server-side
    files.
    """
    accept_mime = {'*/*'}
    widgets = [FileUpload, TextInput]

    def __init__(self, *args, **kwargs):
        super(FileField, self).__init__(*args, **kwargs)
        if isinstance(self.accept_mime, str):
            self.accept_mime = {self.accept_mime}
        if not isinstance(self.accept_mime, set):
            self.accept_mime = set(self.accept_mime)

    def to_python(self, value):
        return AnthraxFileWrapper(value)

    def from_python(self, value):
        return None

    def validate_raw(self, value):
        if isinstance(value, str):
            if os.path.commonprefix([value, self.directory]) != self.directory:
                raise ValidationError(_('Invalid directory'))

    def validate_python(self, value):
        maintype, subtype = value.mimetype.split('/')
        possible_mimetypes = {
            value.mimetype, maintype + '/*', '*/' + subtype, '*/*'
        }
        if not possible_mimetypes & self.accept_mime:
            raise ValidationError(_('Invalid mime'))

    def _declarative_raw_validation(self, value):
        pass
