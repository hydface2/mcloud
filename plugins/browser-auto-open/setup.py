from __future__ import print_function

import os
import sys
import imp

metadata = imp.load_source(
    'metadata', os.path.join('../../mcloud', 'metadata.py'))

from setuptools import setup, find_packages

# See here for more options:
# <http://pythonhosted.org/setuptools/setuptools.html>

mcloud_version = '0.10.14'

setup(
    name='mcloud-plugin-browser-auto-open',
    version=mcloud_version,
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    maintainer='Alex Rudakov',
    maintainer_email='ribozz@gmail.com',
    url='mcloud.io',
    description='browser-auto-open mcloud plugin',
    long_description=open('README.rst').read(),

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Software Distribution',
    ],
    py_modules=['mcloud_browser_auto_open'],
    install_requires=[
        'mcloud==%s' % mcloud_version,
        'PyYAML'
    ],

    entry_points={
        'mcloud_plugins': [
            'browser-auto-open = mcloud_browser_auto_open:BrowserAutoOpenPlugin'
        ]
    }
)
