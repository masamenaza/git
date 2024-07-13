"""
=================
Grouped bar chart
=================

This example serves to develop and discuss the API. It's geared towards illustating
API usage and design decisions only through the development phase. It's not intended
to go into the final PR in this form.

Case 1: multiple separate datasets
----------------------------------

"""
import matplotlib.pyplot as plt
import numpy as np

x = ['A', 'B']
data1 = [1, 1.2]
data2 = [2, 2.4]
data3 = [3, 3.6]


fig, axs = plt.subplots(1, 2)

# current solution: manual positioning with multiple bar)= calls
label_pos = np.array([0, 1])
bar_width = 0.8 / 3
data_shift = -1*bar_width + np.array([0, bar_width, 2*bar_width])
axs[0].bar(label_pos + data_shift[0], data1, width=bar_width, label="data1")
axs[0].bar(label_pos + data_shift[1], data2, width=bar_width, label="data2")
axs[0].bar(label_pos + data_shift[2], data3, width=bar_width, label="data3")
axs[0].set_xticks(label_pos, x)
axs[0].legend()

# grouped_bar() with list of datasets
# note also that this is a straight-forward generalization of the single-dataset case:
#   bar(x, data1, label="data1")
axs[1].grouped_bar(x, [data1, data2, data3], dataset_labels=["data1", "data2", "data3"])


# %%
# Case 1b: multiple datasets as dict
# ----------------------------------
# instead of carrying a list of datasets and a list of dataset labels, users may
# want to organized their datasets in a dict.

datasets = {
    'data1': data1,
    'data2': data2,
    'data3': data3,
}

# %%
# While you can feed keys and values into the above API, it may be convenient to pass
# the whole dict as "data" and automatically extract the labels from the keys:

fig, axs = plt.subplots(1, 2)

# explicitly extract values and labels from a dict and feed to grouped_bar():
axs[0].grouped_bar(x, datasets.values(), dataset_labels=datasets.keys())
# accepting a dict as input
axs[1].grouped_bar(x, datasets)

# %%
# Case 2: 2D array data
# ---------------------
# When receiving a 2D array, we interpret the data as
#
# .. code-block:: none
#
#             dataset_0 dataset_1 dataset_2
#    x[0]='A'  ds0_a     ds1_a     ds2_a
#    x[1]='B'  ds0_b     ds1_b     ds2_b
#
# This is consistent with the standard data science interpretation of instances
# on the vertical and features on the horizontal. And also matches how pandas is
# interpreting rows and columns.
#
# Note that a list of individual datasets and a 2D array behave structurally different,
# i.e. hen turning a list into a numpy array, you have to transpose that array to get
# the correct representation. Those two behave the same::
#
#     grouped_bar(x, [data1, data2])
#     grouped_bar(x, np.array([data1, data2]).T)
#
# This is a conscious decision, because the commonly understood dimension ordering
# semantics of "list of datasets" and 2D array of datasets is different.

x = ['A', 'B']
data = np.array([
    [1, 2, 3],
    [1.2, 2.4, 3.6],
])
columns = ["data1", "data2", "data3"]

fig, ax = plt.subplots()
ax.grouped_bar(x, data, dataset_labels=columns)

# %%
# This creates the same plot as pandas (code cannot be executed because pandas
# os not a doc dependency)::
#
#     df = pd.DataFrame(data, index=x, columns=columns)
#     df.plot.bar()
