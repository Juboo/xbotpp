import xbotpp
from setuptools import setup


setup(
    name='xbotpp',
    version=xbotpp.__version__,
    description='A multi-protocol chat bot.',
    author='aki--aki',
    author_email='aki@aki.pw',
    url='https://github.com/aki--aki/xbotpp',
    packages=['xbotpp', 'xbotpp.config', 'xbotpp.util'],
    entry_points = {
        'console_scripts': [
            'xbotpp = xbotpp:main',
            'xbotpp-migrate = xbotpp.config.migrate:main',
            'xbotpp-config = xbotpp.config.interactive:main',
            'xbotpp-socket-client = xbotpp.util.socket_client:main',
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
