#!/usr/bin/env python

from matplotlib.widgets import Cursor
import numpy as np
import matplotlib.pyplot as plt


fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, axisbg='#FFFFCC')

x, y = 4*(np.random.rand(2, 100)-.5)
ax.plot(x, y, 'o')
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)

# set useblit = True on gtkagg for enhanced performance
cursor = Cursor(ax, useblit=True, color='red', linewidth=2 )

# The next two lines are here just to "simulate" for what the cursor will look
# like for the gallery, because the documentation is generated without a GUI
ax.axvline(.3, 0, 1, color='red', linewidth=2)
ax.axhline(.14, 0, 1, color='red', linewidth=2)

plt.show()
