#!/usr/bin/env python
# -*- mode: python; coding: koi8-r; -*-

import sys
from cStringIO import StringIO
import xml.sax

from paragraph import Paragraph, attr


class StopParsing(Exception):
    pass


class ContentHandler(xml.sax.handler.ContentHandler):
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
            self.content.append(Paragraph('empty-line', ''))
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
            for atr in attrs.getNames():
                if atr.endswith('href'):
                    self.add_empty_line()
                    self.cur_data = '['+attrs.getValue(atr)[1:]+']'
                    break
        elif name == 'binary':
            raise StopParsing
        elif name in ('strong', 'emphasis', 'style'):
            self.cur_attr = [sum(map(len, self.cur_data)), attr[name]]
        elif name == 'a':
            href = None
            for atr in attrs.getNames():
                if atr.endswith('href'):
                    href = attrs.getValue(atr)
                    break
            self.cur_attr = [sum(map(len, self.cur_data)), (attr.a, href)]
        elif name == 'subtitle':
            self.add_empty_line()
        attrs_names = attrs.getNames()
        if attrs_names:
            if 'id' in attrs_names:
                self.cur_id = attrs.getValue('id')


    def endElement(self, name):
        if name == 'empty-line':
            self.add_empty_line()
        elif self.is_body and name != 'body':
            data = ''.join(self.cur_data)
            if name in ['strong', 'emphasis', 'a', 'style']:
                if not self.cur_attr:
                    print 'FB2 PARSER ERROR: nested styles?'
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
                                                  id=self.cur_id))
                elif self.is_epigraph and name == 'p':
                    self.content.append(Paragraph('epigraph', data,
                                                  attrs=self.attrs,
                                                  lang=self.lang,
                                                  id=self.cur_id))
                elif self.is_cite and name == 'p':
                    self.content.append(Paragraph('cite', data,
                                                  attrs=self.attrs,
                                                  lang=self.lang,
                                                  id=self.cur_id))
                else:
                    self.content.append(Paragraph(name, data,
                                                  attrs=self.attrs,
                                                  lang=self.lang,
                                                  id=self.cur_id))
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
        elif name in ('subtitle', 'image'):
            self.add_empty_line()
##         elif name == 'poem':
##             self.content.append(Paragraph('p', ''))
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
        return

    chandler = ContentHandler()
    input_source = xml.sax.InputSource()
    input_source.setByteStream(StringIO(data))
    xml_reader = xml.sax.make_parser()
    xml_reader.setContentHandler(chandler)

    try:
        xml_reader.parse(input_source)
    except StopParsing:
        # skip <binary>
        pass

    return chandler.content

##----------------------------------------------------------------------

if __name__ == '__main__':
    fn = sys.argv[1]
    #from main import create_content
    #c = create_content(fn, 80)
    c = fb2parse(file(fn).read())
    #for s, t in c:
    #    print t, s

