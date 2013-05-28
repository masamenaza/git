# -*- encoding: utf-8 -*-
import io

from matplotlib import rcParams
from matplotlib import pyplot as plt
from matplotlib.testing.decorators import image_comparison, knownfailureif


@image_comparison(baseline_images=['pdf_use14corefonts'], extensions=['pdf'])
def test_use14corefonts():
    rcParams['pdf.use14corefonts'] = True
    rcParams['font.family'] = 'sans-serif'
    rcParams['font.size'] = 8
    rcParams['font.sans-serif'] = ['Helvetica']

    title = u'Test PDF backend with option use14corefonts=True'

    text = u'''A three-line text positioned just above a blue line
    and containing some French characters and the euro symbol:
    "Merci pépé pour les 10 €"'''

    plt.figure()
    plt.title(title)
    plt.text(0.5, 0.5, text, horizontalalignment='center', fontsize=24)
    plt.axhline(0.5, linewidth=0.5)


def test_type42():
    rcParams['pdf.fonttype'] = 42

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot([1, 2, 3])
    fig.savefig(io.BytesIO())


if __name__ == "__main__":
    import nose
    nose.runmodule(argv=['-s', '--with-doctest'], exit=False)
