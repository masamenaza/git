"""
An experimental support for curvilinear grid.
"""

import functools
from itertools import chain

import numpy as np

import matplotlib as mpl
from matplotlib.path import Path
from matplotlib.transforms import Affine2D, IdentityTransform
from .axislines import AxisArtistHelper, GridHelperBase
from .axis_artist import AxisArtist
from .grid_finder import GridFinder


def _value_and_jac_angle(func, xs, ys, xlim, ylim):
    """
    Parameters
    ----------
    func : callable
        A function that transforms the coordinates of a point (x, y) to a new coordinate
        system (u, v), and which can also take x and y as arrays of shape *shape* and
        returns (u, v) as a ``(2, shape)`` array.
    xs, ys : array-likes
        Points where *func* and its derivatives will be evaluated.
    xlim, ylim : pairs of floats
        (min, max) beyond which *func* should not be evaluated.

    Returns
    -------
    val
        Value of *func* at each point of ``(xs, ys)``.
    thetas_dx
        Angles (in radians) defined by the (u, v) components of the numerically
        differentiated df/dx vector, at each point of ``(xs, ys)``.  If needed, the
        differentiation step size is increased until at least one component of df/dx
        is nonzero, under the constraint of not going out of the *xlims*, *ylims*
        bounds.  If the gridline at a point is actually null (and the angle is thus not
        well defined), the derivatives are evaluated after taking a small step along y;
        this ensures e.g. that the tick at r=0 on a radial axis of a polar plot is
        parallel with the ticks at r!=0.
    thetas_dy
        Like *thetas_dx*, but for df/dy.
    """

    shape = np.broadcast_shapes(np.shape(xs), np.shape(ys))
    val = func(xs, ys)

    thetas = []
    eps0 = np.finfo(float).eps ** (1/2)  # cf. scipy.optimize.approx_fprime

    # Take finite difference steps towards the furthest bound; the step size will be the
    # min of epsilon and the distance to that bound.
    xlo, xhi = sorted(xlim)
    xdlo = xs - xlo
    xdhi = xhi - xs
    xeps_max = np.maximum(xdlo, xdhi)
    xeps0 = np.where(xdhi >= xdlo, 1, -1) * np.minimum(eps0, xeps_max)
    ylo, yhi = sorted(ylim)
    ydlo = ys - ylo
    ydhi = yhi - ys
    yeps_max = np.maximum(ydlo, ydhi)
    yeps0 = np.where(ydhi >= ydlo, 1, -1) * np.minimum(eps0, yeps_max)

    for dfunc, ps, eps0, eps_max, eps_q in [
            (lambda eps_p, eps_q: func(xs + eps_p, ys + eps_q),
             xs, xeps0, xeps_max, yeps0),
            (lambda eps_p, eps_q: func(xs + eps_q, ys + eps_p),
             ys, yeps0, yeps_max, xeps0),
    ]:
        thetas_dp = np.full(shape, np.nan)
        missing = np.full(shape, True)
        eps_p = eps0
        for it, eps_q in enumerate([0, eps_q]):
            while missing.any() and (abs(eps_p) < eps_max).any():
                if it == 0 and (eps_p > 1).any():
                    break  # Degenerate derivative, move a bit along the other coord.
                eps_p = np.minimum(eps_p, eps_max)
                df_x, df_y = (dfunc(eps_p, eps_q) - dfunc(0, eps_q)) / eps_p
                good = missing & ((df_x != 0) | (df_y != 0))
                thetas_dp[good] = np.arctan2(df_y, df_x)[good]
                missing &= ~good
                eps_p *= 2
        thetas.append(thetas_dp)
    return (val, *thetas)


class FixedAxisArtistHelper(AxisArtistHelper.Fixed):
    """
    Helper class for a fixed axis.
    """

    def __init__(self, grid_helper, side, nth_coord_ticks=None):
        """
        nth_coord = along which coordinate value varies.
         nth_coord = 0 ->  x axis, nth_coord = 1 -> y axis
        """

        super().__init__(loc=side)

        self.grid_helper = grid_helper
        if nth_coord_ticks is None:
            nth_coord_ticks = self.nth_coord
        self.nth_coord_ticks = nth_coord_ticks

        self.side = side

    def update_lim(self, axes):
        self.grid_helper.update_lim(axes)

    def get_tick_transform(self, axes):
        return axes.transData

    def get_tick_iterators(self, axes):
        """tick_loc, tick_angle, tick_label"""
        v1, v2 = axes.get_ylim() if self.nth_coord == 0 else axes.get_xlim()
        if v1 > v2:  # Inverted limits.
            side = {"left": "right", "right": "left",
                    "top": "bottom", "bottom": "top"}[self.side]
        else:
            side = self.side
        g = self.grid_helper
        ti1 = g.get_tick_iterator(self.nth_coord_ticks, side)
        ti2 = g.get_tick_iterator(1-self.nth_coord_ticks, side, minor=True)
        return chain(ti1, ti2), iter([])


class FloatingAxisArtistHelper(AxisArtistHelper.Floating):
    def __init__(self, grid_helper, nth_coord, value, axis_direction=None):
        """
        nth_coord = along which coordinate value varies.
         nth_coord = 0 ->  x axis, nth_coord = 1 -> y axis
        """
        super().__init__(nth_coord, value)
        self.value = value
        self.grid_helper = grid_helper
        self._extremes = -np.inf, np.inf
        self._line_num_points = 100  # number of points to create a line

    def set_extremes(self, e1, e2):
        if e1 is None:
            e1 = -np.inf
        if e2 is None:
            e2 = np.inf
        self._extremes = e1, e2

    def update_lim(self, axes):
        self.grid_helper.update_lim(axes)

        x1, x2 = axes.get_xlim()
        y1, y2 = axes.get_ylim()
        grid_finder = self.grid_helper.grid_finder
        extremes = grid_finder.extreme_finder(grid_finder.inv_transform_xy,
                                              x1, y1, x2, y2)

        lon_min, lon_max, lat_min, lat_max = extremes
        e_min, e_max = self._extremes  # ranges of other coordinates
        if self.nth_coord == 0:
            lat_min = max(e_min, lat_min)
            lat_max = min(e_max, lat_max)
        elif self.nth_coord == 1:
            lon_min = max(e_min, lon_min)
            lon_max = min(e_max, lon_max)

        lon_levs, lon_n, lon_factor = \
            grid_finder.grid_locator1(lon_min, lon_max)
        lat_levs, lat_n, lat_factor = \
            grid_finder.grid_locator2(lat_min, lat_max)

        if self.nth_coord == 0:
            xx0 = np.full(self._line_num_points, self.value)
            yy0 = np.linspace(lat_min, lat_max, self._line_num_points)
            xx, yy = grid_finder.transform_xy(xx0, yy0)
        elif self.nth_coord == 1:
            xx0 = np.linspace(lon_min, lon_max, self._line_num_points)
            yy0 = np.full(self._line_num_points, self.value)
            xx, yy = grid_finder.transform_xy(xx0, yy0)

        self._grid_info = {
            "extremes": (lon_min, lon_max, lat_min, lat_max),
            "lon_info": (lon_levs, lon_n, np.asarray(lon_factor)),
            "lat_info": (lat_levs, lat_n, np.asarray(lat_factor)),
            "lon_labels": grid_finder.tick_formatter1(
                "bottom", lon_factor, lon_levs),
            "lat_labels": grid_finder.tick_formatter2(
                "bottom", lat_factor, lat_levs),
            "line_xy": (xx, yy),
        }

    def get_axislabel_transform(self, axes):
        return Affine2D()  # axes.transData

    def get_axislabel_pos_angle(self, axes):
        def trf_xy(x, y):
            trf = self.grid_helper.grid_finder.get_transform() + axes.transData
            return trf.transform([x, y]).T

        xmin, xmax, ymin, ymax = self._grid_info["extremes"]
        if self.nth_coord == 0:
            xx0 = self.value
            yy0 = (ymin + ymax) / 2
        elif self.nth_coord == 1:
            xx0 = (xmin + xmax) / 2
            yy0 = self.value
        xy1, angle_dx, angle_dy = _value_and_jac_angle(
            trf_xy, xx0, yy0, (xmin, xmax), (ymin, ymax))
        p = axes.transAxes.inverted().transform(xy1)
        if 0 <= p[0] <= 1 and 0 <= p[1] <= 1:
            return xy1, np.rad2deg([angle_dy, angle_dx][self.nth_coord])
        else:
            return None, None

    def get_tick_transform(self, axes):
        return IdentityTransform()  # axes.transData

    def get_tick_iterators(self, axes):
        """tick_loc, tick_angle, tick_label, (optionally) tick_label"""

        lat_levs, lat_n, lat_factor = self._grid_info["lat_info"]
        yy0 = lat_levs / lat_factor

        lon_levs, lon_n, lon_factor = self._grid_info["lon_info"]
        xx0 = lon_levs / lon_factor

        e0, e1 = self._extremes

        def trf_xy(x, y):
            trf = self.grid_helper.grid_finder.get_transform() + axes.transData
            return trf.transform(np.column_stack(np.broadcast_arrays(x, y))).T

        # find angles
        if self.nth_coord == 0:
            mask = (e0 <= yy0) & (yy0 <= e1)
            (xx1, yy1), angle_normal, angle_tangent = _value_and_jac_angle(
                trf_xy, self.value, yy0[mask], (-np.inf, np.inf), (e0, e1))
            labels = self._grid_info["lat_labels"]

        elif self.nth_coord == 1:
            mask = (e0 <= xx0) & (xx0 <= e1)
            (xx1, yy1), angle_tangent, angle_normal = _value_and_jac_angle(
                trf_xy, xx0[mask], self.value, (-np.inf, np.inf), (e0, e1))
            labels = self._grid_info["lon_labels"]

        labels = [l for l, m in zip(labels, mask) if m]
        tick_to_axes = self.get_tick_transform(axes) - axes.transAxes
        in_01 = functools.partial(
            mpl.transforms._interval_contains_close, (0, 1))

        def f1():
            for x, y, normal, tangent, lab \
                    in zip(xx1, yy1, angle_normal, angle_tangent, labels):
                c2 = tick_to_axes.transform((x, y))
                if in_01(c2[0]) and in_01(c2[1]):
                    yield [x, y], *np.rad2deg([normal, tangent]), lab

        return f1(), iter([])

    def get_line_transform(self, axes):
        return axes.transData

    def get_line(self, axes):
        self.update_lim(axes)
        x, y = self._grid_info["line_xy"]
        return Path(np.column_stack([x, y]))


class GridHelperCurveLinear(GridHelperBase):
    def __init__(self, aux_trans,
                 extreme_finder=None,
                 grid_locator1=None,
                 grid_locator2=None,
                 tick_formatter1=None,
                 tick_formatter2=None):
        """
        aux_trans : a transform from the source (curved) coordinate to
        target (rectilinear) coordinate. An instance of MPL's Transform
        (inverse transform should be defined) or a tuple of two callable
        objects which defines the transform and its inverse. The callables
        need take two arguments of array of source coordinates and
        should return two target coordinates.

        e.g., ``x2, y2 = trans(x1, y1)``
        """
        super().__init__()
        self._grid_info = None
        self._aux_trans = aux_trans
        self.grid_finder = GridFinder(aux_trans,
                                      extreme_finder,
                                      grid_locator1,
                                      grid_locator2,
                                      tick_formatter1,
                                      tick_formatter2)

    def update_grid_finder(self, aux_trans=None, **kwargs):
        if aux_trans is not None:
            self.grid_finder.update_transform(aux_trans)
        self.grid_finder.update(**kwargs)
        self._old_limits = None  # Force revalidation.

    def new_fixed_axis(self, loc,
                       nth_coord=None,
                       axis_direction=None,
                       offset=None,
                       axes=None):
        if axes is None:
            axes = self.axes
        if axis_direction is None:
            axis_direction = loc
        helper = FixedAxisArtistHelper(self, loc, nth_coord_ticks=nth_coord)
        axisline = AxisArtist(axes, helper, axis_direction=axis_direction)
        # Why is clip not set on axisline, unlike in new_floating_axis or in
        # the floating_axig.GridHelperCurveLinear subclass?
        return axisline

    def new_floating_axis(self, nth_coord,
                          value,
                          axes=None,
                          axis_direction="bottom"
                          ):
        if axes is None:
            axes = self.axes
        helper = FloatingAxisArtistHelper(
            self, nth_coord, value, axis_direction)
        axisline = AxisArtist(axes, helper)
        axisline.line.set_clip_on(True)
        axisline.line.set_clip_box(axisline.axes.bbox)
        # axisline.major_ticklabels.set_visible(True)
        # axisline.minor_ticklabels.set_visible(False)
        return axisline

    def _update_grid(self, x1, y1, x2, y2):
        self._grid_info = self.grid_finder.get_grid_info(x1, y1, x2, y2)

    def get_gridlines(self, which="major", axis="both"):
        grid_lines = []
        if axis in ["both", "x"]:
            for gl in self._grid_info["lon"]["lines"]:
                grid_lines.extend(gl)
        if axis in ["both", "y"]:
            for gl in self._grid_info["lat"]["lines"]:
                grid_lines.extend(gl)
        return grid_lines

    def get_tick_iterator(self, nth_coord, axis_side, minor=False):

        # axisnr = dict(left=0, bottom=1, right=2, top=3)[axis_side]
        angle_tangent = dict(left=90, right=90, bottom=0, top=0)[axis_side]
        # angle = [0, 90, 180, 270][axisnr]
        lon_or_lat = ["lon", "lat"][nth_coord]
        if not minor:  # major ticks
            for (xy, a), l in zip(
                    self._grid_info[lon_or_lat]["tick_locs"][axis_side],
                    self._grid_info[lon_or_lat]["tick_labels"][axis_side]):
                angle_normal = a
                yield xy, angle_normal, angle_tangent, l
        else:
            for (xy, a), l in zip(
                    self._grid_info[lon_or_lat]["tick_locs"][axis_side],
                    self._grid_info[lon_or_lat]["tick_labels"][axis_side]):
                angle_normal = a
                yield xy, angle_normal, angle_tangent, ""
            # for xy, a, l in self._grid_info[lon_or_lat]["ticks"][axis_side]:
            #     yield xy, a, ""
