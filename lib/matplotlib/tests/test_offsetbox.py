from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from matplotlib.testing.decorators import image_comparison
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.offsetbox import AnchoredOffsetbox, DrawingArea


@image_comparison(baseline_images=['offsetbox_clipping'], remove_text=True)
def test_offsetbox_clipping():
    # - create a plot
    # - put an AnchoredOffsetbox with a child DrawingArea
    #   at the center of the axes
    # - give the DrawingArea a gray background
    # - put a black line across the bounds of the DrawingArea
    # - see that the black line is clipped to the edges of
    #   the DrawingArea.
    fig, ax = plt.subplots()
    size = 100
    da = DrawingArea(size, size, clip=True)
    bg = mpatches.Rectangle((0, 0), size, size,
                            facecolor='#CCCCCC',
                            edgecolor='None',
                            linewidth=0)
    line = mlines.Line2D([-size*.5, size*1.5], [size/2, size/2],
                         color='black',
                         linewidth=10)
    anchored_box = AnchoredOffsetbox(
        loc=10,
        child=da,
        pad=0.,
        frameon=False,
        bbox_to_anchor=(.5, .5),
        bbox_transform=ax.transAxes,
        borderpad=0.)

    da.add_artist(bg)
    da.add_artist(line)
    ax.add_artist(anchored_box)
    ax.set_xlim((0, 1))
    ax.set_ylim((0, 1))


def test_offsetbox_clip_children():
    # - create a plot
    # - put an AnchoredOffsetbox with a child DrawingArea
    #   at the center of the axes
    # - give the DrawingArea a gray background
    # - put a black line across the bounds of the DrawingArea
    # - see that the black line is clipped to the edges of
    #   the DrawingArea.
    fig, ax = plt.subplots()
    size = 100
    da = DrawingArea(size, size, clip=True)
    bg = mpatches.Rectangle((0, 0), size, size,
                            facecolor='#CCCCCC',
                            edgecolor='None',
                            linewidth=0)
    line = mlines.Line2D([-size*.5, size*1.5], [size/2, size/2],
                         color='black',
                         linewidth=10)
    anchored_box = AnchoredOffsetbox(
        loc=10,
        child=da,
        pad=0.,
        frameon=False,
        bbox_to_anchor=(.5, .5),
        bbox_transform=ax.transAxes,
        borderpad=0.)

    da.add_artist(bg)
    da.add_artist(line)
    ax.add_artist(anchored_box)

    fig.canvas.draw()
    assert not fig.stale
    da.clip_children = True
    assert fig.stale


def test_offsetbox_loc_codes():
    # Check that valid string location codes all work with an AnchoredOffsetbox
    codes = {'upper right': 1,
             'upper left': 2,
             'lower left': 3,
             'lower right': 4,
             'right': 5,
             'center left': 6,
             'center right': 7,
             'lower center': 8,
             'upper center': 9,
             'center': 10,
             }
    fig, ax = plt.subplots()
    da = DrawingArea(100, 100)
    for code in codes:
        anchored_box = AnchoredOffsetbox(loc=code, child=da)
        ax.add_artist(anchored_box)
    fig.canvas.draw()


@image_comparison(baseline_images=['rasterized_patch'],
                  extensions=['pdf'], tol=0.01)
def test_rasterized_patch_pdf():
    fig = plt.figure()
    ax = fig.add_subplot(111)

    patch1 = mpatches.Rectangle((0.5, 0.5), 1., 1., color='red',
                                          label='patch1')
    patch2 = mpatches.Rectangle((2.0, 0.5), 1., 1., color='blue',
                                          label='patch2')

    ax.add_patch(patch1)
    ax.add_patch(patch2)

    ax.set_xlim(0., 3.5)
    ax.set_ylim(0., 3)

    legend = ax.legend()
    # rasterize the first patch in the legend
    legend.get_patches()[0].set_rasterized(True)


@image_comparison(baseline_images=['rasterized_patches'],
                  extensions=['pdf'], tol=0.01)
def test_rasterized_patches_pdf():
    fig = plt.figure()
    ax = fig.add_subplot(111)

    patch1 = mpatches.Rectangle((0.5, 0.5), 1., 1., color='red',
                                          label='patch1')
    patch2 = mpatches.Rectangle((2.0, 0.5), 1., 1., color='blue',
                                          label='patch2')

    ax.add_patch(patch1)
    ax.add_patch(patch2)

    ax.set_xlim(0., 3.5)
    ax.set_ylim(0., 3)

    legend = ax.legend()
    # rasterize both patches in the legend
    legend.get_patches()[0].set_rasterized(True)
    legend.get_patches()[1].set_rasterized(True)


@image_comparison(baseline_images=['rasterized_legend'],
                  extensions=['pdf'], tol=0.01)
def test_rasterized_legend_pdf():
    fig = plt.figure()
    ax = fig.add_subplot(111)

    patch1 = mpatches.Rectangle((0.5, 0.5), 1., 1., color='red',
                                          label='patch1')
    patch2 = mpatches.Rectangle((2.0, 0.5), 1., 1., color='blue',
                                          label='patch2')

    ax.add_patch(patch1)
    ax.add_patch(patch2)

    ax.set_xlim(0., 3.5)
    ax.set_ylim(0., 3)

    legend = ax.legend()
    # rasterize the entire legend
    legend.set_rasterized(True)


@image_comparison(baseline_images=['rasterized_patch'],
                  extensions=['png'], tol=0.01)
def test_rasterized_patch_png():
    fig = plt.figure()
    ax = fig.add_subplot(111)

    patch1 = mpatches.Rectangle((0.5, 0.5), 1., 1., color='red',
                                          label='patch1')
    patch2 = mpatches.Rectangle((2.0, 0.5), 1., 1., color='blue',
                                          label='patch2')

    ax.add_patch(patch1)
    ax.add_patch(patch2)

    ax.set_xlim(0., 3.5)
    ax.set_ylim(0., 3)

    legend = ax.legend()
    # rasterize the first patch in the legend
    legend.get_patches()[0].set_rasterized(True)


@image_comparison(baseline_images=['rasterized_patches'],
                  extensions=['png'], tol=0.01)
def test_rasterized_patches_png():
    fig = plt.figure()
    ax = fig.add_subplot(111)

    patch1 = mpatches.Rectangle((0.5, 0.5), 1., 1., color='red',
                                          label='patch1')
    patch2 = mpatches.Rectangle((2.0, 0.5), 1., 1., color='blue',
                                          label='patch2')

    ax.add_patch(patch1)
    ax.add_patch(patch2)

    ax.set_xlim(0., 3.5)
    ax.set_ylim(0., 3)

    legend = ax.legend()
    # rasterize both patches in the legend
    legend.get_patches()[0].set_rasterized(True)
    legend.get_patches()[1].set_rasterized(True)


@image_comparison(baseline_images=['rasterized_legend'],
                  extensions=['png'], tol=0.01)
def test_rasterized_legend_png():
    fig = plt.figure()
    ax = fig.add_subplot(111)

    patch1 = mpatches.Rectangle((0.5, 0.5), 1., 1., color='red',
                                          label='patch1')
    patch2 = mpatches.Rectangle((2.0, 0.5), 1., 1., color='blue',
                                          label='patch2')

    ax.add_patch(patch1)
    ax.add_patch(patch2)

    ax.set_xlim(0., 3.5)
    ax.set_ylim(0., 3)

    legend = ax.legend()
    # rasterize the entire legend
    legend.set_rasterized(True)
