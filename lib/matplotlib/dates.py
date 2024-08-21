"""
Date and timedelta locators and formatters.
"""

import datetime
import functools
import logging
import re
import string

from dateutil.rrule import (rrule, MO, TU, WE, TH, FR, SA, SU, YEARLY,
                            MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY,
                            SECONDLY)
from dateutil.relativedelta import relativedelta
import dateutil.parser
import dateutil.tz
import numpy as np

import matplotlib as mpl
from matplotlib import _api, cbook, ticker, units

__all__ = ('datestr2num', 'date2num', 'num2date', 'num2timedelta', 'drange',
           'set_epoch', 'get_epoch', 'DateFormatter', 'ConciseDateFormatter',
           'AutoDateFormatter', 'DateLocator', 'RRuleLocator',
           'AutoDateLocator', 'YearLocator', 'MonthLocator', 'WeekdayLocator',
           'DayLocator', 'HourLocator', 'MinuteLocator',
           'SecondLocator', 'MicrosecondLocator',
           'rrule', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU',
           'YEARLY', 'MONTHLY', 'WEEKLY', 'DAILY',
           'HOURLY', 'MINUTELY', 'SECONDLY', 'MICROSECONDLY', 'relativedelta',
           'DateConverter', 'ConciseDateConverter', 'rrulewrapper')


_log = logging.getLogger(__name__)
UTC = datetime.timezone.utc


def _get_tzinfo(tz=None):
    """
    Generate `~datetime.tzinfo` from a string or return `~datetime.tzinfo`.
    If None, retrieve the preferred timezone from the rcParams dictionary.
    """
    tz = mpl._val_or_rc(tz, 'timezone')
    if tz == 'UTC':
        return UTC
    if isinstance(tz, str):
        tzinfo = dateutil.tz.gettz(tz)
        if tzinfo is None:
            raise ValueError(f"{tz} is not a valid timezone as parsed by"
                             " dateutil.tz.gettz.")
        return tzinfo
    if isinstance(tz, datetime.tzinfo):
        return tz
    raise TypeError(f"tz must be string or tzinfo subclass, not {tz!r}.")


# Time-related constants.
EPOCH_OFFSET = float(datetime.datetime(1970, 1, 1).toordinal())
# EPOCH_OFFSET is not used by matplotlib
MICROSECONDLY = SECONDLY + 1
HOURS_PER_DAY = 24.
MIN_PER_HOUR = 60.
SEC_PER_MIN = 60.
MONTHS_PER_YEAR = 12.

DAYS_PER_WEEK = 7.
DAYS_PER_MONTH = 30.
DAYS_PER_YEAR = 365.0

MINUTES_PER_DAY = MIN_PER_HOUR * HOURS_PER_DAY

SEC_PER_HOUR = SEC_PER_MIN * MIN_PER_HOUR
SEC_PER_DAY = SEC_PER_HOUR * HOURS_PER_DAY
SEC_PER_WEEK = SEC_PER_DAY * DAYS_PER_WEEK

MUSECONDS_PER_DAY = 1e6 * SEC_PER_DAY

MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = (
    MO, TU, WE, TH, FR, SA, SU)
WEEKDAYS = (MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY)

# default epoch: passed to np.datetime64...
_epoch = None


def _reset_epoch_test_example():
    """
    Reset the Matplotlib date epoch so it can be set again.

    Only for use in tests and examples.
    """
    global _epoch
    _epoch = None


def set_epoch(epoch):
    """
    Set the epoch (origin for dates) for datetime calculations.

    The default epoch is :rc:`dates.epoch` (by default 1970-01-01T00:00).

    If microsecond accuracy is desired, the date being plotted needs to be
    within approximately 70 years of the epoch. Matplotlib internally
    represents dates as days since the epoch, so floating point dynamic
    range needs to be within a factor of 2^52.

    `~.dates.set_epoch` must be called before any dates are converted
    (i.e. near the import section) or a RuntimeError will be raised.

    See also :doc:`/gallery/ticks/date_precision_and_epochs`.

    Parameters
    ----------
    epoch : str
        valid UTC date parsable by `numpy.datetime64` (do not include
        timezone).

    """
    global _epoch
    if _epoch is not None:
        raise RuntimeError('set_epoch must be called before dates plotted.')
    _epoch = epoch


def get_epoch():
    """
    Get the epoch used by `matplotlib.dates`.

    Returns
    -------
    epoch : str
        String for the epoch (parsable by `numpy.datetime64`).
    """
    global _epoch

    _epoch = mpl._val_or_rc(_epoch, 'date.epoch')
    return _epoch


def _to_ordinalf(d, *, is_timedelta=False):
    """
    Convert `numpy.datetime64` or an `numpy.ndarray` of those types to
    Gregorian date as UTC float relative to the epoch (see `.get_epoch`).
    Roundoff is float64 precision.  Practically: microseconds for dates
    between 290301 BC, 294241 AD, milliseconds for larger dates
    (see `numpy.datetime64`).
    If `is_timedelta=True`, converts `numpy.timedelta64` or an `numpy.ndarray`
    of those types to float. The converted floating point timedelta values are
    relative to `timedelta(0)`.
    """

    # the "extra" ensures that we at least allow the dynamic range out to
    # seconds.  That should get out to +/-2e11 years.
    if is_timedelta:
        dseconds = d.astype('timedelta64[s]')
        dt = dseconds.astype(np.float64)
    else:
        dseconds = d.astype('datetime64[s]')
        t0 = np.datetime64(get_epoch(), 's')
        dt = (dseconds - t0).astype(np.float64)

    extra = (d - dseconds).astype('timedelta64[ns]')
    dt += extra.astype(np.float64) / 1.0e9
    dt = dt / SEC_PER_DAY

    NaT_int = np.datetime64('NaT').astype(np.int64)
    t_int = d.astype(np.int64)
    dt[t_int == NaT_int] = np.nan

    return dt


def _from_ordinalf(x, tz=None):
    """
    Convert Gregorian float of the date, preserving hours, minutes,
    seconds and microseconds.  Return value is a `.datetime`.

    The input date *x* is a float in ordinal days at UTC, and the output will
    be the specified `.datetime` object corresponding to that time in
    timezone *tz*, or if *tz* is ``None``, in the timezone specified in
    :rc:`timezone`.
    """

    tz = _get_tzinfo(tz)

    dt = (np.datetime64(get_epoch()) +
          np.timedelta64(int(np.round(x * MUSECONDS_PER_DAY)), 'us'))
    if dt < np.datetime64('0001-01-01') or dt >= np.datetime64('10000-01-01'):
        raise ValueError(f'Date ordinal {x} converts to {dt} (using '
                         f'epoch {get_epoch()}), but Matplotlib dates must be '
                          'between year 0001 and 9999.')
    # convert from datetime64 to datetime:
    dt = dt.tolist()

    # datetime64 is always UTC:
    dt = dt.replace(tzinfo=dateutil.tz.gettz('UTC'))
    # but maybe we are working in a different timezone so move.
    dt = dt.astimezone(tz)
    # fix round off errors
    if np.abs(x) > 70 * 365:
        # if x is big, round off to nearest twenty microseconds.
        # This avoids floating point roundoff error
        ms = round(dt.microsecond / 20) * 20
        if ms == 1000000:
            dt = dt.replace(microsecond=0) + datetime.timedelta(seconds=1)
        else:
            dt = dt.replace(microsecond=ms)

    return dt


# a version of _from_ordinalf that can operate on numpy arrays
_from_ordinalf_np_vectorized = np.vectorize(_from_ordinalf, otypes="O")
# a version of dateutil.parser.parse that can operate on numpy arrays
_dateutil_parser_parse_np_vectorized = np.vectorize(dateutil.parser.parse)


def datestr2num(d, default=None):
    """
    Convert a date string to a datenum using `dateutil.parser.parse`.

    Parameters
    ----------
    d : str or sequence of str
        The dates to convert.

    default : datetime.datetime, optional
        The default date to use when fields are missing in *d*.
    """
    if isinstance(d, str):
        dt = dateutil.parser.parse(d, default=default)
        return date2num(dt)
    else:
        if default is not None:
            d = [date2num(dateutil.parser.parse(s, default=default))
                 for s in d]
            return np.asarray(d)
        d = np.asarray(d)
        if not d.size:
            return d
        return date2num(_dateutil_parser_parse_np_vectorized(d))


def date2num(d):
    """
    Convert datetime objects to Matplotlib dates.

    Parameters
    ----------
    d : `datetime.datetime` or `numpy.datetime64` or sequences of these

    Returns
    -------
    float or sequence of floats
        Number of days since the epoch.  See `.get_epoch` for the
        epoch, which can be changed by :rc:`date.epoch` or `.set_epoch`.  If
        the epoch is "1970-01-01T00:00:00" (default) then noon Jan 1 1970
        ("1970-01-01T12:00:00") returns 0.5.

    Notes
    -----
    The Gregorian calendar is assumed; this is not universal practice.
    For details see the module docstring.
    """
    return _timevalue2num(d)


def timedelta2num(t):
    """
    Convert datetime objects to Matplotlib dates.

    Parameters
    ----------
    t : `datetime.timedelta` or `numpy.timedelta64` or sequences of these

    Returns
    -------
    float or sequence of floats
        Number of days. For example, 1 day 12 hours returns 1.5.
    """
    return _timevalue2num(t, is_timedelta=True)


def _timevalue2num(v, *, is_timedelta=False):
    """
    Convert datetime or timedelta to Matplotlibs representation as days
    (since the epoch for datetime) as float.

    Parameters
    ----------
    v: `datetime.datetime`, `numpy.datetime64`, `datetime.timedelta` or
        `numpy.timedelta64` or sequences of these
    is_timedelta: `bool`, indicates that a timedelta object is converted
        instead of a datetime object
    """
    # Unpack in case of e.g. Pandas or xarray object
    v = cbook._unpack_to_numpy(v)

    # make an iterable, but save state to unpack later:
    iterable = np.iterable(v)
    if not iterable:
        v = [v]

    masked = np.ma.is_masked(v)
    mask = np.ma.getmask(v)
    v = np.asarray(v)

    # convert to timedelta64/datetime64 arrays, if not already:
    if is_timedelta and not np.issubdtype(v.dtype, np.timedelta64):
        v = v.astype('timedelta64[us]')
    elif not is_timedelta and not np.issubdtype(v.dtype, np.datetime64):
        # datetime arrays
        if not v.size:
            # deals with an empty array; only required for datetime
            return v
        tzi = getattr(v[0], 'tzinfo', None)
        if tzi is not None:
            # make datetime naive:
            v = [dt.astimezone(UTC).replace(tzinfo=None) for dt in v]
            v = np.asarray(v)
        v = v.astype('datetime64[us]')

    v = np.ma.masked_array(v, mask=mask) if masked else v
    v = _to_ordinalf(v, is_timedelta=is_timedelta)

    return v if iterable else v[0]


def num2date(x, tz=None):
    """
    Convert Matplotlib dates to `~datetime.datetime` objects.

    Parameters
    ----------
    x : float or sequence of floats
        Number of days (fraction part represents hours, minutes, seconds)
        since the epoch.  See `.get_epoch` for the
        epoch, which can be changed by :rc:`date.epoch` or `.set_epoch`.
    tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
        Timezone of *x*. If a string, *tz* is passed to `dateutil.tz`.

    Returns
    -------
    `~datetime.datetime` or sequence of `~datetime.datetime`
        Dates are returned in timezone *tz*.

        If *x* is a sequence, a sequence of `~datetime.datetime` objects will
        be returned.

    Notes
    -----
    The Gregorian calendar is assumed; this is not universal practice.
    For details, see the module docstring.
    """
    tz = _get_tzinfo(tz)
    return _from_ordinalf_np_vectorized(x, tz).tolist()


_ordinalf_to_timedelta_np_vectorized = np.vectorize(
    lambda x: datetime.timedelta(days=x), otypes="O")


def num2timedelta(x):
    """
    Convert number of days to a `~datetime.timedelta` object.

    If *x* is a sequence, a sequence of `~datetime.timedelta` objects will
    be returned.

    Parameters
    ----------
    x : float, sequence of floats
        Number of days. The fraction part represents hours, minutes, seconds.

    Returns
    -------
    `datetime.timedelta` or list[`datetime.timedelta`]
    """
    return _ordinalf_to_timedelta_np_vectorized(x).tolist()


def drange(dstart, dend, delta):
    """
    Return a sequence of equally spaced Matplotlib dates.

    The dates start at *dstart* and reach up to, but not including *dend*.
    They are spaced by *delta*.

    Parameters
    ----------
    dstart, dend : `~datetime.datetime`
        The date limits.
    delta : `datetime.timedelta`
        Spacing of the dates.

    Returns
    -------
    `numpy.array`
        A list floats representing Matplotlib dates.

    """
    f1 = date2num(dstart)
    f2 = date2num(dend)
    step = delta.total_seconds() / SEC_PER_DAY

    # calculate the difference between dend and dstart in times of delta
    num = int(np.ceil((f2 - f1) / step))

    # calculate end of the interval which will be generated
    dinterval_end = dstart + num * delta

    # ensure, that an half open interval will be generated [dstart, dend)
    if dinterval_end >= dend:
        # if the endpoint is greater than or equal to dend,
        # just subtract one delta
        dinterval_end -= delta
        num -= 1

    f2 = date2num(dinterval_end)  # new float-endpoint
    return np.linspace(f1, f2, num + 1)


def _wrap_in_tex(text):
    p = r'([a-zA-Z]+)'
    ret_text = re.sub(p, r'}$\1$\\mathdefault{', text)

    # Braces ensure symbols are not spaced like binary operators.
    ret_text = ret_text.replace('-', '{-}').replace(':', '{:}')
    # To not concatenate space between numbers.
    ret_text = ret_text.replace(' ', r'\;')
    ret_text = '$\\mathdefault{' + ret_text + '}$'
    ret_text = ret_text.replace('$\\mathdefault{}$', '')
    return ret_text


class _TimedeltaFormatTemplate(string.Template):
    # formatting template for datetime-like formatter strings
    delimiter = '%'
    idpattern = r'[>-]?[dHMSf]{1}'

    # add VERBOSE to override default IGNORECASE; VERBOSE is always added
    # anyway by the template class, so this is effectively a None flag here
    flags = re.VERBOSE


def strftimedelta(td, fmt_str):
    """
    Return a string representing a timedelta, controlled by an explicit
    format string.

    The format codes are similar to the Python's datetime format codes from the
    :mod:`datetime` module (which are equivalent to the C standard format
    codes).

    The following is a full list of the format codes that are supported by this
    function.

    +-----------+---------------------------------------+---------------------+
    | Code      | Meaning                               | Example             |
    +-----------+---------------------------------------+---------------------+
    | %d        | Days (1)                              | 0, 1, 2, ...        |
    +-----------+---------------------------------------+---------------------+
    | %H        | Hours as zero-padded decimal number   | 00, 01, ..., 23     |
    +-----------+---------------------------------------+---------------------+
    | %M        | Minutes as zero-padded decimal number | 00, 01, ..., 59     |
    +-----------+---------------------------------------+---------------------+
    | %S        | Seconds as zero-padded decimal number | 00, 01, ..., 59     |
    +-----------+---------------------------------------+---------------------+
    | %-H       | Hours as decimal number (2)           | 0, 1, ..., 23       |
    +-----------+---------------------------------------+---------------------+
    | %-M       | Minutes as decimal number (2)         | 0, 1, ..., 59       |
    +-----------+---------------------------------------+---------------------+
    | %-S       | Seconds as decimal number (2)         | 0, 1, ..., 59       |
    +-----------+---------------------------------------+---------------------+
    | %>H       | Total number of hours including days  | 0, 1, ..., 100, ... |
    |           | (3)                                   |                     |
    +-----------+---------------------------------------+---------------------+
    | %>M       | Total number of minutes including     | 0, 1, ..., 100, ... |
    |           | days and hours (3)                    |                     |
    +-----------+---------------------------------------+---------------------+
    | %>S       | Total number of seconds including     | 0, 1, ..., 100, ... |
    |           | days, hours and minutes (3)           |                     |
    +-----------+---------------------------------------+---------------------+
    | %f        | Microseconds as a decimal number,     | 000000, 000001, ... |
    |           | zero-padded to 6 digits               | 999999              |
    +-----------+---------------------------------------+---------------------+

    - (1): Days are zero-padded to two digits in the C standard. Zero-padding
      is not used here, because there is no maximum number of digits
    - (2): Support for the %-H, %-M, %-S format codes may be platform specific
      in `datetime.datetime.strftime`, but these are always supported in
      `strftimedelta`.
    - (3): %>H, %>M, %>S are extensions to the C standard to support
      representing 3 days as 72 hours, for example.

    Parameters
    ----------
    td : datetime.timedelta
    fmt_str : str
        format string
    """
    s_t = td.total_seconds()
    sign = '-' if s_t < 0 else ''
    s_t = abs(s_t)

    d, s = divmod(s_t, SEC_PER_DAY)
    m_t, s = divmod(s, SEC_PER_MIN)
    h, m = divmod(m_t, MIN_PER_HOUR)
    h_t, _ = divmod(s_t, SEC_PER_HOUR)

    us = td.microseconds

    # define substitution strings; all reasonable equivalents from the c
    # standard implementation for strftime for dates are supported
    # >H, >M, >S are total values and not partially consumed by there next
    # larger units e.g. for timedelta(days=1.5): d=1, h=12, H=36
    values = {'d': int(d),  # days; no zero-padding compared to c std
              '>H': int(h_t),  # total number of h, m, s;
              '>M': int(m_t),  # extension to c standard
              '>S': int(s_t),
              'H': '{:02d}'.format(int(h)),  # zero-padded h, m, s;
              'M': '{:02d}'.format(int(m)),  # equivalent to c std
              'S': '{:02d}'.format(int(s)),
              '-H': int(h),  # h, m, s without zero-padding;
              '-M': int(m),  # platform specific in c std
              '-S': int(s),
              'f': '{:06d}'.format(int(us))}  # microseconds, equiv. c std

    try:
        result = _TimedeltaFormatTemplate(fmt_str).substitute(**values)
    except ValueError as exc:
        # show a more understandable error message
        exc.args = (f"Invalid format string '{fmt_str}' for timedelta", )
        raise exc
    return sign + result


def strftdnum(td_num, fmt_str):
    """
    Return a string representing a matplotlib internal float based timedelta,
    controlled by an explicit format string.

    # TODO: reference table of format codes

    Parameters
    ----------
    td_num : float
        timedelta in matplotlib float representation
    fmt_str : str
        format string
    """
    td = num2timedelta(td_num)
    return strftimedelta(td, fmt_str)


## date tick locators and formatters ###


class TimedeltaFormatter(ticker.Formatter):
    """
    Format a tick with a `strftimedelta` format string.
    """

    def __init__(self, fmt, *, usetex=None):
        """
        Parameters
        ----------
        fmt : str
            `~matplotlib.dates.strftimedelta` format string
        usetex : bool, default: :rc:`text.usetex`
            To enable/disable the use of TeX's math mode for rendering the
            results of the formatter.
        """
        self.fmt = fmt
        self._usetex = mpl._val_or_rc(usetex, 'text.usetex')

    def __call__(self, x, pos=0):
        result = strftdnum(x, self.fmt)
        return _wrap_in_tex(result) if self._usetex else result


class DateFormatter(TimedeltaFormatter):
    """
    Format a tick (in days since the epoch) with a
    `~datetime.datetime.strftime` format string.
    """

    def __init__(self, fmt, tz=None, *, usetex=None):
        """
        Parameters
        ----------
        fmt : str
            `~datetime.datetime.strftime` format string
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        usetex : bool, default: :rc:`text.usetex`
            To enable/disable the use of TeX's math mode for rendering the
            results of the formatter.
        """
        super().__init__(fmt, usetex=usetex)
        self.tz = _get_tzinfo(tz)

    def __call__(self, x, pos=0):
        result = num2date(x, self.tz).strftime(self.fmt)
        return _wrap_in_tex(result) if self._usetex else result

    def set_tzinfo(self, tz):
        self.tz = _get_tzinfo(tz)


class _ConciseTimevalueFormatter(ticker.Formatter):

    def __init__(self, locator, show_offset=True, *, usetex=None):
        self._locator = locator
        self.offset_string = ''
        self.show_offset = show_offset
        self._usetex = mpl._val_or_rc(usetex, 'text.usetex')
        self._zerovals = [None, None, None, None, None, None, None]

        self.formats = list()
        self.zero_formats = list()
        self.offset_formats = list()

    def __call__(self, x, pos=None):
        return NotImplemented

    def _get_formats(self):
        return self.formats, self.zero_formats, self.offset_formats

    def _format_ticks(self, tickvalue, ticktuple):
        # basic algorithm:
        # 1) only display a part of the date if it changes over the ticks.
        # 2) don't display the smaller part of the date if:
        #    it is always the same or if it is the start of the
        #    year, month, day etc.
        fmts, zerofmts, offsetfmts = self._get_formats()
        # fmts: format for most ticks at this level
        # zerofmts: format beginnings of days, months, years, etc.
        # offsetfmts: offset fmt are for the offset in the upper left of the
        #             or lower right of the axis.
        show_offset = self.show_offset

        # determine the level we will label at:
        # mostly 0: years,  1: months,  2: days,
        # 3: hours, 4: minutes, 5: seconds, 6: microseconds
        for level in range(5, -1, -1):
            unique = np.unique(ticktuple[:, level])
            if len(unique) > 1:
                # if 1 is included in unique, the year is shown in ticks
                if level < 2 and np.any(unique == 1):
                    show_offset = False
                break
            elif level == 0:
                # all tickdate are the same, so only micros might be different
                # set to the most precise (6: microseconds doesn't exist...)
                level = 5

        # level is the basic level we will label at.
        # now loop through and decide the actual ticklabels
        labels = [''] * len(ticktuple)
        for nn in range(len(ticktuple)):
            if level < 5:
                if ticktuple[nn][level] == self._zerovals[level]:
                    fmt = zerofmts[level]
                else:
                    fmt = fmts[level]
            else:
                # special handling for seconds + microseconds
                if (isinstance(tickvalue[nn], datetime.timedelta)
                        and (tickvalue[nn].total_seconds() % 60 == 0.0)):
                    fmt = zerofmts[level]
                elif (isinstance(tickvalue[nn], datetime.datetime)
                        and (tickvalue[nn].second
                             == tickvalue[nn].microsecond == 0)):
                    fmt = zerofmts[level]
                else:
                    fmt = fmts[level]
            labels[nn] = self._format_string(tickvalue[nn], fmt)

        # special handling of seconds and microseconds:
        # strip extra zeros and decimal if possible.
        # this is complicated by two factors.  1) we have some level-4 strings
        # here (i.e. 03:00, '0.50000', '1.000') 2) we would like to have the
        # same number of decimals for each string (i.e. 0.5 and 1.0).
        if level >= 5:
            trailing_zeros = min(
                (len(s) - len(s.rstrip('0')) for s in labels if '.' in s),
                default=None)
            if trailing_zeros:
                for nn in range(len(labels)):
                    if '.' in labels[nn]:
                        labels[nn] = labels[nn][:-trailing_zeros].rstrip('.')

        if show_offset:
            # set the offset string:
            self.offset_string = self._format_string(tickvalue[-1],
                                                     offsetfmts[level])
            if self._usetex:
                self.offset_string = _wrap_in_tex(self.offset_string)
        else:
            self.offset_string = ''

        if self._usetex:
            return [_wrap_in_tex(l) for l in labels]
        else:
            return labels

    def get_offset(self):
        return self.offset_string

    def format_data_short(self, value):
        return NotImplemented

    def _format_string(self, value, fmt):
        return NotImplemented


class ConciseDateFormatter(_ConciseTimevalueFormatter):
    """
    A `.Formatter` which attempts to figure out the best format to use for the
    date, and to make it as compact as possible, but still be complete. This is
    most useful when used with the `AutoDateLocator`.

    >>> locator = AutoDateLocator()
    >>> formatter = ConciseDateFormatter(locator)

    Parameters
    ----------
    locator : `.ticker.Locator`
        Locator that this axis is using.

    tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
        Ticks timezone, passed to `.dates.num2date`.

    formats : list of 6 strings, optional
        Format strings for 6 levels of tick labelling: mostly years,
        months, days, hours, minutes, and seconds.  Strings use
        the same format codes as `~datetime.datetime.strftime`.  Default is
        ``['%Y', '%b', '%d', '%H:%M', '%H:%M', '%S.%f']``

    zero_formats : list of 6 strings, optional
        Format strings for tick labels that are "zeros" for a given tick
        level.  For instance, if most ticks are months, ticks around 1 Jan 2005
        will be labeled "Dec", "2005", "Feb".  The default is
        ``['', '%Y', '%b', '%b-%d', '%H:%M', '%H:%M']``

    offset_formats : list of 6 strings, optional
        Format strings for the 6 levels that is applied to the "offset"
        string found on the right side of an x-axis, or top of a y-axis.
        Combined with the tick labels this should completely specify the
        date.  The default is::

            ['', '%Y', '%Y-%b', '%Y-%b-%d', '%Y-%b-%d', '%Y-%b-%d %H:%M']

    show_offset : bool, default: True
        Whether to show the offset or not.

    usetex : bool, default: :rc:`text.usetex`
        To enable/disable the use of TeX's math mode for rendering the results
        of the formatter.

    Examples
    --------
    See :doc:`/gallery/ticks/date_concise_formatter`

    .. plot::

        import datetime
        import matplotlib.dates as mdates

        base = datetime.datetime(2005, 2, 1)
        dates = np.array([base + datetime.timedelta(hours=(2 * i))
                          for i in range(732)])
        N = len(dates)
        np.random.seed(19680801)
        y = np.cumsum(np.random.randn(N))

        fig, ax = plt.subplots(constrained_layout=True)
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        ax.plot(dates, y)
        ax.set_title('Concise Date Formatter')

    """

    def __init__(self, locator, tz=None, formats=None, offset_formats=None,
                 zero_formats=None, show_offset=True, *, usetex=None):
        """
        Autoformat the date labels.  The default format is used to form an
        initial string, and then redundant elements are removed.
        """
        super().__init__(locator, show_offset=show_offset, usetex=usetex)
        self._tz = tz
        # zerovals are values that are zeros for a given tick level, for dates,
        # months and days start at 1, while hours, minutes, ... start at 0
        self._zerovals = [0, 1, 1, 0, 0, 0, 0]
        self.defaultfmt = '%Y'
        # there are 6 levels with each level getting a specific format
        # 0: mostly years,  1: months,  2: days,
        # 3: hours, 4: minutes, 5: seconds
        if formats:
            if len(formats) != 6:
                raise ValueError('formats argument must be a list of '
                                 '6 format strings (or None)')
            self.formats = formats
        else:
            self.formats = ['%Y',  # ticks are mostly years
                            '%b',          # ticks are mostly months
                            '%d',          # ticks are mostly days
                            '%H:%M',       # hrs
                            '%H:%M',       # min
                            '%S.%f',       # secs
                            ]
        # fmt for zeros ticks at this level.  These are
        # ticks that should be labeled w/ info the level above.
        # like 1 Jan can just be labelled "Jan".  02:02:00 can
        # just be labeled 02:02.
        if zero_formats:
            if len(zero_formats) != 6:
                raise ValueError('zero_formats argument must be a list of '
                                 '6 format strings (or None)')
            self.zero_formats = zero_formats
        elif formats:
            # use the users formats for the zero tick formats
            self.zero_formats = [''] + self.formats[:-1]
        else:
            # make the defaults a bit nicer:
            self.zero_formats = [''] + self.formats[:-1]
            self.zero_formats[3] = '%b-%d'

        if offset_formats:
            if len(offset_formats) != 6:
                raise ValueError('offset_formats argument must be a list of '
                                 '6 format strings (or None)')
            self.offset_formats = offset_formats
        else:
            self.offset_formats = ['',
                                   '%Y',
                                   '%Y-%b',
                                   '%Y-%b-%d',
                                   '%Y-%b-%d',
                                   '%Y-%b-%d %H:%M']

    def __call__(self, x, pos=None):
        formatter = DateFormatter(self.defaultfmt, self._tz,
                                  usetex=self._usetex)
        return formatter(x, pos=pos)

    def format_ticks(self, values):
        tickdatetime = [num2date(value, tz=self._tz) for value in values]
        ticktuple = np.array([tdt.timetuple()[:6] for tdt in tickdatetime])
        return super()._format_ticks(tickdatetime, ticktuple)

    def format_data_short(self, value):
        return num2date(value, tz=self._tz).strftime('%Y-%m-%d %H:%M:%S')

    def _format_string(self, value, fmt):
        return value.strftime(fmt)


class ConciseTimedeltaFormatter(_ConciseTimevalueFormatter):
    """
    A `.Formatter` which attempts to figure out the best format to use for the
    timedelta, and to make it as compact as possible, but still be complete.
    This is most useful when used with the `AutoDateLocator`.
    """

    def __init__(self, locator, formats=None, offset_formats=None,
                 zero_formats=None, show_offset=True, *, usetex=None):
        """
        Autoformat the timedelta labels.  The default format is used to form an
        initial string, and then redundant elements are removed.

        Parameters
        ----------
        locator : `.ticker.Locator`
            Locator that this axis is using.

        formats : list of 4 strings, optional
            Format strings for 4 levels of tick labelling: mostly days, hours,
            minutes, and seconds. Strings use the same format codes specified
            described in `strftimedelta`.  Default is
            ``['%d d', '%-H:%M', '%-H:%M' '%-S.%f']``

        zero_formats : list of 4 strings, optional
            Format strings for tick labels that are "zeros" for a given tick
            level.  For instance, if most ticks are hours, ticks around 48:00
            will be labeled "2 d". The default is
            ``['%d d', '%d d', '%-H:%M', '%-H:%M']``

        offset_formats : list of 4 strings, optional
            Format strings for the 4 levels that is applied to the "offset"
            string found on the right side of an x-axis, or top of a y-axis.
            Combined with the tick labels this should completely specify the
            date.  The default is
            ``['', '', '%d days', '%d days %-H:%M']``

        show_offset : bool, default: True
            Whether to show the offset or not.

        usetex : bool, default: :rc:`text.usetex`
            To enable/disable the use of TeX's math mode for rendering the results
            of the formatter.
        """
        super().__init__(locator, show_offset=show_offset, usetex=usetex)
        # zerovals are values that are zeros for a given tick level. For
        # timedelta, this is always 0
        self._zerovals = [0, 0, 0, 0, 0, 0, 0]
        self.defaultfmt = '%d d'
        # there are 6 levels with each level getting a specific format
        # 0: mostly years,  1: months,  2: days,
        # 3: hours, 4: minutes, 5: seconds
        # level 0 and 1 are unsupported for timedelta and skipped here
        if formats:
            if len(formats) != 4:
                raise ValueError('formats argument must be a list of '
                                 '4 format strings (or None)')
            self.formats = formats
        else:
            self.formats = ['%d d',  # days
                            '%-H:%M',   # hours
                            '%-H:%M',   # minutes
                            '%-S.%f',   # secs
                            ]
        # fmt for zeros ticks at this level.  These are
        # ticks that should be labeled w/ info the level above.
        # like 02:02:00 can just be labeled 02:02.
        if zero_formats:
            if len(zero_formats) != 4:
                raise ValueError('zero_formats argument must be a list of '
                                 '4 format strings (or4 None)')
            self.zero_formats = zero_formats
        else:
            # use the users formats for the zero tick formats
            self.zero_formats = ['%d d'] + self.formats[:-1]

        if offset_formats:
            if len(offset_formats) != 4:
                raise ValueError('offset_formats argument must be a list of '
                                 '4 format strings (or None)')
            self.offset_formats = offset_formats
        else:
            self.offset_formats = ['',
                                   '',
                                   '%d days',
                                   '%d days %-H:%M']

    def __call__(self, x, pos=None):
        formatter = TimedeltaFormatter(self.defaultfmt, usetex=self._usetex)
        return formatter(x, pos=pos)

    def _make_timetuple(self, td):
        # returns a tuple similar in structure to datetime.timetuple
        # all values are rounded to integer precision
        s_t = td.total_seconds()
        d, s = divmod(s_t, SEC_PER_DAY)
        m_t, s = divmod(s, SEC_PER_MIN)
        h, m = divmod(m_t, MIN_PER_HOUR)

        # year, month not supported for timedelta, therefore zero
        return 0, 0, d, h, m, s, td.microseconds

    def _get_formats(self):
        # extend list of format strings by two empty (and unused) strings for
        # year and month (necessary for compatibility with base class)
        ret = list()
        for fmts in (self.formats, self.zero_formats, self.offset_formats):
            ret.append(["", "", *fmts])
        return ret

    def format_ticks(self, values):
        ticktimedelta = [num2timedelta(value) for value in values]
        ticktuple = np.array([self._make_timetuple(tdt)
                              for tdt in ticktimedelta])
        return super()._format_ticks(ticktimedelta, ticktuple)

    def format_data_short(self, value):
        return strftimedelta(num2timedelta(value), '%d d %H:%M:%S')

    def _format_string(self, value, fmt):
        return strftimedelta(value, fmt)


class _AutoTimevalueFormatter(ticker.Formatter):
    """
    Base class for `AutoTimedeltaFormatter` and `AutoDateFormatter`.
    This class cannot be used directly. `.scaled` needs to be set and
    `._get_template_formatter` needs to be implemented by the child class.
    """

    # This can be improved by providing some user-level direction on
    # how to choose the best format (precedence, etc.).

    # Perhaps a 'struct' that has a field for each time-type where a
    # zero would indicate "don't show" and a number would indicate
    # "show" with some sort of priority.  Same priorities could mean
    # show all with the same priority.

    # Or more simply, perhaps just a format string for each
    # possibility...

    def __init__(self, locator, defaultfmt='', *, usetex=None):
        self._locator = locator
        self.defaultfmt = defaultfmt
        self._usetex = mpl._val_or_rc(usetex, 'text.usetex')
        self._formatter = self._get_template_formatter(defaultfmt)
        self.scaled = dict()

    def _set_locator(self, locator):
        self._locator = locator

    def _get_template_formatter(self, fmt):
        return NotImplemented

    def __call__(self, x, pos=None):
        try:
            locator_unit_scale = float(self._locator._get_unit())
        except AttributeError:
            locator_unit_scale = 1
        # Pick the first scale which is greater than the locator unit.
        fmt = next((fmt for scale, fmt in sorted(self.scaled.items())
                    if scale >= locator_unit_scale),
                   self.defaultfmt)

        if isinstance(fmt, str):
            self._formatter = self._get_template_formatter(fmt)
            result = self._formatter(x, pos)
        elif callable(fmt):
            result = fmt(x, pos)
        else:
            raise TypeError(f'Unexpected type passed to {self!r}.')

        return result


class AutoTimedeltaFormatter(_AutoTimevalueFormatter):
    """
    A `.Formatter` which attempts to figure out the best format to use by
    choosing a label format that only includes relevant information but is
    still easily readable. This is most useful when used with the
    `AutoTimedeltaLocator`.

    `.AutoTimedeltaFormatter` has a ``.scale`` dictionary that maps tick scales
    (the interval in days between one major tick) to format strings; this
    dictionary defaults to ::

        self.scaled = {
            DAYS_PER_YEAR: rcParams['date.autoformat.year'],
            DAYS_PER_MONTH: rcParams['date.autoformat.month'],
            1: rcParams['date.autoformat.day'],
            1 / HOURS_PER_DAY: rcParams['date.autoformat.hour'],
            1 / MINUTES_PER_DAY: rcParams['date.autoformat.minute'],
            1 / SEC_PER_DAY: rcParams['date.autoformat.second'],
            1 / MUSECONDS_PER_DAY: rcParams['date.autoformat.microsecond'],
        }

    The formatter uses the format string corresponding to the lowest key in
    the dictionary that is greater or equal to the current scale.  Dictionary
    entries can be customized::

        locator = AutoTimedeltaLocator()
        formatter = AutoTimedeltaFormatter(locator)
        formatter.scaled[1/(24*60)] = '%M:%S' # only show min and sec

    Custom callables can also be used instead of format strings.  The following
    example shows how to use a custom format function to strip trailing zeros
    from decimal seconds and adds the date to the first ticklabel::

        def my_format_function(x, pos=None):
            pass  # TODO: add example

        formatter.scaled[1/(24*60)] = my_format_function
    """

    def __init__(self, locator, defaultfmt='%d days %H:%M', *, usetex=None):
        """
        Autoformat the timedelta labels.

        Parameters
        ----------
        locator : `.ticker.Locator`
            Locator that this axis is using.

        defaultfmt : str
            The default format to use if none of the values in ``self.scaled``
            are greater than the unit returned by ``locator._get_unit()``.

        usetex : bool, default: :rc:`text.usetex`
            To enable/disable the use of TeX's math mode for rendering the
            results of the formatter. If any entries in ``self.scaled`` are set
            as functions, then it is up to the customized function to enable or
            disable TeX's math mode itself.
        """
        super().__init__(locator, defaultfmt=defaultfmt, usetex=usetex)
        self.scaled = {
            1: "%d days",
            1 / HOURS_PER_DAY: '%d days, %H:%M',
            1 / MINUTES_PER_DAY: '%d days, %H:%M',
            1 / SEC_PER_DAY: '%d days, %H:%M:%S',
            1e3 / MUSECONDS_PER_DAY: '%d days, %H:%M:%S.%f',
            1 / MUSECONDS_PER_DAY: '%d days, %H:%M:%S.%f',
        }

    def _get_template_formatter(self, fmt):
        return TimedeltaFormatter(fmt, usetex=self._usetex)


class AutoDateFormatter(_AutoTimevalueFormatter):
    """
    A `.Formatter` which attempts to figure out the best format to use by
    choosing a label format that only includes relevant information but is
    still easily readable. This is most useful when used with the
    `AutoDateLocator`.

    `.AutoDateFormatter` has a ``.scale`` dictionary that maps tick scales (the
    interval in days between one major tick) to format strings; this dictionary
    defaults to ::

        self.scaled = {
            DAYS_PER_YEAR: rcParams['date.autoformatter.year'],
            DAYS_PER_MONTH: rcParams['date.autoformatter.month'],
            1: rcParams['date.autoformatter.day'],
            1 / HOURS_PER_DAY: rcParams['date.autoformatter.hour'],
            1 / MINUTES_PER_DAY: rcParams['date.autoformatter.minute'],
            1 / SEC_PER_DAY: rcParams['date.autoformatter.second'],
            1 / MUSECONDS_PER_DAY: rcParams['date.autoformatter.microsecond'],
        }

    The formatter uses the format string corresponding to the lowest key in
    the dictionary that is greater or equal to the current scale.  Dictionary
    entries can be customized::

        locator = AutoDateLocator()
        formatter = AutoDateFormatter(locator)
        formatter.scaled[1/(24*60)] = '%M:%S' # only show min and sec

    Custom callables can also be used instead of format strings.  The following
    example shows how to use a custom format function to strip trailing zeros
    from decimal seconds and adds the date to the first ticklabel::

        def my_format_function(x, pos=None):
            x = matplotlib.dates.num2date(x)
            if pos == 0:
                fmt = '%D %H:%M:%S.%f'
            else:
                fmt = '%H:%M:%S.%f'
            label = x.strftime(fmt)
            label = label.rstrip("0")
            label = label.rstrip(".")
            return label

        formatter.scaled[1/(24*60)] = my_format_function
    """
    def __init__(self, locator, tz=None, defaultfmt='%Y-%m-%d', *,
                 usetex=None):
        """
        Autoformat the date labels.

        Parameters
        ----------
        locator : `.ticker.Locator`
            Locator that this axis is using.

        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.

        defaultfmt : str
            The default format to use if none of the values in ``self.scaled``
            are greater than the unit returned by ``locator._get_unit()``.

        usetex : bool, default: :rc:`text.usetex`
            To enable/disable the use of TeX's math mode for rendering the
            results of the formatter. If any entries in ``self.scaled`` are set
            as functions, then it is up to the customized function to enable or
            disable TeX's math mode itself.
        """
        self._tz = tz
        super().__init__(locator, defaultfmt=defaultfmt, usetex=usetex)
        rcParams = mpl.rcParams
        self.scaled = {
            DAYS_PER_YEAR: rcParams['date.autoformatter.year'],
            DAYS_PER_MONTH: rcParams['date.autoformatter.month'],
            1: rcParams['date.autoformatter.day'],
            1 / HOURS_PER_DAY: rcParams['date.autoformatter.hour'],
            1 / MINUTES_PER_DAY: rcParams['date.autoformatter.minute'],
            1 / SEC_PER_DAY: rcParams['date.autoformatter.second'],
            1 / MUSECONDS_PER_DAY: rcParams['date.autoformatter.microsecond']
        }

    def _get_template_formatter(self, fmt):
        return DateFormatter(fmt, tz=self._tz, usetex=self._usetex)


class rrulewrapper:
    """
    A simple wrapper around a `dateutil.rrule` allowing flexible
    date tick specifications.
    """
    def __init__(self, freq, tzinfo=None, **kwargs):
        """
        Parameters
        ----------
        freq : {YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY}
            Tick frequency. These constants are defined in `dateutil.rrule`,
            but they are accessible from `matplotlib.dates` as well.
        tzinfo : `datetime.tzinfo`, optional
            Time zone information. The default is None.
        **kwargs
            Additional keyword arguments are passed to the `dateutil.rrule`.
        """
        kwargs['freq'] = freq
        self._base_tzinfo = tzinfo

        self._update_rrule(**kwargs)

    def set(self, **kwargs):
        """Set parameters for an existing wrapper."""
        self._construct.update(kwargs)

        self._update_rrule(**self._construct)

    def _update_rrule(self, **kwargs):
        tzinfo = self._base_tzinfo

        # rrule does not play nicely with timezones - especially pytz time
        # zones, it's best to use naive zones and attach timezones once the
        # datetimes are returned
        if 'dtstart' in kwargs:
            dtstart = kwargs['dtstart']
            if dtstart.tzinfo is not None:
                if tzinfo is None:
                    tzinfo = dtstart.tzinfo
                else:
                    dtstart = dtstart.astimezone(tzinfo)

                kwargs['dtstart'] = dtstart.replace(tzinfo=None)

        if 'until' in kwargs:
            until = kwargs['until']
            if until.tzinfo is not None:
                if tzinfo is not None:
                    until = until.astimezone(tzinfo)
                else:
                    raise ValueError('until cannot be aware if dtstart '
                                     'is naive and tzinfo is None')

                kwargs['until'] = until.replace(tzinfo=None)

        self._construct = kwargs.copy()
        self._tzinfo = tzinfo
        self._rrule = rrule(**self._construct)

    def _attach_tzinfo(self, dt, tzinfo):
        # pytz zones are attached by "localizing" the datetime
        if hasattr(tzinfo, 'localize'):
            return tzinfo.localize(dt, is_dst=True)

        return dt.replace(tzinfo=tzinfo)

    def _aware_return_wrapper(self, f, returns_list=False):
        """Decorator function that allows rrule methods to handle tzinfo."""
        # This is only necessary if we're actually attaching a tzinfo
        if self._tzinfo is None:
            return f

        # All datetime arguments must be naive. If they are not naive, they are
        # converted to the _tzinfo zone before dropping the zone.
        def normalize_arg(arg):
            if isinstance(arg, datetime.datetime) and arg.tzinfo is not None:
                if arg.tzinfo is not self._tzinfo:
                    arg = arg.astimezone(self._tzinfo)

                return arg.replace(tzinfo=None)

            return arg

        def normalize_args(args, kwargs):
            args = tuple(normalize_arg(arg) for arg in args)
            kwargs = {kw: normalize_arg(arg) for kw, arg in kwargs.items()}

            return args, kwargs

        # There are two kinds of functions we care about - ones that return
        # dates and ones that return lists of dates.
        if not returns_list:
            def inner_func(*args, **kwargs):
                args, kwargs = normalize_args(args, kwargs)
                dt = f(*args, **kwargs)
                return self._attach_tzinfo(dt, self._tzinfo)
        else:
            def inner_func(*args, **kwargs):
                args, kwargs = normalize_args(args, kwargs)
                dts = f(*args, **kwargs)
                return [self._attach_tzinfo(dt, self._tzinfo) for dt in dts]

        return functools.wraps(f)(inner_func)

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        f = getattr(self._rrule, name)

        if name in {'after', 'before'}:
            return self._aware_return_wrapper(f)
        elif name in {'xafter', 'xbefore', 'between'}:
            return self._aware_return_wrapper(f, returns_list=True)
        else:
            return f

    def __setstate__(self, state):
        self.__dict__.update(state)


class DateLocator(ticker.Locator):
    """
    Base class for date tick locators that determine the tick locations
    when plotting dates.

    This class is subclassed by other Locators and
    is not meant to be used on its own.
    """
    hms0d = {'byhour': 0, 'byminute': 0, 'bysecond': 0}

    def __init__(self, tz=None):
        """
        Parameters
        ----------
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        """
        self.tz = _get_tzinfo(tz)

    @property
    def default_range(self):
        """The default min and max limits of the axis."""
        # property because date2num needs to be computed each time in
        # case the epoch is changed
        return (date2num(datetime.date(1970, 1, 1)),
                date2num(datetime.date(1970, 1, 2)))

    def set_tzinfo(self, tz):
        """
        Set timezone info.

        Parameters
        ----------
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        """
        self.tz = _get_tzinfo(tz)

    def datalim_to_dt(self):
        """Convert axis data interval to datetime objects."""
        dmin, dmax = self.axis.get_data_interval()
        if dmin > dmax:
            dmin, dmax = dmax, dmin

        return num2date(dmin, self.tz), num2date(dmax, self.tz)

    def viewlim_to_dt(self):
        """Convert the view interval to datetime objects."""
        vmin, vmax = self.axis.get_view_interval()
        if vmin > vmax:
            vmin, vmax = vmax, vmin
        return num2date(vmin, self.tz), num2date(vmax, self.tz)

    def _get_unit(self):
        """
        Return how many days a unit of the locator is; used for
        intelligent autoscaling.
        """
        return 1

    def _get_interval(self):
        """
        Return the number of units for each tick.
        """
        return 1

    def nonsingular(self, vmin, vmax):
        """
        Given the proposed upper and lower extent, adjust the range
        if it is too close to being singular (i.e. a range of ~0).
        """
        if not np.isfinite(vmin) or not np.isfinite(vmax):
            # Except if there is no data, then use default range
            return self.default_range
        if vmax < vmin:
            vmin, vmax = vmax, vmin
        unit = self._get_unit()
        interval = self._get_interval()
        if abs(vmax - vmin) < 1e-6:
            vmin -= 2 * unit * interval
            vmax += 2 * unit * interval
        return vmin, vmax


class RRuleLocator(DateLocator):
    """
    Make ticks using `rrulewrapper` which allows almost arbitrary date tick
    specifications, see :doc:`rrule example </gallery/ticks/date_demo_rrule>`.
    """
    # use the dateutil rrule instance

    def __init__(self, o, tz=None):
        super().__init__(tz)
        self.rule = o

    def __call__(self):
        # if no data have been set, this will tank with a ValueError
        try:
            dmin, dmax = self.viewlim_to_dt()
        except ValueError:
            return []

        return self.tick_values(dmin, dmax)

    def tick_values(self, vmin, vmax):
        start, stop = self._create_rrule(vmin, vmax)
        dates = self.rule.between(start, stop, True)
        if len(dates) == 0:
            return date2num([vmin, vmax])
        return self.raise_if_exceeds(date2num(dates))

    def _create_rrule(self, vmin, vmax):
        # set appropriate rrule dtstart and until and return
        # start and end
        delta = relativedelta(vmax, vmin)

        # We need to cap at the endpoints of valid datetime
        try:
            start = vmin - delta
        except (ValueError, OverflowError):
            # cap
            start = datetime.datetime(1, 1, 1, 0, 0, 0,
                                      tzinfo=datetime.timezone.utc)

        try:
            stop = vmax + delta
        except (ValueError, OverflowError):
            # cap
            stop = datetime.datetime(9999, 12, 31, 23, 59, 59,
                                     tzinfo=datetime.timezone.utc)

        self.rule.set(dtstart=start, until=stop)

        return vmin, vmax

    def _get_unit(self):
        # docstring inherited
        freq = self.rule._rrule._freq
        return self.get_unit_generic(freq)

    @staticmethod
    def get_unit_generic(freq):
        if freq == YEARLY:
            return DAYS_PER_YEAR
        elif freq == MONTHLY:
            return DAYS_PER_MONTH
        elif freq == WEEKLY:
            return DAYS_PER_WEEK
        elif freq == DAILY:
            return 1.0
        elif freq == HOURLY:
            return 1.0 / HOURS_PER_DAY
        elif freq == MINUTELY:
            return 1.0 / MINUTES_PER_DAY
        elif freq == SECONDLY:
            return 1.0 / SEC_PER_DAY
        else:
            # error
            return -1  # or should this just return '1'?

    def _get_interval(self):
        return self.rule._rrule._interval


class AutoDateLocator(DateLocator):
    """
    On autoscale, this class picks the best `DateLocator` to set the view
    limits and the tick locations.

    Attributes
    ----------
    intervald : dict

        Mapping of tick frequencies to multiples allowed for that ticking.
        The default is ::

            self.intervald = {
                YEARLY  : [1, 2, 4, 5, 10, 20, 40, 50, 100, 200, 400, 500,
                           1000, 2000, 4000, 5000, 10000],
                MONTHLY : [1, 2, 3, 4, 6],
                DAILY   : [1, 2, 3, 7, 14, 21],
                HOURLY  : [1, 2, 3, 4, 6, 12],
                MINUTELY: [1, 5, 10, 15, 30],
                SECONDLY: [1, 5, 10, 15, 30],
                MICROSECONDLY: [1, 2, 5, 10, 20, 50, 100, 200, 500,
                                1000, 2000, 5000, 10000, 20000, 50000,
                                100000, 200000, 500000, 1000000],
            }

        where the keys are defined in `dateutil.rrule`.

        The interval is used to specify multiples that are appropriate for
        the frequency of ticking. For instance, every 7 days is sensible
        for daily ticks, but for minutes/seconds, 15 or 30 make sense.

        When customizing, you should only modify the values for the existing
        keys. You should not add or delete entries.

        Example for forcing ticks every 3 hours::

            locator = AutoDateLocator()
            locator.intervald[HOURLY] = [3]  # only show every 3 hours
    """

    def __init__(self, tz=None, minticks=5, maxticks=None,
                 interval_multiples=True):
        """
        Parameters
        ----------
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        minticks : int
            The minimum number of ticks desired; controls whether ticks occur
            yearly, monthly, etc.
        maxticks : int
            The maximum number of ticks desired; controls the interval between
            ticks (ticking every other, every 3, etc.).  For fine-grained
            control, this can be a dictionary mapping individual rrule
            frequency constants (YEARLY, MONTHLY, etc.) to their own maximum
            number of ticks.  This can be used to keep the number of ticks
            appropriate to the format chosen in `AutoDateFormatter`. Any
            frequency not specified in this dictionary is given a default
            value.
        interval_multiples : bool, default: True
            Whether ticks should be chosen to be multiple of the interval,
            locking them to 'nicer' locations.  For example, this will force
            the ticks to be at hours 0, 6, 12, 18 when hourly ticking is done
            at 6 hour intervals.
        """
        super().__init__(tz=tz)
        self._freq = YEARLY
        self._freqs = [YEARLY, MONTHLY, DAILY, HOURLY, MINUTELY,
                       SECONDLY, MICROSECONDLY]
        self.minticks = minticks

        self.maxticks = {YEARLY: 11, MONTHLY: 12, DAILY: 11, HOURLY: 12,
                         MINUTELY: 11, SECONDLY: 11, MICROSECONDLY: 8}
        if maxticks is not None:
            try:
                self.maxticks.update(maxticks)
            except TypeError:
                # Assume we were given an integer. Use this as the maximum
                # number of ticks for every frequency and create a
                # dictionary for this
                self.maxticks = dict.fromkeys(self._freqs, maxticks)
        self.interval_multiples = interval_multiples
        self.intervald = {
            YEARLY:   [1, 2, 4, 5, 10, 20, 40, 50, 100, 200, 400, 500,
                       1000, 2000, 4000, 5000, 10000],
            MONTHLY:  [1, 2, 3, 4, 6],
            DAILY:    [1, 2, 3, 7, 14, 21],
            HOURLY:   [1, 2, 3, 4, 6, 12],
            MINUTELY: [1, 5, 10, 15, 30],
            SECONDLY: [1, 5, 10, 15, 30],
            MICROSECONDLY: [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000,
                            5000, 10000, 20000, 50000, 100000, 200000, 500000,
                            1000000],
                            }
        if interval_multiples:
            # Swap "3" for "4" in the DAILY list; If we use 3 we get bad
            # tick loc for months w/ 31 days: 1, 4, ..., 28, 31, 1
            # If we use 4 then we get: 1, 5, ... 25, 29, 1
            self.intervald[DAILY] = [1, 2, 4, 7, 14]

        self._byranges = [None, range(1, 13), range(1, 32),
                          range(0, 24), range(0, 60), range(0, 60), None]

    def __call__(self):
        # docstring inherited
        dmin, dmax = self.viewlim_to_dt()
        locator = self.get_locator(dmin, dmax)
        return locator()

    def tick_values(self, vmin, vmax):
        return self.get_locator(vmin, vmax).tick_values(vmin, vmax)

    def nonsingular(self, vmin, vmax):
        # whatever is thrown at us, we can scale the unit.
        # But default nonsingular date plots at an ~4 year period.
        if not np.isfinite(vmin) or not np.isfinite(vmax):
            # Except if there is no data, then use default range
            return self.default_range
        if vmax < vmin:
            vmin, vmax = vmax, vmin
        if vmin == vmax:
            vmin = vmin - DAYS_PER_YEAR * 2
            vmax = vmax + DAYS_PER_YEAR * 2
        return vmin, vmax

    def _get_unit(self):
        if self._freq in [MICROSECONDLY]:
            return 1. / MUSECONDS_PER_DAY
        else:
            return RRuleLocator.get_unit_generic(self._freq)

    def get_locator(self, dmin, dmax):
        """Pick the best locator based on a distance."""
        delta = relativedelta(dmax, dmin)
        tdelta = dmax - dmin

        # take absolute difference
        if dmin > dmax:
            delta = -delta
            tdelta = -tdelta
        # The following uses a mix of calls to relativedelta and timedelta
        # methods because there is incomplete overlap in the functionality of
        # these similar functions, and it's best to avoid doing our own math
        # whenever possible.
        numYears = float(delta.years)
        numMonths = numYears * MONTHS_PER_YEAR + delta.months
        numDays = tdelta.days  # Avoids estimates of days/month, days/year.
        numHours = numDays * HOURS_PER_DAY + delta.hours
        numMinutes = numHours * MIN_PER_HOUR + delta.minutes
        numSeconds = np.floor(tdelta.total_seconds())
        numMicroseconds = np.floor(tdelta.total_seconds() * 1e6)

        nums = [numYears, numMonths, numDays, numHours, numMinutes,
                numSeconds, numMicroseconds]

        use_rrule_locator = [True] * 6 + [False]

        # Default setting of bymonth, etc. to pass to rrule
        # [unused (for year), bymonth, bymonthday, byhour, byminute,
        #  bysecond, unused (for microseconds)]
        byranges = [None, 1, 1, 0, 0, 0, None]

        # Loop over all the frequencies and try to find one that gives at
        # least a minticks tick positions.  Once this is found, look for
        # an interval from a list specific to that frequency that gives no
        # more than maxticks tick positions. Also, set up some ranges
        # (bymonth, etc.) as appropriate to be passed to rrulewrapper.
        for i, (freq, num) in enumerate(zip(self._freqs, nums)):
            # If this particular frequency doesn't give enough ticks, continue
            if num < self.minticks:
                # Since we're not using this particular frequency, set
                # the corresponding by_ to None so the rrule can act as
                # appropriate
                byranges[i] = None
                continue

            # Find the first available interval that doesn't give too many
            # ticks
            for interval in self.intervald[freq]:
                if num <= interval * (self.maxticks[freq] - 1):
                    break
            else:
                if not (self.interval_multiples and freq == DAILY):
                    _api.warn_external(
                        f"AutoDateLocator was unable to pick an appropriate "
                        f"interval for this date range. It may be necessary "
                        f"to add an interval value to the AutoDateLocator's "
                        f"intervald dictionary. Defaulting to {interval}.")

            # Set some parameters as appropriate
            self._freq = freq

            if self._byranges[i] and self.interval_multiples:
                byranges[i] = self._byranges[i][::interval]
                if i in (DAILY, WEEKLY):
                    if interval == 14:
                        # just make first and 15th.  Avoids 30th.
                        byranges[i] = [1, 15]
                    elif interval == 7:
                        byranges[i] = [1, 8, 15, 22]

                interval = 1
            else:
                byranges[i] = self._byranges[i]
            break
        else:
            interval = 1

        if (freq == YEARLY) and self.interval_multiples:
            locator = YearLocator(interval, tz=self.tz)
        elif use_rrule_locator[i]:
            _, bymonth, bymonthday, byhour, byminute, bysecond, _ = byranges
            rrule = rrulewrapper(self._freq, interval=interval,
                                 dtstart=dmin, until=dmax,
                                 bymonth=bymonth, bymonthday=bymonthday,
                                 byhour=byhour, byminute=byminute,
                                 bysecond=bysecond)

            locator = RRuleLocator(rrule, tz=self.tz)
        else:
            locator = MicrosecondLocator(interval, tz=self.tz)
            if date2num(dmin) > 70 * 365 and interval < 1000:
                _api.warn_external(
                    'Plotting microsecond time intervals for dates far from '
                    f'the epoch (time origin: {get_epoch()}) is not well-'
                    'supported. See matplotlib.dates.set_epoch to change the '
                    'epoch.')

        locator.set_axis(self.axis)
        return locator


class YearLocator(RRuleLocator):
    """
    Make ticks on a given day of each year in regular intervals of one or
    multiple years.

    Examples::

      # Tick every year on Jan 1st
      locator = YearLocator()

      # Tick every 5 years on July 4th
      locator = YearLocator(5, month=7, day=4)
    """
    def __init__(self, base=1, month=1, day=1, tz=None):
        """
        Parameters
        ----------
        base : int, default: 1
            Mark ticks every *base* years.
        month : int, default: 1
            The month on which to place the ticks, starting from 1. Default is
            January.
        day : int, default: 1
            The day on which to place the ticks.
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        """
        rule = rrulewrapper(YEARLY, interval=base, bymonth=month,
                            bymonthday=day, **self.hms0d)
        super().__init__(rule, tz=tz)
        self.base = ticker._Edge_integer(base, 0)

    def _create_rrule(self, vmin, vmax):
        # 'start' needs to be a multiple of the interval to create ticks on
        # interval multiples when the tick frequency is YEARLY
        ymin = max(self.base.le(vmin.year) * self.base.step, 1)
        ymax = min(self.base.ge(vmax.year) * self.base.step, 9999)

        c = self.rule._construct
        replace = {'year': ymin,
                   'month': c.get('bymonth', 1),
                   'day': c.get('bymonthday', 1),
                   'hour': 0, 'minute': 0, 'second': 0}

        start = vmin.replace(**replace)
        stop = start.replace(year=ymax)
        self.rule.set(dtstart=start, until=stop)

        return start, stop


class MonthLocator(RRuleLocator):
    """
    Make ticks on occurrences of specific months, for example, 1, 3, 12.
    """
    def __init__(self, bymonth=None, bymonthday=1, interval=1, tz=None):
        """
        Parameters
        ----------
        bymonth : int or list of int, default: all months
            Ticks will be placed on every month in *bymonth*. Default is
            ``range(1, 13)``, i.e. every month.
        bymonthday : int, default: 1
            The day on which to place the ticks.
        interval : int, default: 1
            The interval between each iteration. For example, if
            ``interval=2``, mark every second occurrence.
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        """
        if bymonth is None:
            bymonth = range(1, 13)

        rule = rrulewrapper(MONTHLY, bymonth=bymonth, bymonthday=bymonthday,
                            interval=interval, **self.hms0d)
        super().__init__(rule, tz=tz)


class WeekdayLocator(RRuleLocator):
    """
    Make ticks on occurrences of specific weekdays, for example, *MO*, *MI*,
    *FR*.
    """

    def __init__(self, byweekday=1, interval=1, tz=None):
        """
        Parameters
        ----------
        byweekday : int or list of int, default: all days
            Ticks will be placed on every weekday in *byweekday*. Default is
            every day.

            Elements of *byweekday* must be one of MO, TU, WE, TH, FR, SA,
            SU, the constants from :mod:`dateutil.rrule`, which have been
            imported into the :mod:`matplotlib.dates` namespace.
        interval : int, default: 1
            The interval between each iteration. For example, if
            ``interval=2``, mark every second occurrence.
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        """
        rule = rrulewrapper(DAILY, byweekday=byweekday,
                            interval=interval, **self.hms0d)
        super().__init__(rule, tz=tz)


class DayLocator(RRuleLocator):
    """
    Make ticks on occurrences of specific days of the month, for example,
    1, 15, 30.
    """
    def __init__(self, bymonthday=None, interval=1, tz=None):
        """
        Parameters
        ----------
        bymonthday : int or list of int, default: all days
            Ticks will be placed on every day in *bymonthday*. Default is
            ``bymonthday=range(1, 32)``, i.e., every day of the month.
        interval : int, default: 1
            The interval between each iteration. For example, if
            ``interval=2``, mark every second occurrence.
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        """
        if interval != int(interval) or interval < 1:
            raise ValueError("interval must be an integer greater than 0")
        if bymonthday is None:
            bymonthday = range(1, 32)

        rule = rrulewrapper(DAILY, bymonthday=bymonthday,
                            interval=interval, **self.hms0d)
        super().__init__(rule, tz=tz)


class HourLocator(RRuleLocator):
    """
    Make ticks on occurrences of specific hours, for example, 0, 6, 12, 18.
    """
    def __init__(self, byhour=None, interval=1, tz=None):
        """
        Parameters
        ----------
        byhour : int or list of int, default: all hours
            Ticks will be placed on every hour in *byhour*. Default is
            ``byhour=range(24)``, i.e., every hour.
        interval : int, default: 1
            The interval between each iteration. For example, if
            ``interval=2``, mark every second occurrence.
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        """
        if byhour is None:
            byhour = range(24)

        rule = rrulewrapper(HOURLY, byhour=byhour, interval=interval,
                            byminute=0, bysecond=0)
        super().__init__(rule, tz=tz)


class MinuteLocator(RRuleLocator):
    """
    Make ticks on occurrences of specific minutes, for example, 0, 15, 30, 45.
    """
    def __init__(self, byminute=None, interval=1, tz=None):
        """
        Parameters
        ----------
        byminute : int or list of int, default: all minutes
            Ticks will be placed on every minute in *byminute*. Default is
            ``byminute=range(60)``, i.e., every minute.
        interval : int, default: 1
            The interval between each iteration. For example, if
            ``interval=2``, mark every second occurrence.
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        """
        if byminute is None:
            byminute = range(60)

        rule = rrulewrapper(MINUTELY, byminute=byminute, interval=interval,
                            bysecond=0)
        super().__init__(rule, tz=tz)


class SecondLocator(RRuleLocator):
    """
    Make ticks on occurrences of specific seconds, for example, 0, 15, 30, 45.
    """
    def __init__(self, bysecond=None, interval=1, tz=None):
        """
        Parameters
        ----------
        bysecond : int or list of int, default: all seconds
            Ticks will be placed on every second in *bysecond*. Default is
            ``bysecond = range(60)``, i.e., every second.
        interval : int, default: 1
            The interval between each iteration. For example, if
            ``interval=2``, mark every second occurrence.
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        """
        if bysecond is None:
            bysecond = range(60)

        rule = rrulewrapper(SECONDLY, bysecond=bysecond, interval=interval)
        super().__init__(rule, tz=tz)


class MicrosecondLocator(DateLocator):
    """
    Make ticks on regular intervals of one or more microsecond(s).

    .. note::

        By default, Matplotlib uses a floating point representation of time in
        days since the epoch, so plotting data with
        microsecond time resolution does not work well for
        dates that are far (about 70 years) from the epoch (check with
        `~.dates.get_epoch`).

        If you want sub-microsecond resolution time plots, it is strongly
        recommended to use floating point seconds, not datetime-like
        time representation.

        If you really must use datetime.datetime() or similar and still
        need microsecond precision, change the time origin via
        `.dates.set_epoch` to something closer to the dates being plotted.
        See :doc:`/gallery/ticks/date_precision_and_epochs`.

    """
    def __init__(self, interval=1, tz=None):
        """
        Parameters
        ----------
        interval : int, default: 1
            The interval between each iteration. For example, if
            ``interval=2``, mark every second occurrence.
        tz : str or `~datetime.tzinfo`, default: :rc:`timezone`
            Ticks timezone. If a string, *tz* is passed to `dateutil.tz`.
        """
        super().__init__(tz=tz)
        self._interval = interval
        self._wrapped_locator = ticker.MultipleLocator(interval)

    def set_axis(self, axis):
        self._wrapped_locator.set_axis(axis)
        return super().set_axis(axis)

    def __call__(self):
        # if no data have been set, this will tank with a ValueError
        try:
            dmin, dmax = self.viewlim_to_dt()
        except ValueError:
            return []

        return self.tick_values(dmin, dmax)

    def tick_values(self, vmin, vmax):
        nmin, nmax = date2num((vmin, vmax))
        t0 = np.floor(nmin)
        nmax = nmax - t0
        nmin = nmin - t0
        nmin *= MUSECONDS_PER_DAY
        nmax *= MUSECONDS_PER_DAY

        ticks = self._wrapped_locator.tick_values(nmin, nmax)

        ticks = ticks / MUSECONDS_PER_DAY + t0
        return ticks

    def _get_unit(self):
        # docstring inherited
        return 1. / MUSECONDS_PER_DAY

    def _get_interval(self):
        # docstring inherited
        return self._interval


class TimedeltaLocator(ticker.MultipleLocator):
    """
    Make ticks in regular timedelta intervals, for example every 15 minutes.

    Examples::

        # Ticks every day
        locator = TimedeltaLocator()

        # Ticks every 4 hours
        locator = TimedeltaLocator(HOURLY, 4)
    """
    default_range = (timedelta2num(datetime.timedelta(days=0)),
                     timedelta2num(datetime.timedelta(days=1)))
    """The default min and max limits of the axis."""

    _FACTORS = {
        WEEKLY: 7.0,
        DAILY: 1.0,
        HOURLY: 1.0 / HOURS_PER_DAY,
        MINUTELY: 1.0 / MINUTES_PER_DAY,
        SECONDLY: 1.0 / SEC_PER_DAY,
        MICROSECONDLY: 1.0 / MUSECONDS_PER_DAY
    }

    def __init__(self, freq=DAILY, interval=1):
        """
        Create ticks with a specific frequency and interval.

        Parameters
        ----------
        freq: one of `WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY, MICROSECONDLY`
            The base frequency for creating ticks
        interval: int
            The interval (integer multiple of frequency) for creating ticks
        """
        self._freq = freq
        self._interval = interval
        base = 1 * self._FACTORS[self._freq] * self._interval
        super().__init__(base=base)

    # TODO: signature does not match base method, imo that is ok here?
    def set_params(self, freq, interval):
        # docstring inherited
        if freq is not None:
            self._freq = freq
        if interval is not None:
            self._interval = interval
        base = self._FACTORS[self._freq] * self._interval
        super().set_params(base=base)

    def _get_unit(self):
        return self._FACTORS[self._freq]

    def nonsingular(self, vmin, vmax):
        """
        Given the proposed upper and lower extent, adjust the range
        if it is too close to being singular (i.e. a range of ~0).
        """
        if not np.isfinite(vmin) or not np.isfinite(vmax):
            # Except if there is no data, then use 0 - 10 days as default
            return self.default_range
        if vmax < vmin:
            vmin, vmax = vmax, vmin
        unit = self._FACTORS[self._freq]
        if abs(vmax - vmin) < 1e-6:
            vmin -= 2 * unit * self._interval
            vmax += 2 * unit * self._interval
        return vmin, vmax


class AutoTimedeltaLocator(TimedeltaLocator):
    """
    On autoscale, this class picks the best frequency and interval for
    `TimedeltaLocator` to set the view limits and the tick locations.

    Attributes
    ----------
    intervald : dict

        Mapping of tick frequencies to multiples allowed for that ticking.
        The default is ::

            self.intervald = {
                DAILY: [1, 2, 3, 7, 14, 21],
                HOURLY: [1, 2, 3, 4, 6, 12],
                MINUTELY: [1, 5, 10, 15, 30],
                SECONDLY: [1, 5, 10, 15, 30],
                MICROSECONDLY: [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000,
                                2000, 5000, 10000, 20000, 50000, 100000,
                                200000, 500000, 1000000]
            }


        where the keys are defined in `dateutil.rrule`.

        The interval is used to specify multiples that are appropriate for
        the frequency of ticking. For instance, every 7 days is sensible
        for daily ticks, but for minutes/seconds, 15 or 30 make sense.

        When customizing, you should only modify the values for the existing
        keys. You should not add or delete entries.

        Example for forcing ticks every 3 hours::

            locator = AutoTimedeltaLocator()
            locator.intervald[HOURLY] = [3]  # only show every 3 hours
    """
    def __init__(self, minticks=5, maxticks=None):
        """
        Parameters
        ----------
        minticks : int
            The minimum number of ticks desired; controls whether ticks occur
            yearly, monthly, etc.
        maxticks : int
            The maximum number of ticks desired; controls the interval between
            ticks (ticking every other, every 3, etc.).  For fine-grained
            control, this can be a dictionary mapping individual rrule
            frequency constants (DAILY, HOURLY, etc.) to their own maximum
            number of ticks.  This can be used to keep the number of ticks
            appropriate to the format chosen in `AutoTimedeltaFormatter`. Any
            frequency not specified in this dictionary is given a default
            value.
        """
        super().__init__()
        self._freqs = [DAILY, HOURLY, MINUTELY, SECONDLY, MICROSECONDLY]
        self.minticks = minticks
        self.maxticks = {DAILY: 11, HOURLY: 12, MINUTELY: 11, SECONDLY: 11,
                         MICROSECONDLY: 8}
        if maxticks is not None:
            try:
                self.maxticks.update(maxticks)
            except TypeError:
                # Assume we were given an integer. Use this as the maximum
                # number of ticks for every frequency and create a
                # dictionary for this
                self.maxticks = dict.fromkeys(self._freqs, maxticks)

        self.intervald = {
            DAILY: [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000,
                    10000, 20000, 50000, 100000, 200000, 500000, 1000000],
            HOURLY: [1, 2, 3, 4, 6, 12],
            MINUTELY: [1, 5, 10, 15, 30],
            SECONDLY: [1, 5, 10, 15, 30],
            MICROSECONDLY: [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000,
                            5000, 10000, 20000, 50000, 100000, 200000, 500000,
                            1000000]
        }

    def __call__(self):
        # docstring inherited
        dmin, dmax = self.viewlim_to_dt()
        self.update_from_limits(dmin, dmax)
        return super().__call__()

    def update_from_limits(self, dmin, dmax):
        delta = dmax - dmin
        # take absolute difference
        if dmin > dmax:
            delta = -delta
        numDays = delta.days
        numSeconds = np.floor(delta.total_seconds())
        numHours = numDays * HOURS_PER_DAY + np.floor(numSeconds / SEC_PER_HOUR)
        numMinutes = numDays * MINUTES_PER_DAY \
            + np.floor(numSeconds / SEC_PER_MIN)
        numMicroseconds = np.floor(delta.total_seconds() * 1e6)
        nums = [numDays, numHours, numMinutes, numSeconds, numMicroseconds]
        # Loop over all the frequencies and try to find one that gives at
        # least a minticks tick positions.  Once this is found, look for
        # an interval from an list specific to that frequency that gives no
        # more than maxticks tick positions. Also, set up some ranges
        # (bymonth, etc.) as appropriate to be passed to rrulewrapper.
        for i, (freq, num) in enumerate(zip(self._freqs, nums)):
            # If this particular frequency doesn't give enough ticks, continue
            if num < self.minticks:
                continue

            # Find the first available interval that doesn't give too many
            # ticks
            for interval in self.intervald[freq]:
                if num <= interval * (self.maxticks[freq] - 1):
                    break
            break
        else:
            # prevent interval from being undefined in case intervald was empty
            interval = 1
        super().set_params(freq=freq, interval=interval)

    def viewlim_to_dt(self):
        """Convert the view interval to datetime objects."""
        vmin, vmax = self.axis.get_view_interval()
        if vmin > vmax:
            vmin, vmax = vmax, vmin
        return num2timedelta(vmin), num2timedelta(vmax)

    def nonsingular(self, vmin, vmax):
        self.update_from_limits(*num2timedelta([vmin, vmax]))
        return super().nonsingular(vmin, vmax)


class DateConverter(units.ConversionInterface):
    """
    Converter for `datetime.date` and `datetime.datetime` data, or for
    date/time data represented as it would be converted by `date2num`.

    The 'unit' tag for such data is None or a `~datetime.tzinfo` instance.
    """

    def __init__(self, *, interval_multiples=True):
        self._interval_multiples = interval_multiples
        super().__init__()

    def axisinfo(self, unit, axis):
        """
        Return the `~matplotlib.units.AxisInfo` for *unit*.

        *unit* is a `~datetime.tzinfo` instance or None.
        The *axis* argument is required but not used.
        """
        tz = unit

        majloc = AutoDateLocator(tz=tz,
                                 interval_multiples=self._interval_multiples)
        majfmt = AutoDateFormatter(majloc, tz=tz)

        return units.AxisInfo(majloc=majloc, majfmt=majfmt, label='',
                              default_limits=majloc.default_range)

    @staticmethod
    def convert(value, unit, axis):
        """
        If *value* is not already a number or sequence of numbers, convert it
        with `date2num`.

        The *unit* and *axis* arguments are not used.
        """
        return date2num(value)

    @staticmethod
    def default_units(x, axis):
        """
        Return the `~datetime.tzinfo` instance of *x* or of its first element,
        or None
        """
        if isinstance(x, np.ndarray):
            x = x.ravel()

        try:
            x = cbook._safe_first_finite(x)
        except (TypeError, StopIteration):
            pass

        try:
            return x.tzinfo
        except AttributeError:
            pass
        return None


class ConciseDateConverter(DateConverter):
    # docstring inherited

    def __init__(self, formats=None, zero_formats=None, offset_formats=None,
                 show_offset=True, *, interval_multiples=True):
        self._formats = formats
        self._zero_formats = zero_formats
        self._offset_formats = offset_formats
        self._show_offset = show_offset
        self._interval_multiples = interval_multiples
        super().__init__()

    def axisinfo(self, unit, axis):
        # docstring inherited
        tz = unit
        majloc = AutoDateLocator(tz=tz,
                                 interval_multiples=self._interval_multiples)
        majfmt = ConciseDateFormatter(majloc, tz=tz, formats=self._formats,
                                      zero_formats=self._zero_formats,
                                      offset_formats=self._offset_formats,
                                      show_offset=self._show_offset)
        return units.AxisInfo(majloc=majloc, majfmt=majfmt, label='',
                              default_limits=majloc.default_range)


class TimedeltaConverter(units.ConversionInterface):
    """
    Converter for `datetime.timedelta` and `numpy.timedelta64` data,
    or for timedelta data represented as it would be converted by
    `~matplotlib.dates.timedelta2num`.

    The 'unit' tag for such data is None.
    """
    def axisinfo(self, unit, axis):
        """
        Return the `~matplotlib.units.AxisInfo` for *unit*.

        The *unit* argument is required but not used. It should be `None`.
        The *axis* argument is required but not used.
        """
        majloc = AutoTimedeltaLocator()
        majfmt = AutoTimedeltaFormatter(majloc)

        return units.AxisInfo(majloc=majloc, majfmt=majfmt, label='',
                              default_limits=majloc.default_range)

    @staticmethod
    def convert(value, unit, axis):
        """
        If *value* is not already a number or sequence of numbers, convert it
        with `timedelta2num`.

        The *unit* and *axis* arguments are not used.
        """
        return timedelta2num(value)


class ConciseTimedeltaConverter(TimedeltaConverter):
    # docstring inherited

    def __init__(self, formats=None, zero_formats=None, offset_formats=None,
                 show_offset=True, *, interval_multiples=True):
        self._formats = formats
        self._zero_formats = zero_formats
        self._offset_formats = offset_formats
        self._show_offset = show_offset
        self._interval_multiples = interval_multiples
        super().__init__()

    def axisinfo(self, unit, axis):
        # docstring inherited
        majloc = AutoTimedeltaLocator()
        majfmt = ConciseTimedeltaFormatter(majloc, formats=self._formats,
                                           zero_formats=self._zero_formats,
                                           offset_formats=self._offset_formats,
                                           show_offset=self._show_offset)

        return units.AxisInfo(majloc=majloc, majfmt=majfmt, label='',
                              default_limits=majloc.default_range)


class _SwitchableConverter:
    @staticmethod
    def _get_converter():
        return NotImplemented

    def axisinfo(self, *args, **kwargs):
        return self._get_converter().axisinfo(*args, **kwargs)

    def default_units(self, *args, **kwargs):
        return self._get_converter().default_units(*args, **kwargs)

    def convert(self, *args, **kwargs):
        return self._get_converter().convert(*args, **kwargs)


class _SwitchableDateConverter(_SwitchableConverter):
    """
    Helper converter-like object that generates and dispatches to
    temporary ConciseDateConverter or DateConverter instances based on
    :rc:`date.converter` and :rc:`date.interval_multiples`.
    """

    @staticmethod
    def _get_converter():
        converter_cls = {
            "concise": ConciseDateConverter, "auto": DateConverter}[
                mpl.rcParams["date.converter"]]
        interval_multiples = mpl.rcParams["date.interval_multiples"]
        return converter_cls(interval_multiples=interval_multiples)


units.registry[np.datetime64] = \
    units.registry[datetime.date] = \
    units.registry[datetime.datetime] = \
    _SwitchableDateConverter()


class _SwitchableTimedeltaConverter(_SwitchableConverter):
    """
    Helper converter-like object that generates and dispatches to
    temporary ConciseTimedeltaConverter or TimedeltaConverter instances
    based on :rc:`date.converter`.
    """
    # TODO: do we want to add a `timedelta.converter` rcParam?

    @staticmethod
    def _get_converter():
        converter_cls = {
            "concise": ConciseTimedeltaConverter, "auto": TimedeltaConverter}[
                mpl.rcParams["date.converter"]]
        return converter_cls()


units.registry[np.timedelta64] = \
    units.registry[datetime.timedelta] = \
    _SwitchableTimedeltaConverter()
