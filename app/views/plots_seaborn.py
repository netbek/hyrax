import numpy as np
import pandas as pd
import seaborn as sns
import calmap

from vega_datasets import data
from pyramid.view import view_config
from .helpers.constants import PNG, SVG
from .helpers.plots import sns_plot, mpl_plot


@sns_plot()
def plot_iris_scatter(data, width=400, height=300, format=SVG, style='darkgrid'):
    ax = sns.scatterplot(x='petalLength', y='sepalLength', hue='species',
                         palette='Spectral', data=data)
    return ax.get_figure(), width, height


@mpl_plot()
def plot_year_heatmap(data, width=800, height=200, format=SVG, style='whitegrid'):
    ax = calmap.yearplot(data, how=None, dayticks=(0, 2, 4, 6),
                         cmap='YlGn', fillcolor='#eeeeee')
    return ax.get_figure(), width, height


@mpl_plot()
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
