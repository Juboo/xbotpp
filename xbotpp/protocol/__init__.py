def setup():
	from ..exthook import ExtensionImporter
	importer = ExtensionImporter(['xbotpp_protocol_%s'], __name__)
	importer.install()

setup()
del setup
