import os
from unittest import TestCase

import server.parser as parser
reload(parser)
from common import exclude_keys


class PowerParserTest(TestCase):
    XML_FILE = "power.xml"
    FIXTURES = {
            "power/10000.html": {
                "actiontype": u"Minor",
                "classname": u"Fighter",
                "entry_type": "power",
                "id": 10000,
                "level": 10,
                "name": u"Mighty Surge",
                "usagetype": u"Daily",
                },
            "power/997.html": {
                "actiontype": u"Standard",
                "classname": u"Fighter",
                "entry_type": "power",
                "id": 997,
                "level": 1,
                "name": u"Reaping Strike",
                "usagetype": u"At-Will",
                },
            "power/27.html": {
                "actiontype": u"Minor",
                "classname": u"Duergar",
                "entry_type": "power",
                "id": 27,
                "level": None,
                "name": u"Infernal Quills",
                "usagetype": u"Encounter",
                },
            }

    def setUp(self):
        self.maxDiff = None

    def get_fixture_filename(self, filename):
        return os.path.join(os.path.dirname(__file__), "page_fixtures", filename)

    def test_basics(self):
        filenames = [self.get_fixture_filename(f) for f in self.FIXTURES]
        catalog = parser.MergedCatalog([
            parser.XmlFileCatalog(self.get_fixture_filename(self.XML_FILE)),
            parser.BlockFileCatalog(filenames, parser.get_block_parser("power")("power")),
            ])
        catalog.parse()
        for fixture_result in self.FIXTURES.itervalues():
            result = catalog.get_entry_model(fixture_result["id"])
            self.assertEqual(
                    exclude_keys(result.as_dict(), ["text", "sourcebook"]),
                    fixture_result,
                    )
