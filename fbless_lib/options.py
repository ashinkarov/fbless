# -*- mode: python; coding: utf-8; -*-
""" Default options dicts and config files parser
"""
import curses
import ConfigParser
import os

from const import SPECIAL_KEYS, COLORS
from defaults import paths, general, keys, styles

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
        try:
            return COLORS[value]
        except KeyError:
            return config.getint(section, key)
    elif isinstance(sectiondict[section][key], tuple) and section == 'keys':
        return tuple(
            [convert_key(keyname.strip()) for keyname in value.split(',')]
        )
    else:
        return config.get(section, key)


def convert_key(keyname):
    """ Curses needs codes, not actual symbols keys produce.
        Moreover, some keys are specified by the name like
        'space' or 'pgdn'. So we need some processing.
    """

    try:
        return SPECIAL_KEYS[keyname]
    except KeyError:
        return(ord(keyname))

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
