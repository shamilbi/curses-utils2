import curses
from typing import Protocol

from curses_utils2.win import win_addstr


class WinProto(Protocol):
    def set_win(self, win: curses.window):
        pass

    def refresh(self):
        pass


class ListBox:
    '''
    win (box + header) + win (List)

    -----------------------------
    | header                    |
    | List                      |
    |                           |
    -----------------------------

    '''

    def __init__(self, list_: WinProto, header: int = 0):
        self.list_ = list_
        self.header = header

    def set_win(self, win: curses.window):
        # pylint: disable=attribute-defined-outside-init
        self.win = win

        # list win
        rows, cols = win.getmaxyx()
        win2 = win.derwin(rows - 2 - self.header, cols - 4, 1 + self.header, 2)
        self.list_.set_win(win2)

    def refresh(self, header: str):
        self.win.erase()
        win_addstr(self.win, 1, 2, header)
        self.win.box()
        self.win.refresh()

        self.list_.refresh()
