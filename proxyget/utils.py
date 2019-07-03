#! /usr/bin/env python3
"""
proxyget -- utils.py

author  - fmitchell
created - 2018-Dec-10
"""
import io
import itertools
import dataclasses as dc
import sys
from typing import Mapping, TypeVar, Optional, Iterable, Iterator

from . import timers

V = TypeVar('V')

def dict_get_ignore_case(d: Mapping[str, V], key: str,
                         default: Optional[V] = None) -> Optional[V]:
    """ Return (first) value of mapping `d` where the key matches `key`,
    ignoring case.

    If no such match is found, return default (default: None).
    """

    try:  # try O(1) just in case
        return d[key]
    except KeyError:
        pass

    key_lower = key.lower()
    for k, v in d.items():
        if k.lower() == key_lower:
            return v

    return default


def pairwise(itr: Iterable[V]) -> Iterator[V]:
    a, b = itertools.tee(itr, 2)
    next(b)
    return zip(a, b)


def write_bytes(num, fmt: str = '.2f', bits: bool = False) -> str:

    k = 1024
    d = {
        0: '',
        k: 'k',
        k**2: 'M',
        k**3: 'G',
        k**4: 'T'
    }

    if num < 0:
        raise ValueError(f'{num} is less than 0')

    sym: str
    for key1, key2 in pairwise(d):
        if key1 <= num < key2:
            key = key1
            break
    else:
        # noinspection PyUnboundLocalVariable
        key = key2  # last

    sym = d[key] + 'B' if not bits else 'b'
    return f'{num / key:{fmt}} {sym}'


@dc.dataclass
class ProgressBar:

    update_rate: float = 0.5
    prefix: str = 'Progress'
    suffix: str = 'complete'
    precision: int = 1
    length: int = 80
    progress_char: str = r'█'
    empty_char: str = '_'
    file: io.TextIOWrapper = sys.stdout

    _timer: timers.Timer = dc.field(init=False, repr=False)
    _cycle: Iterator[str] = dc.field(init=False, repr=False)

    def __post_init__(self):

        self._assert_char(self.progress_char)
        self._assert_char(self.empty_char)

        self._cycle = itertools.cycle(r'\|/-')
        self._timer = timers.Timer(self.update_rate)

    @staticmethod
    def _assert_char(s: str) -> None:
        assert isinstance(s, str), repr(s)
        assert len(s) == 1, repr(s)

    def print_init(self) -> None:
        self.print_progress(0)
        self._timer.restart()

    def print_progress(self, fraction: float, total: float = 1) -> None:

        if self._timer.checktime != 0 and not self._timer.check():
            return

        if total != 1:
            fraction /= total
        percent = f'{fraction * 100:.{self.precision}f}%'

        filled_length = int(fraction * self.length)  # truncate towards 0
        left_fill = self.progress_char*filled_length
        right_fill = self.empty_char * (self.length - filled_length - 1)
        load_char = next(self._cycle) if filled_length != self.length else ''

        bar = left_fill + load_char + right_fill

        self.file.write(f'\r{self.prefix} |{bar}| {percent} {self.suffix}\r')
        self.file.flush()

        if fraction == 1:
            self.file.write('\n')
            self.file.flush()
