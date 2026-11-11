import curses
import os
from collections.abc import Callable, Generator

from wcwidth import clip, ljust

from .win import set_terminal_title


def screen_size() -> tuple[int, int]:
    maxx, maxy = os.get_terminal_size()
    return (maxy, maxx)


class RowString:
    '{value1:<width1} {value2:<width2} ...'

    def __init__(self, *widths: int):
        self.widths = widths

    def value(self, *values: str):
        arr: list[str] = []
        for w, v in zip(self.widths, values):
            if not w:
                # last value
                arr.append(v)
            else:
                arr.append(clip(ljust(v, w), end=w - 1))
        s = ' '.join(arr)
        return s.rstrip()  # last item stripped


def chunkstring(s: str, chunk_len: int) -> Generator[str]:
    len_ = len(s)
    i = 0
    while True:
        yield s[i : i + chunk_len]  # works even if s=''
        i += chunk_len
        if not i < len_:
            break


def start_curses_app(
    main: Callable[[curses.window], None],
    app_name: str,
    version: str,
):
    try:
        set_terminal_title(f'{app_name} v{version}')
        curses.wrapper(main)
    finally:
        set_terminal_title('')  # reset terminal title
