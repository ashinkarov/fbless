#!/usr/bin/env python
# -*- mode: python; coding: koi8-r; -*-

import sys
import locale

from hyphenation import Hyphenation
from options import options, replace_chars


#screen_cols = 80

default_charset = locale.getdefaultlocale()[1]

hyph = Hyphenation()

# u'\u2013' -> '--'
# u'\u2014' -> '---'
# u'\xa0'   -> неразрывный пробел
# u'\u2026' -> dots...
# u'\xab'   -> '<<'
# u'\xbb'   -> '>>'
# u'\u201c' -> ``
# u'\u201d' -> ''
# u'\u201e' -> ,,
# u'\xad'   -> мягкий перенос
def replace(s):
    return (s
            .replace(u'\u2013', u'-')
            .replace(u'\u2014', u'-')
            .replace(u'\xa0'  , u' ')
            .replace(u'\u2026', u'...')
            #.replace(u'\xab'  , u'<<')
            #.replace(u'\xbb'  , u'>>')
            .replace(u'\xab'  , u'"')
            .replace(u'\xbb'  , u'"')
            .replace(u'\u201c', u'"')
            .replace(u'\u201d', u'"')
            .replace(u'\u201e', u'"')
            .replace(u'\u2116', u'No')
            .replace(u'\xad', '')
            .replace(u'\u2019', '\'')
            )


class Attr:
    keys = {'newline' : -1,
            'normal'  : 0,
            'strong'  : 1,
            'emphasis': 2,
            'a'       : 3,
            'style'   : 4,
            #
            'left_spaces' : 10,
            #
            'search'       : 20,
            'cancel_search': 21,
            }

    def __init__(self):
        self.__dict__.update(self.keys)

    def __getitem__(self, name):
        return self.keys[name]

attr = Attr()


class Paragraph:
    def __init__(self, type='p', data='', attrs=[], lang=None,
                 id=None, byte_index=0):
        #print 'attrs:', attrs
        self.type = type
        self.data = data
        self.attrs = attrs
        self.search_offsets = []
        self.id = id
        self.lines = []
        self.lang = lang
        self.byte_index = byte_index
        if lang is None:
            self.lang = 'ru'
        try:
            self.__dict__.update(options[type])
        except KeyError:
            self.__dict__.update(options['default'])
        if self.justify == 'fill':
            self.stretch = True
        else:
            self.stretch = False

        self._first_indent = 0

        #self.maxlen = self.scr_cols-self.left_indent-self.right_indent

    def stretch_string(self, words, max_len):
        if len(words) < 2:
            return words
        len_words = len([i for i in words if i == ' ']) + 1
        sum_words = sum(len(i) for i in words
                        if not isinstance(i, (int, tuple)))
        min_space, long_space_num = divmod(max_len-sum_words, len_words-1)
        short_space_num = len_words - long_space_num - 1
        bres = short_space_num / 2
        s = []
        for w in words:
            if w == ' ':
                if bres > 0:
                    bres -= long_space_num
                    s.append(' '*(min_space+1))
                else:
                    bres += short_space_num
                    s.append(' '*(min_space+2))
            else:
                s.append(w)
        return s

    def strip_line(self, line):
        # remove trailing whitespaces
        while line:
            if line[-1] == ' ' or isinstance(line[-1], (int, tuple)):
                line.pop()
            else:
                break

    def split_string(self):
        if self.lines: return # already splitted
        if self.data == '\n':
            self.lines = ['']
            return

        max_len = self.scr_cols - self.left_indent - self.right_indent

        offsets = []
        prev_offset = 0
        for attr_begin, attr_end, attr_type in self.attrs:
            offsets.append((prev_offset, attr.normal))
            offsets.append((attr_begin, attr_type))
            prev_offset = attr_end
        offsets.append((prev_offset, attr.normal))
        offsets.append((len(self.data), attr.normal))
        for begin, end in self.search_offsets:
            offsets.append((begin, attr.search))
            offsets.append((end, attr.cancel_search))
        offsets.sort()                  # sort by offsets

        #print offsets

        first_line_offset = self.first_line_indent
        words = [' '*(self.first_line_indent-1)]
        last_line = []

        line = []
        line.append(' '*self.first_line_indent)
        line_len = self.first_line_indent
        attr_begin, cur_attr_type = offsets[0]
        line.append(cur_attr_type)
        in_search = False
        for attr_end, next_attr_type in offsets[1:]:
            data = self.data[attr_begin:attr_end]

            if data:
                if replace_chars:
                    data = replace(data)

                if data.startswith(' '):
                    line.append(' ')
                    line_len += 1

                words = data.split()
                for word in words:
                    if line_len + len(word) + 1 > max_len:
                        if self.hyphenate:
                            # hyphenation
                            wl = hyph.hyphenate(word, self.lang)
                            for ww in wl:
                                if line_len + len(ww) + 1 <= max_len:
                                    line.append(ww+'-')
                                    word = word[len(ww):]
                                    if word.startswith('-'):
                                        word = word[1:]
                                    break
                        # remove trailing whitespaces
                        while line:
                            if line[-1] == ' ' or \
                                   isinstance(line[-1], (int, tuple)):
                                line.pop()
                            else:
                                break
                        line.append(attr.newline)
                        line.append(cur_attr_type)
                        if in_search:
                            line.append(attr.search)
                        line_len = 0

                    line.append(word)
                    line.append(' ')
                    line_len += len(word)+1

                if not data.endswith(' ') and line:
                    line.pop()
                    line_len -= 1

            attr_begin = attr_end
            if next_attr_type  == attr.search:
                in_search = True
            elif next_attr_type == attr.cancel_search:
                in_search = False
            else:
                cur_attr_type = next_attr_type
            line.append(next_attr_type)


        lines = []
        ln = []
        for w in line:
            if w == attr.newline:
                if self.stretch:
                    ln = self.stretch_string(ln, max_len)
                lines.append(ln)
                ln = []
            else:
                ln.append(w)
        if ln:
            lines.append(ln)

        for ln in lines:
            # add leading spaces
            if self.justify == 'center':
                len_line = sum(len(s) for s in ln
                               if not isinstance(s, (int, tuple)))
                d = (max_len - len_line) / 2
                spaces = ' ' * (self.left_indent + d)
            elif self.justify == 'right':
                len_line = sum(len(s) for s in ln
                               if not isinstance(s, (int, tuple)))
                d = max_len - len_line
                spaces = ' ' * (self.left_indent + d)
            else: # left or fill
                spaces = ' ' * self.left_indent
            if spaces:
                ln.insert(0, attr.left_spaces)
                ln.insert(1, spaces)

        self.lines = lines




if __name__ == '__main__':
    s=unicode('Давно было готово заглавие, использующее титул замечательной монографии :вана Аксенова "Пикассо и окрестности". Предрешен был и тот свободный жанр "филологического романа", в котором написана моя любимая русская проза - от мандельштамовского "Разговора о Данте" до "Прогулок с Пушкиным" Синявского. Но что особенно важно, сама собой сформулировалась центральная тема - исповедь последнего советского поколения, голосом которого стал Сергей Довлатов.', 'koi8-r')
    par=Paragraph(data=s, attrs=[(6, 10, attr.strong),
                                 (100, 240, attr.strong)])
    par.scr_cols = 48
    par.search_offsets = [(0, 50), (78, 120)]
    par.split_string()
    for l in par.lines:
        if 0:
            print l
        elif 0:
            for w in l:
                if w == ' ':
                    print '<sp>'
                else:
                    print w
        else:
            for w in l:
                if isinstance(w, int):
                    sys.stdout.write('<%d>' % w)
                    pass
                elif isinstance(w, tuple):
                    sys.stdout.write('<|>')
                else:
                    #print w,
                    #sys.stdout.write('|')
                    sys.stdout.write(w.encode('koi8-r', 'replace'))
            print
    print '~'*(par.scr_cols-par.right_indent)

    #par.print_str()
##     for s in par.lines:
##         if isinstance(s, int):
##             print '>', s, '<'
##         else:
##             for w in s:
##                 print w,
##             print

