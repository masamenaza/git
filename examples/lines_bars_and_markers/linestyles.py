"""
==========
Linestyles
==========

Linestyle can be provided as simple as *solid* , *dotted*, *dashed*
or *dashdot*. Moreover, the dashing of the line can be controlled by
a dash tuple such as (offset, (on_off_seq)) as mentioned in
`.Line2D.set_linestyle`. For example, ``(0, (3, 10, 1, 15))`` means
 3pt-line,10pt-space,1pt-line,15pt-space with no offset.

*Note*: The dash style can also be configured via `.Line2D.set_dashes`
as shown in :doc:`/gallery/lines_bars_and_markers/line_demo_dash_control`
and passing a list of dash sequences using the keyword *dashes* to the
cycler in :doc:`property_cycle </tutorials/intermediate/color_cycle>`.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

linestyle_str = [
     ('solid', 'solid'),       # Same as (0, ()) or '-'
     ('dotted', 'dotted'),    # Same as (0, (1, 1)) or '.'
     ('dashed', 'dashed'),    # Same as '--'
     ('dashdot', 'dashdot')]  # Same as '-.'

linestyle_tuple = [
     ('loosely dotted',        (0, (1, 10))),
     ('densely dotted',        (0, (1, 1))),

     ('loosely dashed',        (0, (5, 10))),
     ('densely dashed',        (0, (5, 1))),

     ('loosely dashdotted',    (0, (3, 10, 1, 10))),
     ('densely dashdotted',    (0, (3, 1, 1, 1))),

     ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
     ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
     ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1)))]


def simple_plot(ax, linestyles):
    yticklabels = []
    for i, (name, linestyle) in enumerate(linestyles):
        ax.plot(X, Y+i, linestyle=linestyle, linewidth=1.5, color='black')
        yticklabels.append(name)

    ax.set(xticks=[], ylim=(-0.5, len(linestyles)-0.5),
           yticks=np.arange(len(linestyles)), yticklabels=yticklabels)

    # For each line style, add a text annotation with a small offset from
    # the reference point (0 in Axes coords, y tick value in Data coords).
    reference_transform = blended_transform_factory(ax.transAxes, ax.transData)
    for i, (name, linestyle) in enumerate(linestyles):
        ax.annotate(repr(linestyle), xy=(0.0, i), xycoords=reference_transform,
                    xytext=(-6, -12), textcoords='offset points', color="blue",
                    fontsize=8, ha="right", family="monospace")

X, Y = np.linspace(0, 100, 10), np.zeros(10)
fig, ax = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 2]},
                       figsize=(10, 6))

simple_plot(ax[0], linestyle_str[::-1])
simple_plot(ax[1], linestyle_tuple[::-1])

plt.tight_layout()
plt.show()
