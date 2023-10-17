from collections.abc import Callable, Sequence
from typing import Any, Literal

from matplotlib.axis import Axis
from matplotlib.transforms import Transform
from matplotlib.projections.polar import _AxisWrapper

import numpy as np

class _DummyAxis:
    __name__: str
    def __init__(self, minpos: float = ...) -> None: ...
    def get_view_interval(self) -> tuple[float, float]: ...
    def set_view_interval(self, vmin: float, vmax: float) -> None: ...
    def get_minpos(self) -> float: ...
    def get_data_interval(self) -> tuple[float, float]: ...
    def set_data_interval(self, vmin: float, vmax: float) -> None: ...
    def get_tick_space(self) -> int: ...

class TickHelper:
    axis: None | Axis | _DummyAxis | _AxisWrapper
    def set_axis(self, axis: Axis | _DummyAxis | _AxisWrapper | None) -> None: ...
    def create_dummy_axis(self, **kwargs:Any) -> None: ...

class Formatter(TickHelper):
    locs: list[float]
    def __call__(self, x: float, pos: int | None = ...) -> str: ...
    def format_ticks(self, values: list[float]) -> list[str]: ...
    def format_data(self, value: float) -> str: ...
    def format_data_short(self, value: float) -> str: ...
    def get_offset(self) -> str: ...
    def set_locs(self, locs: list[float]) -> None: ...
    @staticmethod
    def fix_minus(s: str) -> str: ...

class NullFormatter(Formatter): ...

class FixedFormatter(Formatter):
    seq: Sequence[str]
    offset_string: str
    def __init__(self, seq: Sequence[str]) -> None: ...
    def set_offset_string(self, ofs: str) -> None: ...

class FuncFormatter(Formatter):
    func: Callable[[float, int | None], str]
    offset_string: str
    # Callable[[float, int | None], str] | Callable[[float], str]
    def __init__(self, func: Callable[..., str]) -> None: ...
    def set_offset_string(self, ofs: str) -> None: ...

class FormatStrFormatter(Formatter):
    fmt: str
    def __init__(self, fmt: str) -> None: ...

class StrMethodFormatter(Formatter):
    fmt: str
    def __init__(self, fmt: str) -> None: ...

class ScalarFormatter(Formatter):
    orderOfMagnitude: int
    format: str
    def __init__(
        self,
        useOffset: bool | float | None = ...,
        useMathText: bool | None = ...,
        useLocale: bool | None = ...,
    ) -> None: ...
    offset: float
    def get_useOffset(self) -> bool: ...
    def set_useOffset(self, val: bool | float) -> None: ...
    @property
    def useOffset(self) -> bool: ...
    @useOffset.setter
    def useOffset(self, val: bool | float) -> None: ...
    def get_useLocale(self) -> bool: ...
    def set_useLocale(self, val: bool | None) -> None: ...
    @property
    def useLocale(self) -> bool: ...
    @useLocale.setter
    def useLocale(self, val: bool | None) -> None: ...
    def get_useMathText(self) -> bool: ...
    def set_useMathText(self, val: bool | None) -> None: ...
    @property
    def useMathText(self) -> bool: ...
    @useMathText.setter
    def useMathText(self, val: bool | None) -> None: ...
    def set_scientific(self, b: bool) -> None: ...
    def set_powerlimits(self, lims: tuple[int, int]) -> None: ...
    def format_data_short(self, value: float | np.ma.MaskedArray) -> str: ...
    def format_data(self, value: float) -> str: ...

class LogFormatter(Formatter):
    minor_thresholds: tuple[float, float]
    def __init__(
        self,
        base: float = ...,
        labelOnlyBase: bool = ...,
        minor_thresholds: tuple[float, float] | None = ...,
        linthresh: float | None = ...,
    ) -> None: ...
    def set_base(self, base: float) -> None: ...
    labelOnlyBase: bool
    def set_label_minor(self, labelOnlyBase: bool) -> None: ...
    def set_locs(self, locs: Any | None = ...) -> None: ...
    def format_data(self, value: float) -> str: ...
    def format_data_short(self, value: float) -> str: ...

class LogFormatterExponent(LogFormatter): ...
class LogFormatterMathtext(LogFormatter): ...
class LogFormatterSciNotation(LogFormatterMathtext): ...

class LogitFormatter(Formatter):
    def __init__(
        self,
        *,
        use_overline: bool = ...,
        one_half: str = ...,
        minor: bool = ...,
        minor_threshold: int = ...,
        minor_number: int = ...
    ) -> None: ...
    def use_overline(self, use_overline: bool) -> None: ...
    def set_one_half(self, one_half: str) -> None: ...
    def set_minor_threshold(self, minor_threshold: int) -> None: ...
    def set_minor_number(self, minor_number: int) -> None: ...
    def format_data_short(self, value: float) -> str: ...

class EngFormatter(Formatter):
    ENG_PREFIXES: dict[int, str]
    unit: str
    places: int | None
    sep: str
    def __init__(
        self,
        unit: str = ...,
        places: int | None = ...,
        sep: str = ...,
        *,
        usetex: bool | None = ...,
        useMathText: bool | None = ...
    ) -> None: ...
    def get_usetex(self) -> bool: ...
    def set_usetex(self, val: bool | None) -> None: ...
    @property
    def usetex(self) -> bool: ...
    @usetex.setter
    def usetex(self, val: bool | None) -> None: ...
    def get_useMathText(self) -> bool: ...
    def set_useMathText(self, val: bool | None) -> None: ...
    @property
    def useMathText(self) -> bool: ...
    @useMathText.setter
    def useMathText(self, val: bool | None) -> None: ...
    def format_eng(self, num: float) -> str: ...

class PercentFormatter(Formatter):
    xmax: float
    decimals: int | None
    def __init__(
        self,
        xmax: float = ...,
        decimals: int | None = ...,
        symbol: str | None = ...,
        is_latex: bool = ...,
    ) -> None: ...
    def format_pct(self, x: float, display_range: float) -> str: ...
    def convert_to_pct(self, x: float) -> float: ...
    @property
    def symbol(self) -> str: ...
    @symbol.setter
    def symbol(self, symbol: str) -> None: ...

class Locator(TickHelper):
    MAXTICKS: int
    def tick_values(self, vmin: float, vmax: float) -> Sequence[float]: ...
    # Implementation accepts **kwargs, but is a no-op other than a warning
    # Typing as **kwargs would require each subclass to accept **kwargs for mypy
    def set_params(self) -> None: ...
    def __call__(self) -> Sequence[float]: ...
    def raise_if_exceeds(self, locs: Sequence[float]) -> Sequence[float]: ...
    def nonsingular(self, v0: float, v1: float) -> tuple[float, float]: ...
    def view_limits(self, vmin: float, vmax: float) -> tuple[float, float]: ...

class IndexLocator(Locator):
    offset: float
    def __init__(self, base: float, offset: float) -> None: ...
    def set_params(
        self, base: float | None = ..., offset: float | None = ...
    ) -> None: ...

class FixedLocator(Locator):
    nbins: int | None
    def __init__(self, locs: Sequence[float], nbins: int | None = ...) -> None: ...
    def set_params(self, nbins: int | None = ...) -> None: ...

class NullLocator(Locator): ...

class LinearLocator(Locator):
    presets: dict[tuple[float, float], Sequence[float]]
    def __init__(
        self,
        numticks: int | None = ...,
        presets: dict[tuple[float, float], Sequence[float]] | None = ...,
    ) -> None: ...
    @property
    def numticks(self) -> int: ...
    @numticks.setter
    def numticks(self, numticks: int | None) -> None: ...
    def set_params(
        self,
        numticks: int | None = ...,
        presets: dict[tuple[float, float], Sequence[float]] | None = ...,
    ) -> None: ...

class MultipleLocator(Locator):
    def __init__(self, base: float = ..., offset: float = ...) -> None: ...
    def set_params(self, base: float | None = ..., offset: float | None = ...) -> None: ...
    def view_limits(self, dmin: float, dmax: float) -> tuple[float, float]: ...

class _Edge_integer:
    step: float
    def __init__(self, step: float, offset: float) -> None: ...
    def closeto(self, ms: float, edge: float) -> bool: ...
    def le(self, x: float) -> float: ...
    def ge(self, x: float) -> float: ...

class MaxNLocator(Locator):
    default_params: dict[str, Any]
    def __init__(self, nbins: int | Literal["auto"] | None = ..., **kwargs:Any) -> None: ...
    def set_params(self, **kwargs:Any) -> None: ...
    def view_limits(self, dmin: float, dmax: float) -> tuple[float, float]: ...

class LogLocator(Locator):
    numdecs: float
    numticks: int | None
    def __init__(
        self,
        base: float = ...,
        subs: None | Literal["auto", "all"] | Sequence[float] = ...,
        numdecs: float = ...,
        numticks: int | None = ...,
    ) -> None: ...
    def set_params(
        self,
        base: float | None = ...,
        subs: Literal["auto", "all"] | Sequence[float] | None = ...,
        numdecs: float | None = ...,
        numticks: int | None = ...,
    ) -> None: ...

class SymmetricalLogLocator(Locator):
    numticks: int
    def __init__(
        self,
        transform: Transform | None = ...,
        subs: Sequence[float] | None = ...,
        linthresh: float | None = ...,
        base: float | None = ...,
    ) -> None: ...
    def set_params(
        self, subs: Sequence[float] | None = ..., numticks: int | None = ...
    ) -> None: ...

class AsinhLocator(Locator):
    linear_width: float
    numticks: int
    symthresh: float
    base: int
    subs: Sequence[float] | None
    def __init__(
        self,
        linear_width: float,
        numticks: int = ...,
        symthresh: float = ...,
        base: int = ...,
        subs: Sequence[float] | None = ...,
    ) -> None: ...
    def set_params(
        self,
        numticks: int | None = ...,
        symthresh: float | None = ...,
        base: int | None = ...,
        subs: Sequence[float] | None = ...,
    ) -> None: ...

class LogitLocator(MaxNLocator):
    def __init__(
        self, minor: bool = ..., *, nbins: Literal["auto"] | int = ...
    ) -> None: ...
    def set_params(self, minor: bool | None = ..., **kwargs:Any) -> None: ...
    @property
    def minor(self) -> bool: ...
    @minor.setter
    def minor(self, value: bool) -> None: ...

class AutoLocator(MaxNLocator):
    def __init__(self) -> None: ...

class AutoMinorLocator(Locator):
    ndivs: int
    def __init__(self, n: int | None = ...) -> None: ...
