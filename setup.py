# vim set fileencoding=utf-8
from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

with open('entry_points.ini') as f:
    entry_points = f.read()

setup(
    name = 'Anthrax',
    version = '0.0.1',
    author = 'Szymon Pyżalski',
    author_email = 'zefciu <szymon@pythonista.net>',
    description = 'Form geneation lib to end all form generation lib',
    url = 'http://github.com/zefciu/Anthrax',
    keywords = 'form web ',
    long_description = long_description,

    install_requires = [],
    tests_require = ['nose>=1.0', 'nose-cov>=1.0'],
    test_suite = 'nose.collector',
    package_dir = {'': 'src'},
    packages = [
        'anthrax', 'anthrax.field', 'anthrax.widget',
    ],
    use_2to3 = True,
    classifiers = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points = entry_points,

)

