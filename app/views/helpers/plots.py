import hashlib
import json
import os.path
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns

from functools import wraps
from inspect import getargspec
from pandas.util import hash_pandas_object
from StringIO import StringIO
from .constants import APP_DIR, PLOTS_DIR, PNG, SVG, MPL_STYLES


def to_url(filename):
    if filename.startswith(APP_DIR + '/'):
        return filename[len(APP_DIR):]
    else:
        return filename


def px_to_in(px):
    return px / 96


def to_vega(plot):
    return json.dumps(plot.to_dict(), indent=2)


def inline_svg(data):
    """Prepare SVG for inline use."""
    # Exclude comments and declarations before opening <svg> tag
    i = data.find('<svg')
    if ~i:
        return data[i:]
    else:
        return data

    # import re

    # return re.sub('\s+(?=<)', '', data)


def save_figure(fig, format, width=None, height=None, path=None):
    """Save Matplotlib or Seaborn figure."""
    if width and height:
        fig.set_size_inches(px_to_in(width), px_to_in(height))

    fig.set_dpi(96)
    fig.set_tight_layout(True)

    if path:
        fig.savefig(path, format=format)
        plt.close(fig)
        return path
    else:
        sio = StringIO()
        fig.savefig(sio, format=format)
        plt.close(fig)
        data = sio.getvalue()
        sio.close()

        if format == SVG:
            return inline_svg(data.decode('utf-8'))
        else:
            return data


def parse_plot_args(argspec, kwargs):
    style = kwargs.get('style', argspec.defaults[-3])
    format = kwargs.get('format', argspec.defaults[-2])
    cache = kwargs.get('cache', argspec.defaults[-1])

    return style, format, cache


def get_plot_cache(func_name, data, argspec, kwargs):
    style, format, cache = parse_plot_args(argspec, kwargs)
    extname = 'png' if format == PNG else 'svg'
    cache_key = '{}|{}|{}|{}|{}'.format(
        func_name,
        hash_pandas_object(data).to_string(),
        format,
        '|'.join([str(value) for value in argspec.defaults]),
        '|'.join([str(value) for value in kwargs.values()]),
    )
    basename = hashlib.sha256(cache_key).hexdigest()
    path = '{}/{}.{}'.format(PLOTS_DIR, basename, extname)
    url = to_url(path)
    has_cache = os.path.isfile(path)

    return path, url, has_cache


def alt_plot(func):
    @wraps(func)
    def wrapper(data, *args, **kwargs):
        p, width, height = func(data, *args, **kwargs)
        spec = to_vega(p)

        return spec
    return wrapper


def mpl_plot(func):
    @wraps(func)
    def wrapper(data, *args, **kwargs):
        argspec = getargspec(func)
        style, format, cache = parse_plot_args(argspec, kwargs)
        path, url, has_cache = get_plot_cache(func.__name__, data, argspec, kwargs)

        if not cache or not has_cache:
            with plt.style.context(MPL_STYLES[style]):
                fig, width, height = func(data, *args, **kwargs)
                save_figure(fig, format, width, height, path)

        return path, url
    return wrapper


def sns_plot(func):
    @wraps(func)
    def wrapper(data, *args, **kwargs):
        argspec = getargspec(func)
        style, format, cache = parse_plot_args(argspec, kwargs)
        path, url, has_cache = get_plot_cache(func.__name__, data, argspec, kwargs)

        if not cache or not has_cache:
            with sns.axes_style(style):
                fig, width, height = func(data, *args, **kwargs)
                save_figure(fig, format, width, height, path)

        return path, url
    return wrapper
