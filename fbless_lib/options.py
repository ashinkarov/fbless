# -*- mode: python; coding: utf-8; -*-
#

import curses
import ConfigParser
import os

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


### Loading configuration

def read_style_settings(config, stylename):
    """ Read settings for the given style from the given config.

        Try to cast values to the types they have in the options dictionary.
    """
    if stylename not in options.keys():
        return

    if stylename not in config.sections():
        return

    for (k, v) in options[stylename].items():
        try:
            # have to parse bool before int because the latter is implicitly
            # casted to the former, thus causing attempt to parse bool as int
            if isinstance(v, bool):
                options[stylename][k] = config.getboolean(stylename, k)
            # foreground and background are some integral constants, but in
            # config they are represented by string values
            elif isinstance(v, int) and k not in ['foreground', 'background']:
                options[stylename][k] = config.getint(stylename, k)
            else:
                options[stylename][k] = config.get(stylename, k)
        except ConfigParser.NoOptionError:
            # It's okay, user simply didn't bother to redefine the option
            pass

        # TODO: what could go wrong? Can we provide user with meaningful error
        # messages and not just staketraces?

    # In config, colors are specified with strings, but we need curses
    # constants. Let's convert 'em all!
    for style in options.keys():
        for c in ['foreground', 'background']:
            if isinstance(options[style][c], str):
                options[style][c] = COLORS[options[style][c]]

### Defaults

save_file = '~/.cache/fbless/fbless_save'  # FIXME: need XDG
context_lines = 0
status = True

# screen width. 0 means autodetect
columns = 0
# if True and 'columns' is set, the text would be centered
center_text = False

# use default terminal colors
use_default_colors = True

replace_chars = False

editor = 'vim -c go{byte_offset} "{filename}"'

# interval for autoscroll in sec
auto_scroll_interval = 3

options = {
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
config = ConfigParser.RawConfigParser()
expand = lambda x: os.path.expanduser(x)
config.read(map(expand, ["~/.config/fbless/fblessrc", "~/.fblessrc"]))

for style in options.keys():
    read_style_settings(config, style)

if 'paths' in config.sections():
    try:
        save_file = config.get('paths', 'save_file')
    except ConfigParser.NoOptionError:
        pass

if 'general' in config.sections():
    try:
        context_lines = config.getint('general', 'context_lines')
        auto_scroll_interval = config.getint('general', 'auto_scroll_interval')
        columns = config.getint('general', 'columns')

        status = config.getboolean('general', 'status')
        center_text = config.getboolean('general', 'center_text')
        use_default_colors = config.getboolean('general', 'use_default_colors')
        replace_chars = config.getboolean('general', 'replace_chars')

        editor = config.get('general', 'editor')
    except ConfigParser.NoOptionError:
        # User choose not to redefine some value. No problem!
        pass

if 'keys' in config.sections():
    try:
        for key in keys.keys():
            bindings = config.get('keys', key)
            # curses needs codes, not actual symbols keys produce.
            # Moreover, some keys are specified by the name like
            # 'space' or 'pgdn'. So let's do some processing.
            processed = []

            for b in bindings.split(','):
                if b.strip() not in SPECIAL_KEYS.keys():
                    processed.append(ord(b.strip()))
                else:
                    processed.append(SPECIAL_KEYS[b.strip()])
            keys[key] = processed
    except ConfigParser.NoOptionError:
        pass
