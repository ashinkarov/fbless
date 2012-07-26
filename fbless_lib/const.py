# -*- mode: python; coding: utf-8; -*-
#
import curses

VERSION = '0.2.2'

# constant for auto scroll
NO_SCROLL = None
SCROLL_FIFO = "scroll_fifo"
SCROLL_DOWN = "scroll_down"
SCROLL_UP = "scroll_up"
NEXT_PAGE = "next_page"
PREV_PAGE = "prev_page"


SPECIAL_KEYS = {
    'left': curses.KEY_LEFT,
    'right': curses.KEY_RIGHT,
    'up': curses.KEY_UP,
    'down': curses.KEY_DOWN,
    'enter': curses.KEY_ENTER,
    'return': curses.KEY_ENTER,
    'backspace': curses.KEY_BACKSPACE,
    'bksp': curses.KEY_BACKSPACE,
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
