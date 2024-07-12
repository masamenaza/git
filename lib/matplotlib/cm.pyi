from collections.abc import Iterator, Mapping, Sequence
from matplotlib import cbook, colors
from matplotlib.colorbar import Colorbar

import numpy as np
from numpy.typing import ArrayLike

class ColormapRegistry(Mapping[str, colors.Colormap]):
    def __init__(self, cmaps: Mapping[str, colors.Colormap]) -> None: ...
    def __getitem__(self, item: str) -> colors.Colormap: ...
    def __iter__(self) -> Iterator[str]: ...
    def __len__(self) -> int: ...
    def __call__(self) -> list[str]: ...
    def register(
        self, cmap: colors.Colormap, *, name: str | None = ..., force: bool = ...
    ) -> None: ...
    def unregister(self, name: str) -> None: ...
    def get_cmap(self, cmap: str | colors.Colormap) -> colors.Colormap: ...

_colormaps: ColormapRegistry = ...
_multivar_colormaps: ColormapRegistry = ...
_bivar_colormaps: ColormapRegistry = ...

class VectorMappable:
    scalars: list[ScalarMappable]
    callbacks: cbook.CallbackRegistry
    def __init__(
        self,
        norm: colors.Normalize | None | Sequence[colors.Normalize | None] = ...,
        cmap: str | colors.Colormap | colors.BivarColormap | colors.MultivarColormap | None = ...,
    ) -> None: ...
    @property
    def cmap(self) -> colors.Colormap | colors.BivarColormap | colors.MultivarColormap: ...
    @cmap.setter
    def cmap(self, cmap: str | colors.Colormap | colors.BivarColormap | colors.MultivarColormap) -> None: ...
    @property
    def colorbar(self) -> Colorbar | None: ...
    @colorbar.setter
    def colorbar(self, colorbar) -> None: ...
    def get_cmap(self) -> colors.Colormap | colors.BivarColormap | colors.MultivarColormap: ...
    def set_cmap(self, cmap: str | colors.Colormap | colors.BivarColormap | colors.MultivarColormap) -> None: ...
    def to_rgba(
        self,
        x: np.ndarray,
        alpha: float | ArrayLike | None = ...,
        bytes: bool = ...,
        norm: bool = ...,
    ) -> np.ndarray: ...
    def set_array(self, A: ArrayLike | None) -> None: ...
    def get_array(self) -> np.ndarray | None: ...
    def get_clim(self) -> tuple[float, float] | tuple[list[float], list[float]]: ...
    def set_clim(
        self,
        vmin: float | tuple[float, float] | Sequence[float | None] | None = ...,
        vmax: float | Sequence[float | None] | None = ...,
    ) -> None: ...
    def get_alpha(self) -> float | None: ...
    @property
    def norm(self) -> colors.Normalize | list[colors.Normalize]: ...
    @norm.setter
    def norm(self, norm: colors.Normalize | str | list[colors.Normalize | str]) -> None: ...
    def set_norm(self, norm: colors.Normalize | str | list[colors.Normalize | str]): ...
    def autoscale(self) -> None: ...
    def autoscale_None(self) -> None: ...
    intercepted_changed: bool
    def changed(self) -> None: ...

def get_cmap(name: str | colors.Colormap | None = ..., lut: int | None = ...) -> colors.Colormap: ...

class ScalarMappable:
    cmap: colors.Colormap | None
    colorbar: Colorbar | None
    callbacks: cbook.CallbackRegistry
    def __init__(
        self,
        norm: colors.Normalize | None = ...,
        cmap: str | colors.Colormap | None = ...,
    ) -> None: ...
    def to_rgba(
        self,
        x: np.ndarray,
        alpha: float | ArrayLike | None = ...,
        bytes: bool = ...,
        norm: bool = ...,
    ) -> np.ndarray: ...
    def set_array(self, A: ArrayLike | None) -> None: ...
    def get_array(self) -> np.ndarray | None: ...
    def get_cmap(self) -> colors.Colormap: ...
    def get_clim(self) -> tuple[float, float]: ...
    def set_clim(self, vmin: float | tuple[float, float] | None = ..., vmax: float | None = ...) -> None: ...
    def get_alpha(self) -> float | None: ...
    def set_cmap(self, cmap: str | colors.Colormap) -> None: ...
    @property
    def norm(self) -> colors.Normalize: ...
    @norm.setter
    def norm(self, norm: colors.Normalize | str | None) -> None: ...
    def set_norm(self, norm: colors.Normalize | str | None) -> None: ...
    def autoscale(self) -> None: ...
    def autoscale_None(self) -> None: ...
    def changed(self) -> None: ...

def ensure_cmap(cmap: str | colors.Colormap | colors.BivarColormap | colors.MultivarColormap, accept_multivariate: bool = ...): ...
def ensure_multivariate_norm(n_variates: int, norm: colors.Normalize | str | list[colors.Normalize | str]): ...
def ensure_multivariate_data(n_variates: int, data: ArrayLike) -> None: ...
def ensure_multivariate_clim(
    n_variates: int,
    vmin: float | None | tuple[float, float] | list[float | None] = ...,
    vmax: float | None | list[float | None] = ...,
    ): ...
def ensure_multivariate_params(
    n_variates: int,
    data: ArrayLike,
    norm: colors.Normalize | str | list[colors.Normalize | str],
    vmin: float | None | tuple[float, float] | list[float | None],
    vmax: float | None | list[float | None],
    ): ...
