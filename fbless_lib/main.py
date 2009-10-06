#!/usr/bin/env python
# -*- mode: python; coding: koi8-r; -*-
#

import sys, os
import re
import traceback
import locale
import signal
import zipfile
from cStringIO import StringIO
import time
import curses
import curses.ascii as ascii

from fb2parser import fb2parse
from paragraph import attr
import options


default_charset = locale.getdefaultlocale()[1]


class MainWindow:

    def __init__(self):

        self.filename = None
        if len(sys.argv) > 1:
            self.filename = os.path.abspath(sys.argv[1])
        self.par_index = 0
        self.line_index = 0
        positions = self.load_positions()
        if self.filename is None and not positions:
            sys.exit('missing filename')
        if self.filename is None:
            # load last file
            l = positions[0]
            self.filename = l[0]
            self.par_index = int(l[1])
            self.line_index = int(l[2])
        else:
            for l in positions:
                if l[0] == self.filename:
                    self.par_index = int(l[1])
                    self.line_index = int(l[2])
                    break
        self.basename = os.path.basename(self.filename)

        self.back_history = []
        self.fore_history = []

        self.message = ''
        self.message_timeout = 0

        signal.signal(signal.SIGWINCH, self.resize_window)
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        if options.use_default_colors:
            curses.use_default_colors()
        self.init_color()
        self.init_screen(self.screen)

        #~curses.mousemask(curses.ALL_MOUSE_EVENTS)

        self.link_pos = [] # for <a> elements; list of tuples (y, x, link_name)
        self.cur_link = 0         # current cursor position; index of link_pos
        self.content = create_content(self.filename, curses.COLS)
        self.update_status = True

        self.redraw_scr()

    def init_screen(self, screen):
        screen.keypad(1)
        screen.nodelay(1)
        screen.scrollok(True)
        #screen.idlok(True)

    def load_positions(self):
        positions = []
        try:
            d = open(os.path.expanduser(options.rc_file)).read()
        except:
            pass
        else:
            l = d.splitlines()
            for s in l:
                try:
                    fn, par_index, line_index = s.rsplit(' ', 2)
                    positions.append((fn, par_index, line_index))
                except:
                    traceback.print_exc(file=sys.stdout)
        return positions

    def save_position(self):
        positions = self.load_positions()
        save_pos = [(self.filename, str(self.par_index), str(self.line_index))]
        for l in positions:
            if l[0] != self.filename:
                save_pos.append(l)
        fd = open(os.path.expanduser(options.rc_file), 'w')
        for l in save_pos:
            print >> fd, ' '.join(l)

    def init_color(self):
        n = 1
        for i in options.options:
            fg = options.options[i]['foreground']
            bg = options.options[i]['background']
            if fg is None and bg is None:
                options.options[i]['color'] = None
                continue
            if fg is None:
                fg = options.options['default']['foreground']
            if bg is None:
                bg = options.options['default']['background']
            curses.init_pair(n, fg, bg)
            options.options[i]['color'] = n
            n += 1
        if not options.use_default_colors:
            n = options.options['default']['color']
            self.screen.bkgdset(ord(' '), curses.color_pair(n))

    def add_str(self, line, type):
        # add string to current cursor position

        if type in options.options:
            opt = options.options[type]
        else:
            opt = options.options['default']

        cur_attr = None
        in_search = False
        for s in line:
            if isinstance(s, int):
                # attribute
                if s == attr.strong:
                    cur_attr = options.options['strong']['color']
                elif s == attr.emphasis:
                    cur_attr = options.options['emphasis']['color']
                elif s == attr.style:
                    cur_attr = options.options['style']['color']
                elif s == attr.left_spaces:
                    # leading spaces
                    cur_attr = s #options.options['default']['color']
                elif s == attr.search:
                    in_search = True
                    pass
                elif s == attr.cancel_search:
                    in_search = False
                else:
                    cur_attr = None
                continue

            elif isinstance(s, tuple):
                # link
                cur_attr = options.options['a']['color']
                yx = list(self.screen.getyx())
                yx.append(s[1])         # add link name (href)
                self.link_pos.append(yx)
                continue

            # string
            s = s.encode(default_charset, 'replace')
            if in_search:
                a = curses.A_REVERSE
            else:
                a = curses.A_NORMAL
            if cur_attr == attr.left_spaces:
                self.screen.addstr(s, a)
            elif cur_attr is not None:
                # strong, emphasis, etc...
                color = curses.color_pair(cur_attr)
                self.screen.addstr(s, color|a)
            else:
                if opt['color'] is not None:
                    color = curses.color_pair(opt['color'])
                    self.screen.addstr(s, color|a)
                else:
                    self.screen.addstr(s, a)

    def redraw_scr(self):
        # redraw screen
        self.link_pos = []              # remove links
        self.cur_link = 0
        self.screen.clear()
        _par_index, _line_index = self.par_index, self.line_index
        i = 0
        while True:
            try:
                s, type = self.content.get(_par_index, _line_index)
            except IndexError:
                break
            self.add_str(s, type)
            _par_index, _line_index = self.content.indexes()
            i += 1
            if i > curses.LINES - options.status - 1:
                break
            self.screen.move(i, 0)
            _line_index += 1

    def toggle_status(self, status):
        # toggle status
        #options.status = not options.status
        self.update_status = True
        if not status:
            self.screen.move(curses.LINES-1, 0)
            self.screen.clrtoeol()
            n = curses.LINES - 1
            try:
                s, type = self.content.get(self.par_index, self.line_index+n)
            except IndexError:
                # EOF
                pass
            else:
                self.add_str(s, type)

        if status:
            self.update_links_pos()

    def update_links_pos(self, d=0):
        # Note: this function calling before scrolling
        if not self.link_pos:
            return
        lines = curses.LINES - options.status
        links = []
        i = 0
        for link in self.link_pos:
            link[0] -= d
            if 0 <= link[0] < lines:
                links.append(link)
            else:
                # link removed
                i += 1
        if i == 0:
            # no changes
            return
        # re-sort links
        if links:
            link = self.link_pos[self.cur_link]
            links.sort()
            if link in links:
                self.cur_link = links.index(link)
            else:
                if d == 1:
                    # first link (scroll down)
                    self.cur_link = 0
                else:
                    # last link (scroll up)
                    self.cur_link = len(links) - 1
        else:
            self.cur_link = 0

        self.link_pos = links

    def get_str(self, validator):
        #curses.echo()
        #self.screen.nodelay(0)
        s = ''
        while True:
            ch = self.screen.getch()
            if ch in (curses.KEY_ENTER, ascii.NL):
                break
            #elif ch in (curses.KEY_ENTER, ord('\n')):
            #    return ''
            elif ch in (curses.KEY_BACKSPACE, curses.KEY_LEFT,
                        ascii.DEL, ascii.BS):
                if not s: break
                y, x = curses.getsyx()
                self.screen.move(y, x-1)
                self.screen.delch()
                s = s[:-1]
            elif validator(ch):
                self.screen.addstr(chr(ch))
                s += chr(ch)
        return s

    def search(self):
        self.update_status = True
        self.screen.move(curses.LINES-1, 0)
        self.screen.clrtoeol()
        self.screen.addstr('Search pattern: ')
        self.screen.nodelay(0)
        def validator(ch):
            # FIXME
            #print '>', ch
            #return True
            return 0 <= ch < 256
##             try:
##                 uch = unicode(ch, default_charset)
##             except Exception, ex:
##                 #print '--', ex
##                 return False
##             return True
        s = self.get_str(validator)
        s = unicode(s, default_charset)
        self.screen.nodelay(1)
        #print 'search:', s.encode(default_charset)
        if not s:
            return
        found = self.content.search(s, self.par_index, self.line_index)
        if found in (0, -1):
            self.redraw_scr()
            if found == 0:
                self.message = 'Pattern not found '
            else:
                self.message = 'Invalid pattern '
            return
        self.par_index, self.line_index = found
        self.redraw_scr()

    def search_next(self):
        if not self.content.search_string:
            self.message = 'No previous regular expression'
            return
        self.update_status = True
        found = self.content.search(self.content.search_string,
                                    self.par_index, self.line_index+1)
        if not found:
            self.redraw_scr()
            self.message = 'ERROR: Pattern not found ' # 
            return
        self.par_index, self.line_index = found
        self.redraw_scr()

    def goto_percent(self):
        # FIXME
        self.screen.move(curses.LINES-1, 0)
        self.screen.clrtoeol()
        self.screen.addstr('Go(%): ')
        self.screen.nodelay(0)
        #curses.echo()
        #s = self.screen.getstr()
        def validator(ch):
            return ch < 256 and chr(ch) in '0123456789'
        s = self.get_str(validator)
        #print 'str:', s
        #self.screen.nodelay(1)
        #curses.noecho()
        self.update_status = True
        try:
            pos = float(s)
        except:
            return
        if pos < 0 or pos > 100:
            return

        if 1: #pos:
            self.par_index, self.line_index = self.content.get_position(pos)
            self.redraw_scr()
        #curses.noecho()
        #self.screen.nodelay(1)

    def goto_link(self):
        if self.link_pos:
            id = self.link_pos[self.cur_link][2]
            if id.startswith('#'):
                id = id[1:]
            else:
                print 'external link:', id
                return
            i = self.content.get_by_id(id)
            if i is None:
                self.message = 'Link not found '
            else:
                self.back_history.append((self.par_index, self.line_index))
                self.fore_history = []
                self.update_status = True
                self.par_index = i
                self.line_index = 0
                self.redraw_scr()

    def goto_backward(self):
        if self.back_history:
            self.update_status = True
            pos = self.back_history.pop()
            self.fore_history.append((self.par_index,
                                      self.line_index))
            self.par_index, self.line_index = pos
            self.redraw_scr()

    def goto_foreward(self):
        if self.fore_history:
            self.update_status = True
            pos = self.fore_history.pop()
            self.back_history.append((self.par_index,
                                      self.line_index))
            self.par_index, self.line_index = pos
            self.redraw_scr()

    def jump_link(self):
        if not self.link_pos:
            return
        self.cur_link = (self.cur_link + 1) % len(self.link_pos)
        pos = self.link_pos[self.cur_link]
        self.screen.move(*pos[:2])

    def scroll_up(self):
        if self.par_index == 0 and self.line_index == 0:
            return
        self.update_status = True
        self.screen.scroll(-1)
        self.line_index -= 1

        self.update_links_pos(-1)

        s, type = self.content.get(self.par_index, self.line_index)
        self.screen.move(0, 0)
        self.add_str(s, type)
        self.par_index, self.line_index = self.content.indexes()

    def scroll_down(self):
        n = curses.LINES - options.status
        try:
            s, type = self.content.get(self.par_index, self.line_index+n)
        except IndexError:
            # EOF
            return
        self.update_status = True

        self.update_links_pos(1)

        self.screen.scroll(1)
        self.screen.move(curses.LINES-1-options.status, 0)
        self.screen.clrtoeol()
        self.add_str(s, type)

        self.line_index += 1
        self.par_index, self.line_index = self.content.indexes(
            self.par_index, self.line_index)

    def next_page(self):
        n = curses.LINES - options.context_lines - options.status
        try:
            s, type = self.content.get(self.par_index, self.line_index+n)
        except IndexError:
            # EOF
            return
        self.update_status = True
        self.line_index += n
        self.redraw_scr()
        self.par_index, self.line_index = self.content.indexes(
            self.par_index, self.line_index)

    def prev_page(self):
        if self.par_index == 0 and self.line_index == 0:
            return
        self.update_status = True
        n = curses.LINES - options.context_lines - options.status
        self.line_index -= n
        self.redraw_scr()
        self.par_index, self.line_index = self.content.indexes(
            self.par_index, self.line_index)

    def goto_home(self):
        if self.par_index == 0 and self.line_index == 0:
            return
        self.update_status = True
        self.par_index = self.line_index = 0
        self.redraw_scr()

    def goto_end(self):
        self.update_status = True
        self.par_index, self.line_index = \
                        self.content.get_end_indexes(curses.LINES)
        self.redraw_scr()

    def resize_window(self, *args):
        #self.screen.refresh()
        curses.endwin()
        self.screen = curses.initscr()
        self.update_status = True
        curses.LINES, curses.COLS = self.screen.getmaxyx()
        self.content.update(curses.COLS)
        self.redraw_scr()
        #print >> file('log', 'a'), self.screen.getmaxyx()
        #print >> file('log', 'a'), curses.LINES, curses.COLS
        #print >> file('log', 'a'), '>>', self.screen.getbegyx()

    def draw_status(self, _time):
        self.screen.move(curses.LINES-1, 0)
        self.screen.clrtoeol()
        status = ''
        end_line = self.line_index + curses.LINES - 1
        status += ' %d%%' % self.content.position(
            self.par_index, end_line)
##         if 1: # debug
##             status += ' (%d/%d/%d)' % (self.par_index,
##                                        self.line_index,
##                                        len(self.content._content))
        status += _time
        n = curses.COLS - 2 - len(status)
        status = self.basename[:n] + status
        self.screen.addstr(status, curses.A_REVERSE)

    def draw_message(self, message):
        self.screen.move(curses.LINES-1, 0)
        self.screen.clrtoeol()
        self.screen.addstr(message, curses.A_REVERSE)

    def edit_xml(self):
        par = self.content._content[self.par_index]
        byte_index = par.byte_index
        curses.def_prog_mode()          # save current tty modes
        curses.endwin()
        os.system(options.editor % (byte_index, self.filename))
        self.screen = curses.initscr()


    def main_loop(self):
        cur_time = ''

        while True: # main loop
            ch = self.screen.getch()
            #ch = curses.wgetch()

            if ch in options.keys['quit']:
                break

            elif ch in options.keys['toggle-status']:
                options.status = not options.status
                self.toggle_status(options.status)

            elif ch in options.keys['goto-percent']:
                self.goto_percent()

            elif ch in options.keys['search']:
                self.search()

            elif ch in options.keys['search-next']:
                self.search_next()

            elif ch in options.keys['jump-link']:
                self.jump_link()

            elif ch in options.keys['goto-link']:
                self.goto_link()

            elif ch in options.keys['backward']:
                self.goto_backward()

            elif ch in options.keys['foreward']:
                self.goto_foreward()

            elif ch in options.keys['scroll-up']:
                self.scroll_up()

            elif ch in options.keys['scroll-down']:
                self.scroll_down()

            elif ch in options.keys['next-page']:
                self.next_page()

            elif ch in options.keys['prev-page']:
                self.prev_page()

            elif ch in options.keys['goto-home']:
                self.goto_home()

            elif ch in options.keys['goto-end']:
                self.goto_end()

##             elif ch in options.keys['edit-xml']:
##                 self.edit_xml()

##             elif ch in (curses.KEY_MOUSE,):
##                 print 'mouse:', curses.getmouse()

            #elif hasattr(curses, 'KEY_RESIZE') and ch in (curses.KEY_RESIZE,):
##             elif ch in (curses.KEY_RESIZE,):
##                 print >> file('log', 'w'), 'KEY_RESIZE'
##                 self.resize_window()

##             elif ch != -1:
##                 print 'ch:', ch

            if self.message:
                self.message_timeout = 1000 # milliseconds
                self.draw_message(self.message)
                self.toggle_status(True) # in case if links has been removed
                self.message = ''

            elif options.status:
                _time = time.strftime(' %H:%M ')
                if _time != cur_time:
                    self.update_status = True

            if self.message_timeout:
                self.message_timeout -= 10
                if self.message_timeout <= 0:
                    self.message_timeout = 0
                    self.update_status = True
                    self.toggle_status(options.status) # restore status

            if self.update_status and self.message_timeout <= 0:

                if options.status:
                    self.draw_status(_time)

                if self.link_pos:
                    # move cursor to current link
                    pos = self.link_pos[self.cur_link]
                    self.screen.move(*pos[:2])

                elif not options.status:
                    # move cursor to bottom-right corner
                    self.screen.move(curses.LINES-1, curses.COLS-1)

            self.update_status = False
            cur_time = _time

            curses.napms(10)

        # end of loop
        self.save_position()




class Content:
    def __init__(self, content, scr_cols):
        self._content = content
        self._content_len = 0
        for par in content:
            self._content_len += len(par.data)
        self._par_index = self._line_index = 0
        self.scr_cols = scr_cols
        self.links = {}
        self.search_string = ''

    def get(self, par_index, line_index):
        if par_index < 0:
            par_index = 0
            line_index = 0
        if line_index < 0 and par_index == 0:
            line_index = 0

##         if par_index >= len(self._content):
##             raise IndexError

        if line_index < 0:
            par_index -= 1
            par = self._content[par_index]
            self._split_par(par)
            line_index += len(par.lines)
            return self.get(par_index, line_index)

        par = self._content[par_index]
        self._split_par(par)
        try:
            line = par.lines[line_index]
        except IndexError:
            par_index += 1
            line_index -= len(par.lines)
            return self.get(par_index, line_index)

        self._par_index, self._line_index = par_index, line_index
        return line, par.type

    def set_search_offsets(self, par):
        s = self.search_string
        if not s:
            par.search_offsets = []
            return
        offsets = []
        regex = re.compile(s, re.IGNORECASE|re.UNICODE)
        m = regex.search(par.data)
        while m:
            offsets.append((m.start(), m.end()))
            m = regex.search(s, m.end())
        par.search_offsets = offsets

    def indexes(self, par_index=None, line_index=None):
        if par_index is None and line_index is None:
            return self._par_index, self._line_index
        self.get(par_index, line_index)
        return self._par_index, self._line_index

    def get_by_id(self, id):
        if not self.links:
            # create links dictionary
            i = 0
            for par in self._content:
                if par.id and par.id not in self.links:
                    self.links[par.id] = i
                i += 1
        return self.links.get(id)

    def get_end_indexes(self, scr_lines):
        i = scr_lines
        par_index = len(self._content)
        for par in self._content[::-1]:
            self._split_par(par)
            i -= len(par.lines)
            par_index -= 1
            if i <= 0:
                break
        line_index = -i+1
        return par_index, line_index

    def position(self, par_index, line_index):
        # FIXME
        try:
            par_index, line_index = self.indexes(par_index, line_index)
        except IndexError:
            # EOF
            par_index = len(self._content)
            line_index = 0

        n = 0
        for par in self._content[:par_index]:
            n += len(par.data)

##         for par in self._content[:par_index-1]:
##             n += len(par.data)
##         for line in self._content[par_index].lines[:line_index]:
##             n += len(line)

        pos = float(n)/self._content_len
        if pos > 1: pos = 1
        pos = int(pos*100)
        return pos

    def get_position(self, percent):
        # FIXME
        percent = float(percent)/100
        total = self._content_len
        n = 0
        i = 0
        for par in self._content:
            n += len(par.data)
            if float(n)/total > percent:
                t = curses.LINES - options.context_lines - options.status
                par_index, line_index = self.indexes(i, -t) # back one screen
                return par_index, line_index
            i += 1
        return i-1, 0

    def _split_par(self, par):
        par.scr_cols = self.scr_cols
        self.set_search_offsets(par)
        par.split_string()

    def search(self, s, par_index, line_index):
        if par_index < len(self._content)-1:
            par_index, line_index = self.indexes(par_index, line_index)
        try:
            regex = re.compile(s, re.IGNORECASE|re.UNICODE)
        except re.error:
            return -1

        def do_search(paragraphs):
            i = 0
            for par in paragraphs:
                m = regex.search(par.data)
                if m:
                    if s != self.search_string:
                        self.search_string = s
                        self.update()
                    self._split_par(par)
                    if i == 0:
                        lines = par.lines[line_index:]
                        j = line_index
                    else:
                        lines = par.lines
                        j = 0
                    found = False
                    for ln in lines:
                        if attr.search in ln:
                            found = True
                            break
                        j += 1
                    if found:
                        return i, j
                i += 1
            return 0

        found = do_search(self._content[par_index:])
        if found:
            return found[0]+par_index, found[1]
        # overwrapped search
        line_index = 0
        found = do_search(self._content[:par_index])
        if found:
            return found
        self.search_string = ''
        self.update()
        return 0

    def update(self, scr_cols=None):
        # window geometry changed
        if scr_cols is not None:
            self.scr_cols = scr_cols
        for par in self._content:
            par.lines = []


def create_content(filename, scr_cols):

    if zipfile.is_zipfile(filename):
        zf = zipfile.ZipFile(filename)
        for zip_filename in zf.namelist():
            data = zf.read(zip_filename)
            if data.startswith('<?xml'):
                break
        else:
            sys.exit('zip archive: xml file not found')
    else:
        data = open(filename).read()
        if data.startswith('BZh'):
            import bz2
            data = bz2.decompress(data)
        elif data.startswith('\x1f\x8b'):
            import gzip
            data = gzip.GzipFile(fileobj=StringIO(data)).read()
    content = fb2parse(data)

    return Content(content, scr_cols)


if __name__ == '__main__':
    c = create_content(sys.argv[1], 72)
    pi, li = 0, 0
    i = 0
    while True:
        try:
            s, t = c.get(pi, li)
        except IndexError:
            break
        print t, '>'+s+'<'
        pi, li = c.indexes()
        li += 1
        i += 1
        if i > 200:
            break
    print '---------->', pi, li
    s, t = c.get(pi, li-32)
    print s
    print c.indexes()
    #while True:
    #    s, t = c.get(pi, li)
##     try:
##         main()
##     finally:
##         try:
##             curses.endwin()
##         except:
##             pass


