from __future__ import annotations

import curses

from .proto import WinProto
from .win import win_addstr


class WinBox:
    '''
    win (box) + internal win (body)

    '''

    def __init__(self, body: WinProto, offy: int = 0, offx: int = 0):
        'offy: y offset, offx: x offset'
        self.body = body
        self.offy, self.offx = offy, offx

    def set_win(self, win: curses.window | None):
        # pylint: disable=attribute-defined-outside-init
        self.win = win

        if not win:
            self.body.set_win(None)
            return

        # body win
        rows, cols = win.getmaxyx()
        rows2 = rows - 2 - self.offy  # 2 - border
        cols2 = cols - 2 - 2 * self.offx  # 2 - border
        if rows2 < 0 or cols < 2:
            self.win = None
            self.body.set_win(None)
            return
        if rows2 < 1 or cols2 < 1:
            self.body.set_win(None)
            return
        win2 = win.derwin(
            rows2,
            cols2,
            1 + self.offy,  # 1 - border
            1 + self.offx,  # 1 - border
        )
        self.body.set_win(win2)

    def refresh(self, header: str = ''):
        if not self.win:
            return

        self.win.erase()
        if header:
            # put header above body
            win_addstr(self.win, 1, 1 + self.offx, header, border=1 + self.offx)
        self.win.box()
        self.win.refresh()

        self.body.refresh()
