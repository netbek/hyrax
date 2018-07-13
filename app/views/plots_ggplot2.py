import hashlib
import os.path
import altair as alt
from vega_datasets import data
from pandas.util import hash_pandas_object
from pygg import *
from pyramid.view import view_config


APP_DIR = 'app'
PLOTS_DIR = 'app/cache/plots'
CACHE = False


def to_url(filename):
    if filename.startswith(APP_DIR + '/'):
        return filename[len(APP_DIR):]
    return filename


def inch(px):
    return px / 96


def plot_iris_scatter(df, width=400, height=200):
    # TODO Abstract render cache
    function = 'plot_iris_scatter'
    df_hash = hash_pandas_object(df).to_string()
    basename = hashlib.sha256('{}-{}-{}-{}'.format(function, df_hash, width, height)).hexdigest()
    filename = '{}/{}.png'.format(PLOTS_DIR, basename)

    if CACHE and os.path.isfile(filename):
        return to_url(filename)

    p = ggplot(df, aes(x='petalLength', y='sepalLength', fill='species')) + \
        geom_point(size=1, alpha=0.5) + \
        scale_fill_brewer(palette='"Spectral"') + \
        expand_limits(x=0, y=0)

    ggsave(filename, p, dpi=96, width=inch(width), height=inch(height))

    return to_url(filename)


def plot_iris_histogram(df, width=400, height=200):
    # TODO Abstract render cache
    function = 'plot_iris_histogram'
    df_hash = hash_pandas_object(df).to_string()
    basename = hashlib.sha256('{}-{}-{}-{}'.format(function, df_hash, width, height)).hexdigest()
    filename = '{}/{}.png'.format(PLOTS_DIR, basename)

    if CACHE and os.path.isfile(filename):
        return to_url(filename)

    p = ggplot(df, aes(x='petalLength', fill='species')) + \
        geom_histogram(aes(y='..density..'), binwidth=0.2) + \
        geom_density(stat='"density"', alpha=0.5) + \
        scale_fill_brewer(palette='"Set1"')

    ggsave(filename, p, dpi=96, width=inch(width), height=inch(height))

    return to_url(filename)


class Ggplot2Views:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='plots_ggplot2', renderer='plots_ggplot2.jinja2')
    def index(self):
        """Render the plots"""
        plots = []

        df = data('iris')
        url = plot_iris_scatter(df)
        plots.append({
            'title': 'Scatterplot',
            'url': url
        })

        df = data('iris')
        url = plot_iris_histogram(df)
        plots.append({
            'title': 'Histogram',
            'url': url
        })

        return {
            'plots': plots
        }
