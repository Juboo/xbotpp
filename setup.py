import xbotpp
from setuptools import setup

setup(
	name='xbotpp',
	version=xbotpp.__version__,
	description='A multi-protocol chat bot.',
	author='Aki Jenkinson and contributors',
	author_email='aki@aki.pw',
	url='https://github.com/aki--aki/xbotpp',
	packages=['xbotpp'],
	entry_points = {
		'console_scripts': [
			'xbotpp = xbotpp:init',
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
		'nose',
		'PyYAML',
		'plyvel',
	],
)
