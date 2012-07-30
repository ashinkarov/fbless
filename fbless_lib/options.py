# -*- mode: python; coding: utf-8; -*-
""" Default options dicts and config files parser
"""
import curses
import ConfigParser
import os
import defaults
import const 
import sys
import argparse

paths = dict(defaults.paths)
general = dict(defaults.general)
keys = dict(defaults.keys)
styles = dict(defaults.styles)

try:
    from xdg.BaseDirectory import xdg_config_home
except ImportError:
    xdg_config_home = os.path.expanduser('~/.config')

CONFIG_FILES = [
    os.path.join(xdg_config_home, "fbless", "fblessrc"),
    os.path.expanduser("~/.fblessrc"),
]


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
        if value in const.COLORS:
            return value
        else:
            return config.getint(section, key)
    elif section == 'keys':
        return tuple([keyname.strip() for keyname in value.split(',')])
    else:
        return config.get(section, key)


def convert_key(keyname):
    """ Curses needs codes, not actual symbols keys produce.
        Moreover, some keys are specified by the name like
        'space' or 'pgdn'. So we need some processing.
    """
    try:
        return const.SPECIAL_KEYS[keyname]
    except KeyError:
        return(ord(keyname))

def get_keys(keysgroup):
    """ Convert tuple or other iterable of keys
    """
    return tuple([convert_key(keyname) for keyname in keys[keysgroup]])

def convert_color(colorname):
    """ Convert color names to numeric codes
    """

    try:
        return const.COLORS[colorname]
    except KeyError:
        if colorname:
            return(int(colorname))
        else:
            return(colorname)

def parse_arguments():
    parser = argparse.ArgumentParser(description = 'fb2 console reader', version = const.VERSION)
    parser.add_argument('file', nargs = '?',
                        help = 'fb2, zip, gzip or bzip2 file')
    parser.add_argument('-a', '--autoscroll', action = 'store_true',
                        help = 'enable auto-scroll')
    parser.add_argument('-t', '--scroll_type', choices = ['down', 'up', 
                        'page-down', 'page-up', 'fifo'],
                        help = 'auto-scroll type (down, up, page-down, page-up, fifo)')
    parser.add_argument('-i', '--interval', type = int, metavar = 'sec.',
                        help = 'auto-scroll time interval')
    parser.add_argument('-g', '--goto', type = int, metavar = '%',
                        help = 'go to the offset (in percent)')
    parser.add_argument('-e', '--edit', action = 'store_true',
                        help = 'open in the editor')
    args = parser.parse_args()

    if args.file:
        general['filename'] = args.file
    else:
        general['filename'] = None

    if args.autoscroll:
        general['auto_scroll'] = True
    else:
        general['auto_scroll'] = False

    if args.scroll_type:
        if args.scroll_type == 'down':
           general['auto_scroll_type'] = const.SCROLL_DOWN
        elif args.scroll_type == 'up':
           general['auto_scroll_type'] = const.SCROLL_UP
        elif args.scroll_type == 'page-down':
            general['auto_scroll_type'] = const.NEXT_PAGE
        elif args.scroll_type == 'page-up':
            general['auto_scroll_type'] = const.PREV_PAGE
        elif args.scroll_type == 'fifo':
            general['auto_scroll_type'] = const.SCROLL_FIFO
    else:
        general['auto_scroll_type'] = const.NO_SCROLL

    if args.interval:
        general['auto_scroll_interval'] = args.interval

    if args.goto:
        general['percent'] = args.goto
    else:
        general['percent'] = None
    
    if args.edit:
        general['edit_xml'] = True
    else:
        general['edit_xml'] = False

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
