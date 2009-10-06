#!/usr/bin/env python
# -*- mode: python; coding: koi8-r; -*-
#

## COLOR_BLACK   Black
## COLOR_BLUE    Blue
## COLOR_CYAN    Cyan (light greenish blue)
## COLOR_GREEN   Green
## COLOR_MAGENTA Magenta (purplish red)
## COLOR_RED     Red
## COLOR_WHITE   White
## COLOR_YELLOW  Yellow
import curses

rc_file = '~/.fbless_save'
context_lines = 0
status = True

use_default_colors = True               # use default terminal colors

replace_chars = False #True

editor = 'vim -c go%s %s'               # first %s - byte index
                                        # second %s - file name

options = {
    'default':     {'justify'           : 'fill',
                    'hyphenate'         : True,
                    'left_indent'       : 2,
                    'right_indent'      : 2,
                    'first_line_indent' : 4,
                    'foreground'        : curses.COLOR_WHITE,
                    'background'        : curses.COLOR_BLACK,
                  },
    'p':           {'justify'           : 'fill',
                    'hyphenate'         : True,
                    'left_indent'       : 2,
                    'right_indent'      : 2,
                    'first_line_indent' : 4,
                    'foreground'        : None,
                    'background'        : None,
                  },
    'v':           {'justify'           : 'fill',
                    'hyphenate'         : True,
                    'left_indent'       : 10,
                    'right_indent'      : 4,
                    'first_line_indent' : 0,
                    'foreground'        : None,
                    'background'        : None,
                    },
    'text-author': {'justify'           : 'right',
                    'hyphenate'         : True,
                    'left_indent'       : 20,
                    'right_indent'      : 2,
                    'first_line_indent' : 0,
                    'foreground'        : curses.COLOR_YELLOW,
                    'background'        : None,
                    },
    'epigraph':    {'justify'           : 'fill',
                    'hyphenate'         : True,
                    'left_indent'       : 20,
                    'right_indent'      : 2,
                    'first_line_indent' : 4,
                    'foreground'        : None,
                    'background'        : None,
                    },
    'cite':        {'justify'           : 'fill',
                    'hyphenate'         : True,
                    'left_indent'       : 8,
                    'right_indent'      : 8,
                    'first_line_indent' : 8,
                    'foreground'        : None,
                    'background'        : None,
                    },
    'title':       {'justify'           : 'center',
                    'hyphenate'         : False,
                    'left_indent'       : 8,
                    'right_indent'      : 8,
                    'first_line_indent' : 0,
                    'foreground'        : curses.COLOR_MAGENTA,
                    'background'        : None,
                    },
    'subtitle':    {'justify'           : 'center',
                    'hyphenate'         : False,
                    'left_indent'       : 8,
                    'right_indent'      : 8,
                    'first_line_indent' : 0,
                    'foreground'        : curses.COLOR_CYAN,
                    'background'        : None,
                    },
    'image':       {'justify'           : 'center',
                    'hyphenate'         : False,
                    'left_indent'       : 0,
                    'right_indent'      : 0,
                    'first_line_indent' : 0,
                    'foreground'        : None,
                    'background'        : None,
                    },
    'strong':      {'foreground'        : curses.COLOR_MAGENTA,
                    'background'        : None,
                    },
    'emphasis':    {'foreground'        : curses.COLOR_CYAN,
                    'background'        : None,
                    },
    'style':       {'foreground'        : curses.COLOR_GREEN,
                    'background'        : None,
                    },
    'a':           {'foreground'        : curses.COLOR_RED,
                    'background'        : None,
                    },
    }


keys = {
    'quit'          : (ord('q'), ord('Q')),
    'toggle-status' : (ord('s'),),
    'search'        : (ord('f'), ord('/'),),
    'search-next'   : (ord('n'),),
    'goto-percent'  : (ord('5'), ord('G')),
    'jump-link'     : (ord('\t'), ord('j')),
    'goto-link'     : (curses.KEY_ENTER, ord('\n'), curses.KEY_RIGHT),
    'backward'      : (curses.KEY_LEFT,),
    'foreward'      : (curses.KEY_BACKSPACE, ord('l'),),
    'scroll-up'     : (curses.KEY_UP,),
    'scroll-down'   : (curses.KEY_DOWN,),
    'next-page'     : (ord(' '), curses.KEY_NPAGE),
    'prev-page'     : (curses.KEY_PPAGE,),
    'goto-home'     : (ord('g'), curses.KEY_HOME,),
    'goto-end'      : (curses.KEY_END,),
    'edit-xml'      : (ord('o'),),
}

