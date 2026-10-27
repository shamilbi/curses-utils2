'switch between AppProto'

from __future__ import annotations

import curses
import curses.ascii
import os
import sys
from collections.abc import Generator
from contextlib import contextmanager
from signal import SIGINT, SIGTERM, SIGWINCH, signal
from typing import Protocol

from .win import get_alt_key


class AppProto(Protocol):
    parent: AppSwitchProto

    def sigwinch_handler(self, *_):
        pass

    def handle_alt_key(self, ch: int):
        pass

    def handle_key(self, ch: int) -> str | None:  # switch to another app?
        pass


class AppSwitchProto(Protocol):
    screen: curses.window

    @contextmanager
    def escape2terminal(self):
        pass

    def input_search(self, prompt: str) -> tuple[bool, str]:  # ok, search str
        pass


class AppSwitch(AppSwitchProto):
    'switch between AppProto'

    apps: dict[str, AppProto]  # {id: app}
    app: AppProto  # current app

    def __init__(self, screen):
        self.screen = screen

        self.orig_sigint = signal(SIGINT, self.shutdown)
        signal(SIGTERM, self.shutdown)
        signal(SIGWINCH, self.sigwinch_handler)

        self.screen.keypad(1)
        curses.curs_set(0)
        curses.noecho()
        curses.start_color()

    def sigwinch_handler(self, *_):
        self.app.sigwinch_handler()

    def shutdown(self, *_):
        if curses.isendwin():
            # return to curses
            self.screen.refresh()
        sys.exit(0)

    def _handle_alt_key(self):
        ch = get_alt_key(self.screen)
        if ch == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            # In no-delay mode, return -1 if there is no input, otherwise wait until a key is pressed
            return
        self.app.handle_alt_key(ch)

    def getch(self) -> Generator[int, None, None]:
        while True:
            try:
                ch = self.screen.getch()

                if ch == -1:
                    # SIGWINCH interrupt
                    # t = self.screen.getmaxyx()  # doesn't work
                    continue

                if ch == curses.ascii.ESC:  # Esc
                    self._handle_alt_key()
                elif ch == curses.KEY_RESIZE:
                    # doesn't work
                    # t = self.screen.getmaxyx()
                    pass
                else:
                    char = chr(ch)
                    if char.upper() == 'Q':
                        self.shutdown()
                    else:
                        yield ch
            except curses.error:
                pass

    @contextmanager
    def escape2terminal(self):
        def _clear():
            # clear terminal for privacy
            os.system('cls' if os.name == 'nt' else 'clear')

        curses.endwin()
        old = signal(SIGINT, self.orig_sigint)
        try:
            _clear()
            yield
        except KeyboardInterrupt:
            pass
        finally:
            _clear()
            self.screen.refresh()
            signal(SIGINT, old)

    def input_search(self, prompt: str) -> tuple[bool, str]:  # ok, search str
        with self.escape2terminal():
            try:
                return (True, input(prompt))
            except KeyboardInterrupt:
                pass
        return (False, '')

    def run(self):
        self.app.sigwinch_handler()  # create windows, refresh all
        for ch in self.getch():
            key = self.app.handle_key(ch)
            if key in self.apps:
                self.app = self.apps[key]
                self.app.sigwinch_handler()  # create windows, refresh all
