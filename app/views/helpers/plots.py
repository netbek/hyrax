import hashlib
import json
import os.path
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns

from functools import partial, wraps
from inspect import getargspec
from pandas.util import hash_pandas_object
from .constants import APP_DIR, PLOTS_DIR, PNG, SVG, MPL_STYLES


def to_url(filename):
    if filename.startswith(APP_DIR + '/'):
        return filename[len(APP_DIR):]
    else:
        return filename


def inch(px):
    return px / 96


def to_vega(plot):
    return json.dumps(plot.to_dict(), indent=2)


def save_mpl_figure(path, fig, width=None, height=None):
    if width and height:
        fig.set_size_inches(inch(width), inch(height))

    fig.set_dpi(96)
    fig.set_tight_layout(True)
    fig.savefig(path)
    plt.close(fig)  # Garbage collection

    return True


def parse_args(argspec, kwargs):
    format = kwargs.get('format', argspec.defaults[-2])
    style = kwargs.get('style', argspec.defaults[-1])
    return format, style


def get_cache(func_name, data, argspec, kwargs):
    format, style = parse_args(argspec, kwargs)
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


def sns_plot(cache=True):
    def decorator(func):
        @wraps(func)
        def wrapper(data, *args, **kwargs):
            argspec = getargspec(func)
            format, style = parse_args(argspec, kwargs)
            path, url, has_cache = get_cache(func.__name__, data, argspec, kwargs)

            if not cache or not has_cache:
                with sns.axes_style(style):
                    fig, width, height = func(data, *args, **kwargs)
                    save_mpl_figure(path, fig, width, height)

            return path, url
        return wrapper
    return decorator


def mpl_plot(cache=True):
    def decorator(func):
        @wraps(func)
        def wrapper(data, *args, **kwargs):
            argspec = getargspec(func)
            format, style = parse_args(argspec, kwargs)
            path, url, has_cache = get_cache(func.__name__, data, argspec, kwargs)

            if not cache or not has_cache:
                with plt.style.context(MPL_STYLES[style]):
                    fig, width, height = func(data, *args, **kwargs)
                    save_mpl_figure(path, fig, width, height)

            return path, url
        return wrapper
    return decorator
