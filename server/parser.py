import os
#import re
#import string

#from bs4 import BeautifulSoup
import lxml.etree as etree
#import lxml.html as lhtml

import models


class Catalog(object):
    def __init__(self):
        self._data = {}

    @staticmethod
    def get_model(entry_type):
        return models.entry_types[entry_type]

    @staticmethod
    def has_model(entry_type):
        return entry_type in models.entry_types

    def parse(self):
        raise NotImplementedError("Method 'parse' is not implemented here")

    def get_entry_data(self, entry_id):
        return self._data.get(entry_id, {})

    def get_entry_model(self, entry_id):
        entry_data = self.get_entry_data(entry_id)
        return self.get_model(entry_data["entry_type"])\
                .from_parsed_data(entry_data)

    def get_entry_ids(self):
        return self._data.keys()


class BlockFileCatalog(Catalog):
    def __init__(self, filenames, block_parser):
        super(BlockFileCatalog, self).__init__()
        self._filenames = filenames
        self._block_parser = block_parser

    @staticmethod
    def extract_id(filename):
        return int(os.path.splitext(os.path.basename(filename))[0])

    def parse(self):
        for filename in self._filenames:
            entry_id = self.extract_id(filename)
            with open(filename, "r") as fp:
                entry_data = self._block_parser.parse(entry_id,\
                        fp.read().decode("utf-8"))
                self._data[entry_id] = entry_data


class XmlFileCatalog(Catalog):
    def __init__(self, filename):
        super(XmlFileCatalog, self).__init__()
        self._filename = filename

    def parse(self):
        parser = etree.XMLParser(remove_blank_text=True)
        document = etree.parse(self._filename, parser=parser)
        for entry in document.xpath("/Data/Results")[0]:
            entry_type = unicode(entry.tag.lower())
            entry_data = {str(x.tag.lower()): unicode(x.text.strip())\
                    for x in entry}
            entry_data["entry_type"] = entry_type
            self._data[int(entry_data["id"])] = entry_data


class MergedCatalog(Catalog):
    def __init__(self, catalogs):
        super(MergedCatalog, self).__init__()
        self._catalogs = catalogs

    def parse(self):
        for catalog in self._catalogs:
            catalog.parse()

    def get_entry_data(self, entry_id):
        entry_data = {}
        for catalog in self._catalogs:
            entry_data.update(catalog.get_entry_data(entry_id))
        return entry_data

    def get_entry_ids(self):
        entry_ids = set()
        for catalog in self._catalogs:
            entry_ids |= set(catalog.get_entry_ids())
        return list(entry_ids)


class BlockParser(object):
    block_type = None

    xpath_container = etree.XPath("/div[@id='detail']")
    xpath_name = etree.XPath("/div/h1[@class='player']")
    xpath_kv = etree.XPath("/div/p[@class='flavor']/b")
    xpath_after_kv = etree.XPath("/div/p[@class='flavor']")

    def __init__(self, block_type=None):
        self._patterns = []
        self.create_patterns()
        if block_type is not None:
            self.block_type = block_type

    def create_patterns(self):
        pass

    def add_pattern(self, xpath, action, aggregate_action=None):
        if aggregate_action is None:
            aggregate_action = lambda x: x
        self._patterns.append((xpath, action, aggregate_action))

    @staticmethod
    def aggregate_groups(group_name):
        def aggregate_groups_action(values):
            return [(group_name, values), ]
        return aggregate_groups_action

    @staticmethod
    def join(group_name):
        def join_action(values):
            return [(group_name, u"".join(v for k, v in values)), ]
        return join_action

    @staticmethod
    def label_content(name):
        def label_content_action(element, tree):
            return (name, (u"".join(element.itertext())).strip())
        return label_content_action

    @staticmethod
    def label_kv():
        def label_kv_action(element, tree):
            key = element.text.strip(": ").lower()
            if element.tail:
                value = unicode(element.tail.strip(":").strip())
            else:
                value = element.tail
            return (key, value)
        return label_kv_action

    def parse_raw(self, id, html):
        parser = etree.XMLParser(remove_blank_text=True)
        clean_text = html.replace("images/bullet.gif", "static/images/bullet.gif")
        clean_text = clean_text.replace("http://www.wizards.com/dnd/images/symbol/", "static/images/")
        result = [("id", id), ("entry_type", unicode(self.block_type)), ("text", clean_text)]

        # work around "D&D;" in the html
        html = html.replace("D&D;", "D&amp;D;")
        tree = etree.fromstring(html, parser=parser)

        for xpath, action, aggregate_action in self._patterns:
            pattern_result = []
            for element in xpath(tree):
                pattern_result.append(action(element, tree))
            result += aggregate_action(pattern_result)
        return result

    def parse(self, id, html):
        return dict(self.parse_raw(id, html))

    #def parse_to_model(self, id, html):
        #data = self.parse(id, html)
        #return self.model.from_parsed_data(data, text=html)


class GenericParser(BlockParser):
    model = models.Deity

    def create_patterns(self):
        self.add_pattern(self.xpath_name, self.label_content("name"))
        self.add_pattern(self.xpath_kv, self.label_kv())


class DeityParser(BlockParser):
    block_type = "deity"

    def create_patterns(self):
        self.add_pattern(self.xpath_name, self.label_content("name"))
        self.add_pattern(self.xpath_kv, self.label_kv())


class FeatParser(BlockParser):
    block_type = "feat"

    def create_patterns(self):
        self.add_pattern(self.xpath_name, self.label_content("name"))
        self.add_pattern(self.xpath_kv, self.label_kv())


class ClassParser(BlockParser):
    block_type = "class"


class PowerParser(BlockParser):
    block_type = "power"

    xpath_usagetype = etree.XPath("/div/p[@class='powerstat'][1]/b[1]")

    def create_patterns(self):
        self.add_pattern(self.xpath_usagetype, self.label_content("usagetype"))


class MonsterParser(BlockParser):
    block_type = "monster"

    def create_patterns(self):
        pass


class ItemParser(BlockParser):
    block_type = "item"

    def create_patterns(self):
        pass


class GlossaryParser(BlockParser):
    block_type = "glossary"

    def create_patterns(self):
        pass


class RaceParser(BlockParser):
    block_type = "race"

    def create_patterns(self):
        pass


class RitualParser(BlockParser):
    block_type = "ritual"

    def create_patterns(self):
        pass


def get_block_parser(entry_type):
    return ({
            u"deity": DeityParser,
            u"feat": FeatParser,
            u"class": ClassParser,
            u"power": PowerParser,
            u"monster": MonsterParser,
            u"item": ItemParser,
            u"glossary": GlossaryParser,
            u"race": RaceParser,
            u"ritual": RitualParser,
            }).get(entry_type)
