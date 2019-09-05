import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'pyramid >= 1.8.4',
    'Pillow >= 5.0.0',
    'eor-settings'
]

setup(
    name='eor-filestore',
    version='2.1.0',
    description='A file upload and storage backend for the Pyramid framework',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='p.thorn.ru@gmail.com',
    author_email='p.thorn.ru@gmail.com',
    url='',
    keywords='web wsgi bfg pylons pyramid',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='eor-filestore',
    install_requires=requires
)
