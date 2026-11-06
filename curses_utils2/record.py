from __future__ import annotations

import io
import os
import subprocess
from collections.abc import Iterable
from enum import IntEnum
from typing import Protocol

from .file_utils import create_memfd2


class Text2Field(IntEnum):
    NONE = 0  # unknown, skip
    SINGLE = 1  # single line
    MULTI = 2  # multiple lines


class RecordProto(Protocol):
    def form_fields(self) -> Iterable[tuple[str, str, str, Text2Field]]:
        'id, title, value, type'

    def set_dict(self, d: dict) -> bool:
        pass

    def as_dict(self) -> dict:
        pass


def text2str(text: str) -> str:
    '\r\n -> \n, \t -> spaces'
    s = ''
    if text:
        s = text.rstrip().replace('\r\n', '\n')
        s = s.replace('\t', ' ' * 4)
    return s


def record2stream(fp, r: RecordProto, comment: str = ''):
    if comment:
        # comment
        for s in comment.splitlines():
            fp.write(f'# {s}\n')
        fp.write('\n')

    first = True
    for _, s, value, _ in r.form_fields():
        if first:
            first = False
        else:
            fp.write('\n')
        fp.write(f'{s}:\n{value}\n')


def record2str(r: RecordProto, comment: str = '') -> str:
    with io.StringIO() as fp:
        record2stream(fp, r, comment=comment)
        return fp.getvalue()


def record2file(fpath: str, r: RecordProto, comment: str = ''):
    with open(fpath, 'w', encoding='utf-8') as fp:
        record2stream(fp, r, comment=comment)


def stream2dict(fp, r: RecordProto) -> dict:
    steps = []
    for id_, title, _, type_ in r.form_fields():
        steps.append((f'{title}:\n', id_, type_))
    d = {}
    step = 0
    read_value = Text2Field.NONE
    for line in fp:
        title, id_, type_ = steps[step]
        if read_value == Text2Field.SINGLE:
            d[id_] = line.rstrip()
            read_value = Text2Field.NONE
            step += 1
            if step >= len(steps):
                break
            continue
        if read_value == Text2Field.MULTI:
            # read lines to the end
            d[id_] += line.rstrip() + '\r\n'
            continue
        if line != title:
            continue
        if id_ not in d:
            d[id_] = ''
        read_value = type_
    return d


def file2dict(fpath: str, r: RecordProto) -> dict:
    with open(fpath, 'r', encoding='utf-8') as fp:
        return stream2dict(fp, r)


def file2record(fpath: str, r: RecordProto) -> bool:
    d = file2dict(fpath, r)
    return r.set_dict(d)


def edit_record(r: RecordProto, comment: str = '') -> bool:
    with create_memfd2('tmp') as (_, fpath):
        record2file(fpath, r, comment=comment)
        t1 = os.path.getmtime(fpath)
        subprocess.run(['vim', fpath], check=False)
        t2 = os.path.getmtime(fpath)
        if t1 != t2:
            return file2record(fpath, r)
    return False
