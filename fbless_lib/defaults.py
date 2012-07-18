# -*- mode: python; coding: utf-8; -*-
""" Default options """

import os

try:
    from xdg.BaseDirectory import xdg_cache_home
except ImportError:
    xdg_cache_home = os.path.expanduser('~/.cache')

paths = {
    'save_file': os.path.join(xdg_cache_home, 'fbless', 'fbless_save'),
}

general = {
    'context_lines': 0,
    'status': True,
    # screen width. 0 means autodetect
    'columns': 0,
    # if True and 'columns' is set, the text would be centered
    'center_text': False,
    # use default terminal colors
    'use_default_colors': True,
    'replace_chars': False,
    'editor': 'vim -c go{byte_offset} "{filename}"',
    # interval for autoscroll in sec
    'auto_scroll_interval': 3,
}

styles = {
    'default': {
        'justify': 'fill',
        'hyphenate': True,
        'left_indent': 2,
        'right_indent': 2,
        'first_line_indent': 4,
        'bold': False,
        'foreground': 'white',
        'background': 'black',
    },
    'p': {
        'justify': 'fill',
        'hyphenate': True,
        'left_indent': 2,
        'right_indent': 2,
        'first_line_indent': 4,
        'bold': False,
        'foreground': 'none',
        'background': 'none',
    },
    'v': {
        'justify': 'fill',
        'hyphenate': True,
        'left_indent': 10,
        'right_indent': 4,
        'first_line_indent': 0,
        'foreground': 'none',
        'background': 'none',
    },
    'text-author': {
        'justify': 'right',
        'hyphenate': True,
        'left_indent': 20,
        'right_indent': 2,
        'first_line_indent': 0,
        'foreground': 'yellow',
        'background': 'none',
    },
    'epigraph': {
        'justify': 'fill',
        'hyphenate': True,
        'left_indent': 20,
        'right_indent': 2,
        'first_line_indent': 4,
        'foreground': 'none',
        'background': 'none',
    },
    'cite': {
        'justify': 'fill',
        'hyphenate': True,
        'left_indent': 8,
        'right_indent': 8,
        'first_line_indent': 8,
        'foreground': 'none',
        'background': 'none',
    },
    'title': {
        'justify': 'center',
        'hyphenate': False,
        'left_indent': 8,
        'right_indent': 8,
        'first_line_indent': 0,
        'bold': True,
        'foreground': 'magenta',
        'background': 'none',
    },
    'subtitle': {
        'justify': 'center',
        'hyphenate': False,
        'left_indent': 8,
        'right_indent': 8,
        'first_line_indent': 0,
        'foreground': 'cyan',
        'background': 'none',
    },
    'image': {
        'justify': 'center',
        'hyphenate': False,
        'left_indent': 0,
        'right_indent': 0,
        'first_line_indent': 0,
        'foreground': 'none',
        'background': 'none',
    },
    'strong': {
        'foreground': 'magenta',
        'background': 'none',
    },
    'emphasis': {
        'foreground': 'cyan',
        'background': 'none',
    },
    'style': {
        'foreground': 'green',
        'background': 'none',
    },
    'a': {
        'foreground': 'red',
        'background': 'none',
    },
}

keys = {
    'quit': ('q', 'Q',),
    'toggle-status': ('s',),
    'search': ('/',),
    'scroll-fifo': ('f',),
    'auto-scroll': ('a',),
    'search-next': ('n',),
    'timer-inc': ('+',),
    'timer-dec': ('-',),
    'goto-percent': ('5', 'G',),
    'jump-link': ('\t',),
    'goto-link': ('return', '\n', 'right',),
    'backward': ('left', 'h',),
    'forward': ('backspace', 'l',),
    'scroll-up': ('up', 'k',),
    'scroll-down': ('down', 'j',),
    'next-page': (' ', 'pgdn',),
    'prev-page': ('pgup',),
    'goto-home': ('g', 'home',),
    'goto-end': ('end',),
    'edit-xml': ('o',),
}

