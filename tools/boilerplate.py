"""
Script to autogenerate pyplot wrappers.

When this script is run, the current contents of pyplot are
split into generatable and non-generatable content (via the magic header
:attr:`PYPLOT_MAGIC_HEADER`) and the generatable content is overwritten.
Hence, the non-generatable content should be edited in the pyplot.py file
itself, whereas the generatable content must be edited via templates in
this file.

This file is python 3 only due to the use of `inspect`
"""
# We did try to do the wrapping the smart way,
# with callable functions and new.function, but could never get the
# docstrings right for python2.2.  See
# http://groups.google.com/group/comp.lang.python/browse_frm/thread/dcd63ec13096a0f6/1b14640f3a4ad3dc?#1b14640f3a4ad3dc
# For some later history, see
# http://thread.gmane.org/gmane.comp.python.matplotlib.devel/7068

import os
import inspect
import random
import types

import textwrap

# this line imports the installed copy of matplotlib, and not the local copy
from matplotlib.axes import Axes


# this is the magic line that must exist in pyplot, after which the boilerplate content will be
# appended
PYPLOT_MAGIC_HEADER = '################# REMAINING CONTENT GENERATED BY boilerplate.py ##############\n'

PYPLOT_PATH = os.path.join(os.path.dirname(__file__), 'lib', 'matplotlib',
                           'pyplot.py')


AUTOGEN_MSG = """
# Autogenerated by boilerplate.py.  Do not edit as changes will be lost."""


PLOT_TEMPLATE = AUTOGEN_MSG + """
@_autogen_docstring(Axes.%(func)s)
def %(func)s(%(argspec)s):
    %(ax)s = gca()
    %(ret)s = %(ax)s.%(func)s(%(call)s)
%(mappable)s
    return %(ret)s
"""


# Used for misc functions such as cla/legend etc.
MISC_FN_TEMPLATE = AUTOGEN_MSG + """
@docstring.copy_dedent(Axes.%(func)s)
def %(func)s(%(argspec)s):
    %(ret)s = gca().%(func)s(%(call)s)
    return %(ret)s
"""

# Used for colormap functions
CMAP_TEMPLATE = AUTOGEN_MSG + '''
def {name}():
    """
    Set the colormap to "{name}".

    This changes the default colormap as well as the colormap of the current
    image if there is one. See ``help(colormaps)`` for more information.
    """
    set_cmap("{name}")

'''

CMAP_TEMPLATE_DEPRECATED = AUTOGEN_MSG + '''
def {name}():
    """
    Set the colormap to "{name}".

    This changes the default colormap as well as the colormap of the current
    image if there is one. See ``help(colormaps)`` for more information.
    """
    from matplotlib.cbook import warn_deprecated
    warn_deprecated(
                    "2.0",
                    name="{name}",
                    obj_type="colormap"
                    )
    set_cmap("{name}")

'''


def boilerplate_gen():
    """Generator of lines for the automated part of pyplot."""

    # these methods are all simple wrappers of Axes methods by the same
    # name.
    _plotcommands = (
        'acorr',
        'angle_spectrum',
        'arrow',
        'axhline',
        'axhspan',
        'axvline',
        'axvspan',
        'bar',
        'barh',
        'broken_barh',
        'boxplot',
        'cohere',
        'clabel',
        'contour',
        'contourf',
        'csd',
        'errorbar',
        'eventplot',
        'fill',
        'fill_between',
        'fill_betweenx',
        'hexbin',
        'hist',
        'hist2d',
        'hlines',
        'imshow',
        'loglog',
        'magnitude_spectrum',
        'pcolor',
        'pcolormesh',
        'phase_spectrum',
        'pie',
        'plot',
        'plot_date',
        'psd',
        'quiver',
        'quiverkey',
        'scatter',
        'semilogx',
        'semilogy',
        'specgram',
        # 'spy',
        'stackplot',
        'stem',
        'step',
        'streamplot',
        'tricontour',
        'tricontourf',
        'tripcolor',
        'triplot',
        'violinplot',
        'vlines',
        'xcorr',
        'barbs',
    )

    _misccommands = (
        'cla',
        'grid',
        'legend',
        'table',
        'text',
        'annotate',
        'ticklabel_format',
        'locator_params',
        'tick_params',
        'margins',
        'autoscale',
    )

    cmappable = {
        'contour': 'if %(ret)s._A is not None: sci(%(ret)s)',
        'contourf': 'if %(ret)s._A is not None: sci(%(ret)s)',
        'hexbin': 'sci(%(ret)s)',
        'scatter': 'sci(%(ret)s)',
        'pcolor': 'sci(%(ret)s)',
        'pcolormesh': 'sci(%(ret)s)',
        'hist2d': 'sci(%(ret)s[-1])',
        'imshow': 'sci(%(ret)s)',
        #'spy'    :  'sci(%(ret)s)',  ### may return image or Line2D
        'quiver': 'sci(%(ret)s)',
        'specgram': 'sci(%(ret)s[-1])',
        'streamplot': 'sci(%(ret)s.lines)',
        'tricontour': 'if %(ret)s._A is not None: sci(%(ret)s)',
        'tricontourf': 'if %(ret)s._A is not None: sci(%(ret)s)',
        'tripcolor': 'sci(%(ret)s)',
    }

    def format_value(value):
        """
        Format function default values as needed for inspect.formatargspec.
        The interesting part is a hard-coded list of functions used
        as defaults in pyplot methods.
        """
        if isinstance(value, types.FunctionType):
            if value.__name__ in ('detrend_none', 'window_hanning'):
                return '=mlab.' + value.__name__
            if value.__name__ == 'mean':
                return '=np.' + value.__name__
            raise ValueError(('default value %s unknown to boilerplate.' +
                             'formatvalue') % value)
        return '=' + repr(value)

    text_wrapper = textwrap.TextWrapper(break_long_words=False)

    for fmt, cmdlist in [(PLOT_TEMPLATE, _plotcommands),
                         (MISC_FN_TEMPLATE, _misccommands)]:
        for func in cmdlist:
            # For some commands, an additional line is needed to set the
            # color map
            if func in cmappable:
                mappable = '    ' + cmappable[func] % locals()
            else:
                mappable = ''

            # Get argspec of wrapped function
            base_func = getattr(Axes, func)
            has_data = 'data' in inspect.signature(base_func).parameters
            work_func = inspect.unwrap(base_func)

            (args, varargs, varkw, defaults, kwonlyargs, kwonlydefs,
                annotations) = inspect.getfullargspec(work_func)
            args.pop(0)  # remove 'self' argument
            defaults = tuple(defaults or ())

            # Add a data keyword argument if needed (fmt is PLOT_TEMPLATE) and
            # possible (if *args is used, we can't just add a data
            # argument in front of it since it would gobble one of the
            # arguments the user means to pass via *args)
            # This needs to be done here so that it goes into call
            if not varargs and fmt is PLOT_TEMPLATE and has_data:
                args.append('data')
                defaults = defaults + (None,)

            # How to call the wrapped function
            call = []
            for i, arg in enumerate(args):
                if len(defaults) < len(args) - i:
                    call.append('%s' % arg)
                else:
                    call.append('%s=%s' % (arg, arg))

            # remove the data keyword as it was needed above to go into the
            # call but should go after `hold` in the signature.
            # This is janky as all get out, but hopefully boilerplate will
            # be retired soon.
            if not varargs and fmt is PLOT_TEMPLATE and has_data:
                args.pop()
                defaults = defaults[:-1]

            if varargs is not None:
                call.append('*' + varargs)
            if varkw is not None:
                call.append('**' + varkw)
            call = ', '.join(call)

            text_wrapper.width = 80 - 19 - len(func)
            join_with = '\n' + ' ' * (18 + len(func))
            call = join_with.join(text_wrapper.wrap(call))

            if not varargs and fmt is PLOT_TEMPLATE and has_data:
                args.append('data')
                defaults = defaults + (None,)

            # Now we can build the argspec for defining the wrapper
            argspec = inspect.formatargspec(args, varargs, varkw, defaults,
                                            formatvalue=format_value)
            argspec = argspec[1:-1]  # remove parens

            text_wrapper.width = 80 - 5 - len(func)
            join_with = '\n' + ' ' * (5 + len(func))
            argspec = join_with.join(text_wrapper.wrap(argspec))

            # A gensym-like facility in case some function takes an
            # argument named washold, ax, or ret
            washold, ret, ax = 'washold', 'ret', 'ax'
            bad = {*args, varargs, varkw}
            while washold in bad or ret in bad or ax in bad:
                washold = 'washold' + str(random.randrange(10 ** 12))
                ret = 'ret' + str(random.randrange(10 ** 12))
                ax = 'ax' + str(random.randrange(10 ** 12))

            # Since we can't avoid using some function names,
            # bail out if they are used as argument names
            for reserved in ('gca', 'gci'):
                if reserved in bad:
                    msg = 'Axes method %s has kwarg named %s' % (func, reserved)
                    raise ValueError(msg)

            yield fmt % locals()

    cmaps = (
        'autumn',
        'bone',
        'cool',
        'copper',
        'flag',
        'gray',
        'hot',
        'hsv',
        'jet',
        'pink',
        'prism',
        'spring',
        'summer',
        'winter',
        'magma',
        'inferno',
        'plasma',
        'viridis',
        "nipy_spectral"
    )
    deprecated_cmaps = ("spectral", )
    # add all the colormaps (autumn, hsv, ....)
    for name in cmaps:
        yield CMAP_TEMPLATE.format(name=name)
    for name in deprecated_cmaps:
        yield CMAP_TEMPLATE_DEPRECATED.format(name=name)

    yield ''
    yield '_setup_pyplot_info_docstrings()'


def build_pyplot():
    pyplot_path = os.path.join(os.path.dirname(__file__), "..", 'lib',
                               'matplotlib', 'pyplot.py')

    pyplot_orig = open(pyplot_path, 'r').readlines()

    try:
        pyplot_orig = pyplot_orig[:pyplot_orig.index(PYPLOT_MAGIC_HEADER) + 1]
    except IndexError:
        raise ValueError('The pyplot.py file *must* have the exact line: %s' % PYPLOT_MAGIC_HEADER)

    pyplot = open(pyplot_path, 'w')
    pyplot.writelines(pyplot_orig)
    pyplot.write('\n')

    pyplot.writelines(boilerplate_gen())
    pyplot.write('\n')


if __name__ == '__main__':
    # Write the matplotlib.pyplot file
    build_pyplot()
