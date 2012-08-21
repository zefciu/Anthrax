import unittest
import cgi

from anthrax.container import Form
from anthrax.field import FileField
from util import dummy_frontend

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
                accept_mime=('text/*')
            )
        self.form = TestForm()

    def test_ok(self):
        fs = _create_fs('text/plain', 'Lorem ipsum dolor sit amet')
        self.form.__raw__ = {'resume': fs}
        self.assertTrue(self.form.__valid__)
        self.assertEqual(
            self.form['resume'].file.read(), 'Lorem ipsum dolor sit amet'
        )

    def test_wrong_mime(self):
        fs = _create_fs('application/x-python', 'print("Lorem ipsum")')
        self.form.__raw__ = {'resume': fs}
        self.assertFalse(self.form.__valid__)
