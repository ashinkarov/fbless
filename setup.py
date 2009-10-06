#!/usr/bin/env python
# -*- mode: python; coding: koi8-r -*-

import sys
import os
from distutils.core import setup
from distutils.command.install_data import install_data

program_version = '0.2.1'

class my_install_data(install_data):
    # for install data files to library dir
    def run(self):
        #need to change self.install_dir to the actual library dir
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return install_data.run(self)

setup(
    name = 'fbless',
    version = program_version,
    url = 'http://pybookreader.narod.ru/',
    author = 'Con Radchenko',
    author_email = 'pybookreader@narod.ru',
    description = 'Curses based FictionBook2 viewer.',
    license = 'GPL',
    scripts = ['fbless'],
    packages = ['fbless_lib'],
    cmdclass = {'install_data': my_install_data},
    data_files = [ ('fbless_lib/hyph_dicts',
                    ['fbless_lib/hyph_dicts/hyph_de.dic',
                     'fbless_lib/hyph_dicts/hyph_en.dic',
                     'fbless_lib/hyph_dicts/hyph_es.dic',
                     'fbless_lib/hyph_dicts/hyph_fr.dic',
                     'fbless_lib/hyph_dicts/hyph_it.dic',
                     'fbless_lib/hyph_dicts/hyph_ru.dic',
                     'fbless_lib/hyph_dicts/hyph_uk.dic',
                     'fbless_lib/hyph_dicts/langs.txt',
                     'fbless_lib/hyph_dicts/README.ru']),
                   ],
    )

