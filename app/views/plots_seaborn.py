import hashlib
import os.path
import matplotlib
matplotlib.use('svg')
import matplotlib.pyplot as plt
import seaborn as sns


from vega_datasets import data
from pandas.util import hash_pandas_object
from pyramid.view import view_config


APP_DIR = 'app'
PLOTS_DIR = 'app/cache/plots'
CACHE = False

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
    extname = 'svg'  # TODO Derive from format
    return '{}/{}.{}'.format(PLOTS_DIR, basename, extname)


def get_plot_cache(namespace, df, format, *args):
    path = get_plot_cache_path(namespace, df, format, *args)
    url = to_url(path)

    return (path, url, os.path.isfile(path))


def save_plot(ax, path, width, height):
    fig = ax.get_figure()
    fig.set_size_inches(inch(width), inch(height))
    fig.set_dpi(96)
    fig.set_tight_layout(True)
    fig.savefig(path)
    plt.close(fig)  # Garbage collection

    return True


def plot_iris_scatter(df, format=SVG, width=400, height=300, style='darkgrid'):
    path, url, has_cache = get_plot_cache('plot_iris_scatter', df, format, width, height, style)

    if has_cache:
        return url

    sns.set_style(style)
    ax = sns.scatterplot(x='petalLength', y='sepalLength', hue='species',
                         palette='Spectral', data=df)
    save_plot(ax, path, width, height)

    return url


class SeabornViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='plots_seaborn', renderer='plots_seaborn.jinja2')
    def index(self):
        """Render the plots"""
        plots = []

        df = data('iris')
        url = plot_iris_scatter(df)
        plots.append({
            'title': 'Scatterplot',
            'url': url
        })

        return {
            'plots': plots
        }
