import curses

from .list1_v2 import ListProto, ListV2


class List1mProto(ListProto):
    def record_move_up(self, i: int) -> bool:  # type: ignore[empty-body]
        pass

    def record_move_down(self, i: int) -> bool:  # type: ignore[empty-body]
        pass


class List1mV2(ListV2):
    'List + move_up(), move_down()'

    def __init__(
        self,
        proto: List1mProto,
        current_color: int = curses.A_BOLD,
    ):
        super().__init__(proto, current_color)
        self.proto: List1mProto = proto

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
        if self.idx < len_ - 1:
            self.idx += 1
        if self.cur < rows - 1:
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
