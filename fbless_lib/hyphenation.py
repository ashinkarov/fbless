#!/usr/bin/env python
# -*- mode: python; coding: koi8-r; -*-
#
# $Id: hyphenation.py,v 1.2 2005/07/12 21:14:18 conr Exp $
#

import os, sys
from glob import glob

if __name__ == '__main__':
    dict_files_dir = 'hyph_dicts'
else:
    dict_files_dir = os.path.join('fbless_lib', 'hyph_dicts')
ru_dict_file = os.path.join(dict_files_dir, 'hyph_ru.dic')

vowels = unicode('аеёиоуыэюяАЕЁИОУЫЭЮЯ', 'koi8-r')
consonants = unicode('бвгджзйклмнпрстфхцчшщБВГДЖЗЙКЛМНПРСТФХЦЧШЩ', 'koi8-r')
hardsoftsigns = unicode('ъьЪЬ', 'koi8-r')

class Hyphenation:

    def __init__(self):
        self.hyph_pats = {}

        # ф-ция переносов для русского языка
        self.ru_hyphenate_func = self.ru_hyphenate
        #self.ru_hyphenate_func = self.tex_hyphenate

        dfd = '' #None
        for f in sys.path:
            if os.path.exists(os.path.join(f, ru_dict_file)):
                dfd = os.path.join(f, dict_files_dir)
                break

        self.dict_files_dir = dfd

        if not dfd:
            print 'ERROR: can\'t read hyphenation files'
            return

        self.langs = []
        #self.hyph_pats['ru'] = self.read_patterns('ru')


    def get_langs(self):

        if self.langs:
            return self.langs

        langs = map(lambda x: x[len(self.dict_files_dir)+6:-4],
                    glob(os.path.join(self.dict_files_dir, 'hyph_*.dic')))
        if os.path.exists(os.path.join(self.dict_files_dir, 'langs.txt')):
            for s in open(os.path.join(self.dict_files_dir, 'langs.txt')).readlines():
                s1, s2 = s.split(' ', 1)
                if s1 in langs:
                    self.langs.append((s1, s2[:-1]))
        else:
            for s in langs:
                self.langs.append((s, s))
        self.langs.append(('ru-tex', 'Russian with TeX algorithm'))
        self.langs.sort()
        self.langs.append(('no-hyphenate', 'Don\'t hyphenate'))

        return self.langs


    def read_patterns(self, lang):

        dict_file = os.path.join(self.dict_files_dir, 'hyph_%s.dic' % lang)
        if not os.path.exists(dict_file):
            return None

        hyph_pats = {}

        fd = open(dict_file)
        encoding = fd.readline().strip()

        for l in fd.readlines():
            l = unicode(l, encoding).strip()

            ii = []
            i = 0
            s = ''
            for c in l:
                if c.isdigit():
                    ii.append((i, int(c)))
                else:
                    s += c
                    i += 1

            if ii:
                hyph_pats[s] = ii

        return hyph_pats


    def hyphenate(self, word, lang='ru'):

        if len(word) < 4:
            return []
        if lang == 'no-hyphenate':
            return []

        if lang == 'ru':
            hyphenate_func = self.ru_hyphenate_func
        elif lang == 'ru-tex':
            hyphenate_func = self.tex_hyphenate
            lang = 'ru'
        else:
            hyphenate_func = self.tex_hyphenate

        words_list = []
        w = u''
        ww = u''

        # split words
        for i in word:
            if i.isalpha():
                ww += i
            else:
                if ww:
                    for j in hyphenate_func(ww, lang):
                        words_list.append(w+j)
                if i == '-':
                    words_list.append(w+ww)
                w += ww+i
                ww = u''

        if ww:
            for j in hyphenate_func(ww, lang):
                words_list.append(w+j)

        words_list.reverse()
        return words_list


    def ru_hyphenate(self, word, lang='ru'):
        # based on code by Mike Matsnev
        # ("Haali Reader" http://haali.cs.msu.ru/pocketpc/)

        length = len(word)

        i = 0
        wl = []
        w = ''
        while i < length:
            if word[i] in vowels:
                for j in range(i+1, length):
                    if word [j] in vowels:
                        if word[i+1] in consonants \
                               and word[i+2] in consonants:
                            w += word[i]
                            i += 1
                        elif word[i+1] in consonants \
                                 and word[i+2] in hardsoftsigns:
                            w += word[i:i+2]
                            i += 2
                        if 1 <= i < length-2:
                            wl.append(w+word[i])
                        break

            w += word[i]
            i += 1

        return wl


    def tex_hyphenate(self, word, lang='ru'):

        if not self.hyph_pats.has_key(lang):
            self.hyph_pats[lang] = self.read_patterns(lang)
        if not self.hyph_pats[lang]:
            return []

        hyph_pats = self.hyph_pats[lang]

        w = u'.'+word.lower()+u'.'
        h_list = [0]*len(w)

        for a in range(len(w)+1):
            for b in range(a):
                if hyph_pats.has_key(w[b:a]):
                    h = hyph_pats[w[b:a]]
                    #print '>>', w[b:a].encode('koi8-r'), h
                    for i, j in h:
                        if h_list[b+i] < j:
                            h_list[b+i] = j

        #ret = ''
        ret_list = []
        i = 1
        for j in range(3, len(w)-2):
            if h_list[j]%2:
                #ret += '-'+w[i:j]
                ret_list.append(word[:j-1])
                i = j
        #ret += '-'+w[i:]

        #print ret[1:-1]
        return ret_list


if __name__ == '__main__':

    h=Hyphenation()

##     for i in range(10000):
##         h.hyphenate(unicode('специалист', 'koi8-r'))


    ## Russian
    for w in ('стэнфорд',):
        i = 0
        hl = h.hyphenate(unicode(w, 'koi8-r'), 'ru-tex')
        hl.reverse()
        for l in hl:
            print l[i:].encode('koi8-r'),
            i = len(l)
        print w[i:]
##     for w in ('пере-Стройка','безусловный','полу-остров','автоматизация',
##               'спецотдел','специалист'):
##         i = 0
##         hl = h.hyphenate(unicode(w, 'koi8-r'), 'ru-tex')
##         hl.reverse()
##         for l in hl:
##             print l[i:].encode('koi8-r'),
##             i = len(l)
##         print w[i:]

    ## English
##     for w in ('power', 'gratuiTously', 'hyphenate', 'whole', 'paragraphs'):
##         for l in h.hyphenate(unicode(w, 'iso8859-1'), 'en'):
##             print l.encode('iso8859-1')
##         print '-'*20

    ## German
##     for w in ('berichtet', 'Theodor', 'Holzkopf', 'erfunden',
##               'promovierte', 'Doktor', 'Rechte', 'Эber', 'Thema',
##               'BЖllerschЭsse', 'VЖlkerrecht'):
##         for l in h.hyphenate(unicode(w, 'iso8859-1'), 'de'):
##             print l.encode('iso8859-1')
##         print '-'*20


