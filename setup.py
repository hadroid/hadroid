"""Hadroid setup."""

from codecs import open
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'hadroid', '__init__.py'), encoding='utf-8') as f:
    for line in f.readlines():
        if line.startswith('__version__'):
            version = line.split('=')[1].strip()[1:-1]

setup(
    name='hadroid',
    version=version,
    description='A simple Python chatbot',
    long_description=long_description,
    url='https://github.com/krzysztof/hadroid',
    author='Krzysztof Nowak',
    author_email='kn@linux.com',
    license='GPLv3',
    entry_points={
        'console_scripts': [
            'hadroid = hadroid.botctl:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='bot gitter chat',
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'crontab==0.21.3',
        'docopt==0.6.2',
        'pytz==2016.10',
        'requests==2.11.1',
        'scikit-learn==0.18.1',
        'numpy==1.13.0',
        'scipy==0.19.0',
        'python-dateutil==2.6.0',
    ],
    extras_require={
        'dev': [
            'check-manifest'
        ],
        'test': [
            'pytest==3.1.0'
        ],
    },
)
