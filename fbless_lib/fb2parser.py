#!/usr/bin/env python
# -*- mode: python; coding: koi8-r; -*-

import sys, string
from cStringIO import StringIO
import xml.sax
import xml.parsers.expat

from paragraph import Paragraph, attr


class StopParsing(Exception):
    pass


class ContentHandler:
    def __init__(self):
##         self.elem_stack = []
        self.is_desc = False
        self.cur_data = []
        self.is_title = False
        self.is_body = False
        self.is_epigraph = False
        self.is_cite = False
        self.cur_title = []
        self.attrs = []
        self.cur_attr = []
        self.lang = None
        self.content = []
        self.cur_id = None
        self.prev_paragraph_is_empty = True

    def add_empty_line(self):
        if not self.prev_paragraph_is_empty:
            self.content.append(Paragraph('empty-line', '',
                                          byte_index=_parser.CurrentByteIndex))
            self.prev_paragraph_is_empty = True

    def startElement(self, name, attrs):
        if name == 'description': self.is_desc = True
        elif name == 'body': self.is_body = True
        elif name == 'epigraph': self.is_epigraph = True
        elif name == 'cite': self.is_cite = True
        elif name == 'title':
            self.is_title = True
            self.cur_title = []
        elif name == 'stanza':
            self.add_empty_line()
        elif name == 'image':
            for atr in attrs.keys():
                if atr.endswith('href'):
                    self.add_empty_line()
                    self.cur_data = '['+attrs[atr][1:]+']'
                    break
        elif name == 'binary':
            raise StopParsing
        elif name in ('strong', 'emphasis', 'style'):
            self.cur_attr = [sum(map(len, self.cur_data)), attr[name]]
        elif name == 'a':
            href = None
            for atr in attrs.keys():
                if atr.endswith('href'):
                    href = attrs[atr]
                    break
            self.cur_attr = [sum(map(len, self.cur_data)), (attr.a, href)]
        elif name == 'subtitle':
            self.add_empty_line()
        if 'id' in attrs:
            self.cur_id = attrs['id']

    def endElement(self, name):
        if name == 'empty-line':
            self.add_empty_line()
        elif self.is_body and name != 'body':
            data = ''.join(self.cur_data)
            if name in ['strong', 'emphasis', 'a', 'style']:
                if not self.cur_attr:
                    ##print 'FB2 PARSER ERROR: nested styles?'
                    return
                self.cur_attr.insert(1, len(data))
                self.attrs.append(self.cur_attr)
                self.cur_attr = []
                return
            if data and data.strip():
                if self.is_title:
                    self.add_empty_line()
                    self.content.append(Paragraph('title', data,
                                                  attrs=self.attrs,
                                                  lang=self.lang,
                                                  id=self.cur_id,
                                                  byte_index=_parser.CurrentByteIndex))
                elif self.is_epigraph and name == 'p':
                    self.content.append(Paragraph('epigraph', data,
                                                  attrs=self.attrs,
                                                  lang=self.lang,
                                                  id=self.cur_id,
                                                  byte_index=_parser.CurrentByteIndex))
                elif self.is_cite and name == 'p':
                    self.content.append(Paragraph('cite', data,
                                                  attrs=self.attrs,
                                                  lang=self.lang,
                                                  id=self.cur_id,
                                                  byte_index=_parser.CurrentByteIndex))
                else:
                    self.content.append(Paragraph(name, data,
                                                  attrs=self.attrs,
                                                  lang=self.lang,
                                                  id=self.cur_id,
                                                  byte_index=_parser.CurrentByteIndex))
                self.prev_paragraph_is_empty = False
                self.attrs = []
                self.id = None

        if name == 'description':
            self.is_desc = False
        elif name == 'body':
            self.is_body = False
        elif name == 'epigraph':
            self.is_epigraph = False
            self.add_empty_line()
        elif name == 'cite':
            self.is_cite = False
        elif name == 'title':
            self.is_title = False
            self.add_empty_line()
        elif name in ('subtitle', 'image', 'poem'):
            self.add_empty_line()
        elif name == 'lang':
            self.lang = ''.join(self.cur_data).strip()

        #del self.elem_stack[-1]
        self.cur_data = []
        self.links = {}

    def characters(self, data):
        #data = data.strip()
        #data = data.replace('\n', ' ')
        self.cur_data.append(data)


##----------------------------------------------------------------------

def fb2parse(data):

    if not data.startswith('<?xml'):
        print 'Warning: file is not an XML file. Skipped.'
        return None

    global _parser

    # remove invalid chars
    tab = string.maketrans('', '')
    data = data.translate(tab, '\07\032') # XXX: add other invalid chars here

    content_handler = ContentHandler()

    _parser = xml.parsers.expat.ParserCreate()

    _parser.StartElementHandler = content_handler.startElement
    _parser.EndElementHandler = content_handler.endElement
    _parser.CharacterDataHandler = content_handler.characters

    try:
        _parser.Parse(data)
    except StopParsing:
        pass

    return content_handler.content

##----------------------------------------------------------------------

if __name__ == '__main__':
    fn = sys.argv[1]
    #from main import create_content
    #c = create_content(fn, 80)
    c = fb2parse(file(fn).read())
    #for s, t in c:
    #    print t, s

