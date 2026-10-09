import curses

from .list3_v2 import List3v2, ListProto3


class List3mProto(ListProto3):
    def record_move_up(self, i: int) -> bool:  # type: ignore[empty-body]
        pass

    def record_move_down(self, i: int) -> bool:  # type: ignore[empty-body]
        pass


class List3m(List3v2):
    'List + move_up(), move_down()'

    def __init__(
        self,
        proto: List3mProto,
        **kwargs,
    ):
        super().__init__(proto, **kwargs)
        self.proto: List3mProto = proto

    def move_up(self, i: int):
        if not self.proto.record_move_up(i):
            return
        if self.idx > 0:
            self.idx -= 1
        if self.cur > 0:
            self.cur -= 1
        self.refresh()

    def move_down(self, i: int):
        if not self.win:
            return
        if not self.proto.record_move_down(i):
            return
        len_ = self.proto.records_len()
        rows, _ = self.win.getmaxyx()
        rows //= self.height
        if self.idx + 1 < len_:
            self.idx += 1
        if self.cur + 1 < rows:
            self.cur += 1
        self.refresh()

    def handle_input(self, ch: int) -> bool:
        if super().handle_input(ch):
            return True
        if ch == curses.KEY_SR:  # Shift-Up
            self.move_up(self.idx)
        elif ch == curses.KEY_SF:  # Shift-Down
            self.move_down(self.idx)
        else:
            return False
        return True
