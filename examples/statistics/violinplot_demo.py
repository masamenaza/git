"""
Demo of the new violinplot functionality
"""

import random
import numpy as np
import matplotlib.pyplot as plt

# fake data
fs = 10 # fontsize
pos = range(5)
data = [np.random.normal(size=100) for i in pos]

# TODO: future customizability dicts go here

# (From boxplot demo)
# demonstrate how to customize the display different elements: 
# boxprops = dict(linestyle='--', linewidth=3, color='darkgoldenrod')
# flierprops = dict(marker='o', markerfacecolor='green', markersize=12,
#                   linestyle='none')
# medianprops = dict(linestyle='-.', linewidth=2.5, color='firebrick')
# meanpointprops = dict(marker='D', markeredgecolor='black',
#                       markerfacecolor='firebrick')
# meanlineprops = dict(linestyle='--', linewidth=2.5, color='purple')

fig, axes = plt.subplots(nrows=2, ncols=3, figsize=(6,6))

axes[0, 0].violinplot(data, pos, width=0.1)
axes[0, 0].set_title('Custom violinplot 1', fontsize=fs)

axes[0, 1].violinplot(data, pos, width=0.3)
axes[0, 1].set_title('Custom violinplot 2', fontsize=fs)

axes[0, 2].violinplot(data, pos, width=0.5)
axes[0, 2].set_title('Custom violinplot 3', fontsize=fs)

axes[1, 0].violinplot(data, pos, width=0.7)
axes[1, 0].set_title('Custom violinplot 4', fontsize=fs)

axes[1, 1].violinplot(data, pos, width=0.9)
axes[1, 1].set_title('Custom violinplot 5', fontsize=fs)

axes[1, 2].violinplot(data, pos, width=1.1)
axes[1, 2].set_title('Custom violinplot 6', fontsize=fs)

for ax in axes.flatten():
    ax.set_yticklabels([])

fig.suptitle("Violin Plotting Examples")
fig.subplots_adjust(hspace=0.4)
plt.show()