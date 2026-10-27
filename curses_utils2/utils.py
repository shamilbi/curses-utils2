import curses
import os
from collections.abc import Callable

from .win import set_terminal_title


def screen_size() -> tuple[int, int]:
    maxx, maxy = os.get_terminal_size()
    return (maxy, maxx)


class RowString:
    '{value1:<width1} {value2:<width2} ...'

    def __init__(self, *widths: int):
        self.widths = widths

    def value(self, *values: str):
        # min_ = min(len(self.widths), len(values))
        s = ''
        for w, v in zip(self.widths, values):
            if not w:
                # last value
                s += v
            else:
                s += f'{v[:w]:<{w}} '
        s = s.rstrip()  # last item stripped
        return s


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
