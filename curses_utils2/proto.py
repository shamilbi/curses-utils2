from __future__ import annotations

import curses
from typing import Protocol


class WinProto(Protocol):
    def set_win(self, win: curses.window | None):
        pass

    def refresh(self):
        pass
