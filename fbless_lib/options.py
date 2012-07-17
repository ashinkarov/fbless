# -*- mode: python; coding: utf-8; -*-
#

import curses
import ConfigParser
import os

try:
    from xdg.BaseDirectory import xdg_cache_home, xdg_config_home
except ImportError:
    xdg_cache_home = os.path.expanduser('~/.cache')
    xdg_config_home = os.path.expanduser('~/.config')

CONFIG_FILES = [
        os.path.join(xdg_config_home, "fbless", "fblessrc"),
        os.path.expanduser("~/.fblessrc"),
    ]

SPECIAL_KEYS = {
    'left': curses.KEY_LEFT,
    'right': curses.KEY_RIGHT,
    'up': curses.KEY_UP,
    'down': curses.KEY_DOWN,
    'enter': curses.KEY_ENTER,
    'backspace': curses.KEY_BACKSPACE,
    'home': curses.KEY_HOME,
    'end': curses.KEY_END,
    'pgup': curses.KEY_PPAGE,
    'pgdn': curses.KEY_NPAGE,
    'tab': ord('\t'),
    # we use comma as a delimiter between bindings in config, so we had
    # to create alias for cases when user wants it to be hotkey, too
    'comma': ord(','),
}

COLORS = {
    'black': curses.COLOR_BLACK,
    'blue': curses.COLOR_BLUE,
    'cyan': curses.COLOR_CYAN,
    'green': curses.COLOR_GREEN,
    'magenta': curses.COLOR_MAGENTA,
    'red': curses.COLOR_RED,
    'white': curses.COLOR_WHITE,
    'yellow': curses.COLOR_YELLOW,
    'none': None,
}

### Defaults

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
        'foreground': curses.COLOR_WHITE,
        'background': curses.COLOR_BLACK,
    },
    'p': {
        'justify': 'fill',
        'hyphenate': True,
        'left_indent': 2,
        'right_indent': 2,
        'first_line_indent': 4,
        'bold': False,
        'foreground': None,
        'background': None,
    },
    'v': {
        'justify': 'fill',
        'hyphenate': True,
        'left_indent': 10,
        'right_indent': 4,
        'first_line_indent': 0,
        'foreground': None,
        'background': None,
    },
    'text-author': {
        'justify': 'right',
        'hyphenate': True,
        'left_indent': 20,
        'right_indent': 2,
        'first_line_indent': 0,
        'foreground': curses.COLOR_YELLOW,
        'background': None,
    },
    'epigraph': {
        'justify': 'fill',
        'hyphenate': True,
        'left_indent': 20,
        'right_indent': 2,
        'first_line_indent': 4,
        'foreground': None,
        'background': None,
    },
    'cite': {
        'justify': 'fill',
        'hyphenate': True,
        'left_indent': 8,
        'right_indent': 8,
        'first_line_indent': 8,
        'foreground': None,
        'background': None,
    },
    'title': {
        'justify': 'center',
        'hyphenate': False,
        'left_indent': 8,
        'right_indent': 8,
        'first_line_indent': 0,
        'bold': True,
        'foreground': curses.COLOR_MAGENTA,
        'background': None,
    },
    'subtitle': {
        'justify': 'center',
        'hyphenate': False,
        'left_indent': 8,
        'right_indent': 8,
        'first_line_indent': 0,
        'foreground': curses.COLOR_CYAN,
        'background': None,
    },
    'image': {
        'justify': 'center',
        'hyphenate': False,
        'left_indent': 0,
        'right_indent': 0,
        'first_line_indent': 0,
        'foreground': None,
        'background': None,
    },
    'strong': {
        'foreground': curses.COLOR_MAGENTA,
        'background': None,
    },
    'emphasis': {
        'foreground': curses.COLOR_CYAN,
        'background': None,
    },
    'style': {
        'foreground': curses.COLOR_GREEN,
        'background': None,
    },
    'a': {
        'foreground': curses.COLOR_RED,
        'background': None,
    },
}

keys = {
    'quit': (ord('q'), ord('Q')),
    'toggle-status': (ord('s'),),
    'search': (ord('/'),),
    'scroll-fifo': (ord('f'),),
    'auto-scroll': (ord('a'),),
    'search-next': (ord('n'),),
    'timer-inc': (ord('+'),),
    'timer-dec': (ord('-'),),
    'goto-percent': (ord('5'), ord('G')),
    'jump-link': (ord('\t'),),
    'goto-link': (curses.KEY_ENTER, ord('\n'), curses.KEY_RIGHT),
    'backward': (curses.KEY_LEFT, ord('h')),
    'forward': (curses.KEY_BACKSPACE, ord('l'),),
    'scroll-up': (curses.KEY_UP, ord('k')),
    'scroll-down': (curses.KEY_DOWN, ord('j')),
    'next-page': (ord(' '), curses.KEY_NPAGE),
    'prev-page': (curses.KEY_PPAGE,),
    'goto-home': (ord('g'), curses.KEY_HOME,),
    'goto-end': (curses.KEY_END,),
    'edit-xml': (ord('o'),),
}


def typed_get(config, section, sectiondict, key, value):
    """ Get config value with given type
    """
    if isinstance(sectiondict[section][key], bool):
        return config.getboolean(section, key)
    elif (
            isinstance(sectiondict[section][key], int)
            and key not in ('foreground', 'background')
    ):
        return config.getint(section, key)
    elif key in ('foreground', 'background'):
            # foreground and background are some integral constants, but
            # they're represented with string values in config file
            # we should make conversion
            return COLORS[value]
    elif isinstance(sectiondict[section][key], tuple) and section == 'keys':
        # curses needs codes, not actual symbols keys produce.
        # Moreover, some keys are specified by the name like
        # 'space' or 'pgdn'. So let's do some processing.
        return tuple(
            [convert_key(keyname.strip()) for keyname in value.split(',')]
        )
    else:
        return config.get(section, key)


def convert_key(key):
    if key in SPECIAL_KEYS:
        return SPECIAL_KEYS[key]
    else:
        return(ord(key))

# Let's load settings from config:


config = ConfigParser.RawConfigParser()
config.read(CONFIG_FILES)

for d, section in (
    [(globals(), section) for section in ['paths', 'general', 'keys']]
    + [(styles, style) for style in styles]
):
    if config.has_section(section):
        d[section].update([
            (
                key,
                typed_get(config, section, d, key, value),
            )
            for (key, value) in config.items(section)
            if key in d[section]
        ])
