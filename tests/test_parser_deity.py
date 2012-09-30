import os
from unittest import TestCase

import server.parser as parser
reload(parser)


class DeityParserTest(TestCase):
    FIXTURES = {
            "deity_1.html": {
                "id": u"deity_1",
                "name": u"Avandra",
                "alignment": u"Good",
                "gender": u"Female",
                "domain": u"Change, Freedom, Luck",
                "type": u"God",
                },
            "deity_148.html": {
                "id": u"deity_148",
                "name": u"Sagawehn, The Winged Mistress, the Hive Mind",
                "alignment": u"Unaligned",
                "sphere": u"Vermin",
                "type": u"Dead God",
                },
            }

    def setUp(self):
        self.parser = parser.DeityParser()

    def xtest_basics(self):
        for fixture_filename, fixture_result in self.FIXTURES.iteritems():
            with open(os.path.join(os.path.dirname(__file__), "page_fixtures",\
                    fixture_filename), "r") as fp:
                id = os.path.splitext(fixture_filename)[0]
                result = self.parser.parse(id, fp.read().decode("utf-8"))
                self.assertEqual(result, fixture_result)
