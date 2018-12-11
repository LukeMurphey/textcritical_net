from xml.dom.minidom import parseString
from reader.importer.Perseus import PerseusTextImporter

class LexiconImporter():
    @staticmethod
    def find_perseus_entries(verse):
        document = parseString(verse.original_content)
        orth_tags = document.getElementsByTagName("orth")

        entries = []

        for tag in orth_tags:
            entries.append(PerseusTextImporter.getText(tag.childNodes))

        return entries
