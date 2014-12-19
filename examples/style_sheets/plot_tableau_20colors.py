"""
This shows an example of the "tableau_20colors" styling,
which uses Tableau's "Tableau 20" color scheme.
"""


from matplotlib import pyplot as plt
import numpy as np

x = np.linspace(0, 10)

with plt.style.context('tableau_20colors'):
    plt.plot(x, np.sin(x) + x + np.random.randn(50))
    plt.plot(x, np.sin(x) + 0.5 * x + np.random.randn(50))
    plt.plot(x, np.sin(x) + 2 * x + np.random.randn(50))
    plt.plot(x, np.sin(x) + 3 * x + np.random.randn(50))
    plt.plot(x, np.sin(x) + 4 * x + np.random.randn(50))
    plt.plot(x, np.sin(x) + 5 * x + np.random.randn(50))

plt.show()
