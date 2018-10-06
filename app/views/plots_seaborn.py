import hashlib
import os.path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import seaborn as sns
import calmap

from vega_datasets import data
from pandas.util import hash_pandas_object
from pyramid.view import view_config


APP_DIR = 'app'
PLOTS_DIR = 'app/cache/plots'
CACHE = False

PNG = 'PNG'
SVG = 'SVG'


def to_url(filename):
    if filename.startswith(APP_DIR + '/'):
        return filename[len(APP_DIR):]
    else:
        return filename


def inch(px):
    return px / 96


def get_plot_cache_basename(namespace, df, *args):
    df_str = hash_pandas_object(df).to_string()
    cache_key = '{}|{}|{}'.format(namespace, df_str, '|'.join([str(item) for item in args]))
    return hashlib.sha256(cache_key).hexdigest()


def get_plot_cache_path(namespace, df, format, *args):
    basename = get_plot_cache_basename(namespace, df, *args)
    extname = 'png' if format == PNG else 'svg'
    return '{}/{}.{}'.format(PLOTS_DIR, basename, extname)


def get_plot_cache(namespace, df, format, *args):
    path = get_plot_cache_path(namespace, df, format, *args)
    url = to_url(path)

    return (path, url, os.path.isfile(path))


def save_figure(fig, path, width=None, height=None):
    if width and height:
        fig.set_size_inches(inch(width), inch(height))

    fig.set_dpi(96)
    fig.set_tight_layout(True)
    fig.savefig(path)
    plt.close(fig)  # Garbage collection

    return True


def plot_iris_scatter(data, format=SVG, width=400, height=300, style='darkgrid'):
    path, url, has_cache = get_plot_cache('plot_iris_scatter', data, format, width, height, style)

    if has_cache:
        return url

    sns.set_style(style)
    ax = sns.scatterplot(x='petalLength', y='sepalLength', hue='species',
                         palette='Spectral', data=data)
    save_figure(ax.get_figure(), path, width, height)

    return url


def plot_year_heatmap(data, format=SVG, width=800, height=200, style='whitegrid'):
    path, url, has_cache = get_plot_cache('plot_year_heatmap', data, format, width, height, style)

    if has_cache:
        return url

    plt.style.use('seaborn-{}'.format(style))
    ax = calmap.yearplot(data, how=None, dayticks=(0, 2, 4, 6),
                         cmap='YlGn', fillcolor='#eeeeee')
    save_figure(ax.get_figure(), path, width, height)

    return url


def plot_calendar_heatmap(data, format=SVG, width=800, height=200, style='whitegrid'):
    path, url, has_cache = get_plot_cache(
        'plot_calendar_heatmap', data, format, width, height, style)

    if has_cache:
        return url

    plt.style.use('seaborn-{}'.format(style))
    fig, ax = calmap.calendarplot(data, how=None, dayticks=(0, 2, 4, 6),
                                  cmap='YlGn', fillcolor='#eeeeee')
    save_figure(fig, path, width, height)

    return url


class SeabornViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='plots_seaborn', renderer='plots_seaborn.jinja2')
    def index(self):
        """Render the plots"""
        plots = []

        np.random.seed(sum(map(ord, 'calmap')))
        all_days = pd.date_range('1/15/2014', periods=700, freq='D')
        days = np.sort(np.random.choice(all_days, 50))

        # Year heatmap
        events = pd.Series(np.random.randn(len(days)), index=days)
        url = plot_year_heatmap(events)
        plots.append({
            'title': 'Year heatmap',
            'url': url
        })

        # Calendar heatmap
        events = pd.Series(np.random.randn(len(days)), index=days)
        url = plot_calendar_heatmap(events)
        plots.append({
            'title': 'Calendar heatmap',
            'url': url
        })

        # Scatterplot
        df = data('iris')
        url = plot_iris_scatter(df)
        plots.append({
            'title': 'Scatterplot',
            'url': url
        })

        return {
            'plots': plots
        }
