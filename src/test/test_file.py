import unittest
import cgi
import os

from anthrax.container import Form
from anthrax.field import FileField
from util import dummy_frontend

HERE = os.path.dirname(os.path.abspath(__file__))

def _create_fs(mimetype, content):
    fs = cgi.FieldStorage()
    fs.file = fs.make_file()
    fs.type = mimetype
    fs.file.write(content)
    fs.file.seek(0)
    return fs

class Test(unittest.TestCase):
    """Test a form with file field"""

    def setUp(self):
        class TestForm(Form):
            __frontend__ = dummy_frontend
            resume = FileField(
                max_len=256,
                accept_mime=('text/*'),
                directory=HERE,
            )
        self.form = TestForm()

    def test_from_fs_ok(self):
        """Valid input by field storage."""
        fs = _create_fs('text/plain', 'Lorem ipsum dolor sit amet')
        self.form.__raw__ = {'resume': fs}
        self.assertTrue(self.form.__valid__)
        self.assertEqual(
            self.form['resume'].file.read(), 'Lorem ipsum dolor sit amet'
        )

    def test_from_filename_ok(self):
        """Valid input by field storage."""
        self.form.__raw__ = {'resume': 'lorem.txt'}
        self.assertTrue(self.form.__valid__)
        self.assertEqual(
            self.form['resume'].file.read(), 'Lorem ipsum dolor sit amet\n'
        )

    def test_from_abs_filename(self):
        """Trying to inject absolute filename should be illegal"""
        self.form.__raw__ = {'resume': '/usr/lib/lorem.txt'}
        self.assertFalse(self.form.__valid__)
        self.assertEqual(
            self.form.__errors__['resume'].message,
            "Absolute paths aren't allowed""",
        )

    def test_invalid_type(self):
        """Shouldn't happen. The file gets some strange type."""
        def wrong():
            self.form.__raw__ = {'resume': 42}
        self.assertRaises(TypeError, wrong)

    def test_wrong_mime(self):
        fs = _create_fs('application/x-python', 'print("Lorem ipsum")')
        self.form.__raw__ = {'resume': fs}
        self.assertFalse(self.form.__valid__)

    def test_no_filenames(self):
        """Test a field that only accepts upload."""
        class TestForm(Form):
            __frontend__ = dummy_frontend
            resume = FileField(
                max_len=256,
                accept_mime=('text/*',),
                # directory=HERE,
            )
        form = TestForm()
        form.__raw__ = {'resume': 'lorem.txt'}
        self.assertFalse(form.__valid__)
        self.assertEqual(
            form.__errors__['resume'].message,
            "This field doesn't support filenames"
        )

    def test_to_python(self):
        """You can't use to_python to get any meaningful data."""
        with open(os.path.join(HERE, 'lorem.txt')) as f:
            f.mimetype = 'text/plain'
            self.form['resume'] = f
            self.assertEqual(self.form.__raw__['resume'], None)
