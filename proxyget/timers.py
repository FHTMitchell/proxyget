# it/timers.py

import time
import dataclasses as _dc
import typing as _t

from collections import OrderedDict as _OrderedDict, Counter as _Counter
from warnings import warn as _warn



def timestamp(unix_time: float = None, show_zone: bool = True) -> str:
    """Show time (current if None) in the format 'yyyy-mm-dd HH:MM:SS [TZ]'"""
    if unix_time is None:
        unix_time = time.time()
    fmt = '%Y-%m-%d %H:%M:%S'
    if show_zone:
        fmt += ' %z'
    return time.strftime(fmt, time.localtime(unix_time))


def time_epsilon_ns() -> _t.Optional[int]:
    x = y = time.time_ns()
    eps_vals: _t.List[_t.Tuple[int, int]] = []
    for _ in range(10):
        count = 0
        x = y = time.time_ns()
        while x == y:
            y = time.time_ns()
            count += 1
        eps_vals.append((y - x, count))

    # filter
    eps_vals = [(val, count) for (val, count) in eps_vals if count > 1]
    if not eps_vals:
        return None
    return int(sum(val for val, _ in eps_vals) / len(eps_vals))


def time_epsilon() -> _t.Optional[float]:
    eps_ns = time_epsilon_ns()
    if eps_ns is None:
        return 0.0
    return eps_ns / 1e9


@_dc.dataclass
class TimeUnit:

    name: str
    symbol: str
    conversion: float
    lower_limit: float
    plural: str = None

    def __post_init__(self):
        if self.plural is None:
            self.plural = self.name + 's'

    @staticmethod
    def _make_fmt(sig: int, pad: int, sep: str, fmt: str):
        valid_seps = {'', '_', ','}
        valid_fmts = set('fFgGeE')
        if sep not in valid_seps:
            raise ValueError(f'{sep!r} not in {valid_seps}')
        if fmt not in valid_fmts:
            raise ValueError(f'{fmt!r} not in {valid_fmts}')
        return f'>{pad}{sep}.{sig}{fmt}'

    def get_name(self, number: float):
        return self.name if number == 1 else self.plural

    def long_form(self, seconds: float, sig: int = 1, pad: int = 0,
                  sep: str = '', fmt: str = 'f') -> str:
        value = seconds / self.conversion
        spec = self._make_fmt(sig, pad, sep, fmt)
        return f'{value:{spec}} {self.get_name(value)}'

    def short_form(self, seconds: float, sig: int = 1, pad: int = 0,
                   sep: str = '', fmt: str = 'f') -> str:
        value = seconds / self.conversion
        spec = self._make_fmt(sig, pad, sep, fmt)
        return f'{value:{spec}} {self.symbol}'


time_units = _OrderedDict({
    'ns': TimeUnit('nanosecond', 'ns', 1e-9, 1e-10),
    'us': TimeUnit('microsecond', 'μs', 1e-6, 1e-7),
    'ms': TimeUnit('millisecond', 'ms', 1e-3, 1e-4),
    's': TimeUnit('second', 's', 1, 0.1),
    'm': TimeUnit('minute', 'min', 60, 120),
    'h': TimeUnit('hour', 'hr', 3600, 120 * 60),
    'd': TimeUnit('day', 'd', 24 * 3600, 48 * 3600),
    'y': TimeUnit('year', 'yr', 365.25 * 24 * 3600, 265 * 24 * 3600)
})


def time_diff_repr(unix_start: float, unix_end: float = 0,
                   unit: str = None, long_form: bool = True,
                   sig: int = 1, pad: int = 0, sep: str = '') -> str:
    """
    Returns a string of the absolute difference between two times given in
    automatic units. The unit selection can be overridden with one of the
    following arguments passed to `unit`:
        e: seconds (scientific notation)
        ns: nanoseconds
        us: microseconds
        ms: milliseconds
        s: seconds
        m: minutes
        h: hours
        d: days
        y: years
    `long_form` should be set to true to get the full name of the unit (e.g.
        'seconds') and false to get the symbol (e.g. s).
    `sig` is the number of digits after the decimal point to display.
    `pad` is the minimum size of the numeric value to be returned padded to
        the right with spaces.
    """

    diff = abs(unix_end - unix_start)

    valid_units = {'e'} | time_units.keys()

    if unit is None:
        for key, value in reversed(time_units.items()):
            if diff >= value.lower_limit:
                unit = key
                break
        else:  # no break -- smaller than ns
            unit = 'e' if diff != 0.0 else 'ns'
    elif unit not in valid_units:
        msg = f'unit {unit!r} not in valid values: {valid_units}'
        raise ValueError(msg)

    kwargs = {
        'sig': sig,
        'pad': pad,
        'sep': sep,
        'fmt': 'f'
    }

    if unit == 'e':
        unit = 's'
        kwargs['fmt'] = 'e'

    if long_form:
        return time_units[unit].long_form(diff, **kwargs)
    else:
        return time_units[unit].short_form(diff, **kwargs)


### Classes ###

class Clock(object):
    time = staticmethod(time.time)  # python really can be beautiful

    @staticmethod
    def ftime(show_zone: bool = True) -> str:
        return timestamp(show_zone=show_zone)

    def __repr__(self):
        return "<{}: time=`{}`>".format(self.__class__.__name__,
                                        self.ftime())


class Stopwatch(Clock):
    """
    A stopwatch, starts counting from first instancing and upon restart().
    Call an instance to find the time in seconds since timer started/restarted.
    Call str to print how much time has past in reasonable units.
    """

    _tic: float

    def __init__(self):
        self._tic = time.time()

    def restart(self):
        self._tic = time.time()

    @property
    def tic(self) -> float:
        return self._tic

    @property
    def toc(self) -> float:
        return time.time() - self._tic  # faster to check _tic than tic

    def __call__(self, unit=None, long_form: bool = True, sig=1, pad=0):
        """
        Depreciated - Saved for legacy reasons.
        """
        msg = "Will no longer be callable. Use __format__ instead."
        _warn(msg, DeprecationWarning)
        return self.ftoc(unit, long_form, sig, pad)

    def ftoc(self, unit: str = None, long_form: bool = True, sig: int = 1,
             pad: int = 0, sep: str = '') -> str:
        """
        Time since (re)start in a given unit to sig significant places.
        If unit is None an appropriate unit is chosen.
        """
        return time_diff_repr(time.time(), self.tic, unit, long_form=long_form,
                              sig=sig, pad=pad, sep=sep)

    def __repr__(self):
        return '<{}: tic=`{}`>'.format(self.__class__.__name__,
                                       timestamp(self.tic))

    def __str__(self):
        return self.ftoc()

    def __format__(self, fmt: str) -> str:
        """
        Format specifier for Stopwatch. Can specify a right pad, precision, long
        form or short form (`#` must be first character for short form)
        and unit (see time_diff_repr). "f" and "g" use default unit.
        """
        clsname = self.__class__.__name__

        if any((c in fmt) for c in '=<^'):
            msg = "{} only supports right aligned pad".format(clsname)
            raise ValueError(msg)

        # works by removing sections from the string as they are examined

        long_form = '#' not in fmt
        fmt = fmt.replace('#', '')


        num_seps = fmt.count('_') + fmt.count(',')
        if num_seps > 1:
            msg = f"fmt {fmt!r} has more than one occurance of '_' or ','"
            raise ValueError(msg)
        elif num_seps == 1:
            sep = ',' if ',' in fmt else '_'
            fmt = fmt.replace('_', '').replace(',', '')
        else:  # num_seps == 0
            sep = ''


        if '>' in fmt:

            index = fmt.index('>')

            if index == 0:
                pass
            elif index == 1:
                if fmt[0] != ' ':
                    msg = "Only valid padding character for {} is ' '"
                    raise ValueError(msg.format(clsname))
            else:
                msg = "Invalid format specifier {!r} for {}".format(fmt, clsname)
                raise ValueError(msg)
            pad = ''

            for char in fmt[index + 1:]:
                if not char.isnumeric():
                    break
                pad += char
            fmt = fmt[index + len(pad) + 1:]
            pad = int(pad) if pad else 0

        else:
            pad = 0


        if '.' in fmt:
            index = fmt.index('.')
            if index != 0:
                msg = "Invalid format specifier {!r} for {}"
                raise ValueError(msg.format(fmt[:index], clsname))
            sig = ''
            for char in fmt[index + 1:]:
                if not char.isnumeric():
                    break
                sig += char
            if not sig:
                raise ValueError(f'Format specifier {fmt!r} missing precision')
            fmt = fmt[index + len(sig) + 1:]
            sig = int(sig)
        else:
            sig = 1

        if len(fmt) > 2:
            msg = "Invalid format specifier {!r} for {}"
            raise ValueError(msg.format(fmt, clsname))

        if fmt in 'fgFG':  # includes ''
            fmt = None
        else:
            fmt = fmt.lower()

        return self.ftoc(unit=fmt, long_form=long_form, sig=sig, pad=pad,
                         sep=sep)


class Timer(Stopwatch):

    checktime: float
    checker: Stopwatch

    def __init__(self, checktime: float = 5):
        super(Timer, self).__init__()
        self.checktime = checktime
        self.checker = Stopwatch()

    def __repr__(self):
        msg = '<{}: tic=`{}`, checktime={}>'
        return msg.format(self.__class__.__name__,
                          timestamp(self.tic),
                          self.checktime)

    def restart(self) -> None:
        self.checker.restart()
        super().restart()

    def check(self) -> bool:
        """Checks if self.checktime has passed since self.check returned True"""
        if self.checker.toc > self.checktime:
            self.checker.restart()
            return True
        return False

    def check2(self, time: float) -> bool:
        """"As check but takes a time (in seconds) argument instead

        Separate function for efficiency
        """
        if self.checker.toc > time:
            self.checker.restart()
            return True
        return False
