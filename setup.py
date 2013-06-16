# vim: noai:ts=4:sw=4:expandtab:syntax=python

import pkg_resources
from setuptools import setup


setup(
    name='xbotpp',
    version=pkg_resources.get_distribution('xbotpp').version,
    description='A multi-protocol chat bot.',
    author='aki--aki',
    author_email='aki@aki.pw',
    url='https://github.com/aki--aki/xbotpp',
    packages=['xbotpp', 'xbotpp.config'],
    entry_points = {
        'console_scripts': [
            'xbotpp = xbotpp:main',
            'xbotpp-migrate = xbotpp.config.migrate:main',
            'xbotpp-config = xbotpp.config.interactive:main',
        ],
    },
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Topic :: Communications :: Chat",
        "Development Status :: 4 - Beta",
    ],
    keywords='irc bot',
    license='BSD Licence',
    install_requires=[
        'irc',
        'nose',
    ],
)
