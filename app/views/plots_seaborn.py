import hashlib
import os.path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
import calmap

from functools import partial, wraps
from inspect import getargspec, formatargspec, stack
from vega_datasets import data
from pandas.util import hash_pandas_object
from pyramid.view import view_config


APP_DIR = 'app'
PLOTS_DIR = 'app/cache/plots'
CACHE = False

PNG = 'PNG'
SVG = 'SVG'

ALT = 'ALT'
MPL = 'MPL'
SNS = 'SNS'

MPL_STYLES = {
    'whitegrid': 'seaborn-whitegrid'
}


def to_url(filename):
    if filename.startswith(APP_DIR + '/'):
        return filename[len(APP_DIR):]
    else:
        return filename


def inch(px):
    return px / 96


def save_mpl_figure(fig, path, width=None, height=None):
    if width and height:
        fig.set_size_inches(inch(width), inch(height))

    fig.set_dpi(96)
    fig.set_tight_layout(True)
    fig.savefig(path)
    plt.close(fig)  # Garbage collection

    return True


def setup_plot(lib, cache=True):
    def decorator(func):
        @wraps(func)
        def wrapper(data, *args, **kwargs):
            argspec = getargspec(func)
            format = kwargs.get('format', argspec.defaults[-2])
            style = kwargs.get('style', argspec.defaults[-1])

            extname = 'png' if format == PNG else 'svg'
            cache_key = '{}|{}|{}|{}|{}'.format(
                func.__name__,
                hash_pandas_object(data).to_string(),
                format,
                '|'.join([str(value) for value in argspec.defaults]),
                '|'.join([str(value) for value in kwargs.values()]),
            )
            basename = hashlib.sha256(cache_key).hexdigest()
            path = '{}/{}.{}'.format(PLOTS_DIR, basename, extname)
            url = to_url(path)

            if not cache or not os.path.isfile(path):
                if lib == SNS:
                    with sns.axes_style(style):
                        figure, width, height = func(data, *args, **kwargs)
                        save_mpl_figure(figure, path, width, height)

                elif lib == MPL:
                    with plt.style.context(MPL_STYLES[style]):
                        figure, width, height = func(data, *args, **kwargs)
                        save_mpl_figure(figure, path, width, height)

            return path, url
        return wrapper
    return decorator


@setup_plot(SNS)
def plot_iris_scatter(data, width=400, height=300, format=SVG, style='darkgrid'):
    ax = sns.scatterplot(x='petalLength', y='sepalLength', hue='species',
                         palette='Spectral', data=data)
    return ax.get_figure(), width, height


@setup_plot(MPL)
def plot_year_heatmap(data, width=800, height=200, format=SVG, style='whitegrid'):
    ax = calmap.yearplot(data, how=None, dayticks=(0, 2, 4, 6),
                         cmap='YlGn', fillcolor='#eeeeee')
    return ax.get_figure(), width, height


@setup_plot(MPL)
def plot_calendar_heatmap(data, width=800, height=200, format=SVG, style='whitegrid'):
    fig, ax = calmap.calendarplot(data, how=None, dayticks=(0, 2, 4, 6),
                                  yearlabel_kws={'color': 'black',
                                                 'fontsize': 10, 'fontweight': 'normal'},
                                  cmap='YlGn', fillcolor='#eeeeee')
    return fig, width, height * len(data.index.year.unique())


class SeabornViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='plots_seaborn', renderer='plots_seaborn.jinja2')
    def index(self):
        """Render the plots"""
        plots = []

        np.random.seed(sum(map(ord, 'calmap')))
        all_days = pd.date_range('1/15/2014', periods=1200, freq='D')
        days = np.sort(np.random.choice(all_days, 50))

        # Year heatmap
        events = pd.Series(np.random.randn(len(days)), index=days)
        path, url = plot_year_heatmap(events)
        plots.append({
            'title': 'Year heatmap',
            'url': url
        })

        # Calendar heatmap
        events = pd.Series(np.random.randn(len(days)), index=days)
        path, url = plot_calendar_heatmap(events)
        plots.append({
            'title': 'Calendar heatmap',
            'url': url
        })

        # Scatterplot
        df = data('iris')
        path, url = plot_iris_scatter(df)
        plots.append({
            'title': 'Scatterplot',
            'url': url
        })

        return {
            'plots': plots
        }
