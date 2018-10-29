import numpy as np
import pandas as pd
import seaborn as sns
import calmap

from vega_datasets import data
from pyramid.view import view_config
from .helpers.constants import PNG, SVG
from .helpers.plots import sns_plot, mpl_plot, save_figure


@sns_plot
def plot_iris_scatter(data, width=400, height=300, style='darkgrid', format=SVG, cache=True):
    ax = sns.scatterplot(x='petalLength', y='sepalLength', hue='species',
                         palette='Spectral', data=data)
    return ax.get_figure(), width, height


@mpl_plot
def plot_year_heatmap(data, width=800, height=200, style='whitegrid', format=SVG, cache=True):
    ax = calmap.yearplot(data, how=None, dayticks=(0, 2, 4, 6),
                         cmap='YlGn', fillcolor='#eeeeee')
    return ax.get_figure(), width, height


@mpl_plot
def plot_calendar_heatmap(data, width=800, height=200, style='whitegrid', format=SVG, cache=True):
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

        # np.random.seed(sum(map(ord, 'calmap')))
        # all_days = pd.date_range('1/15/2014', periods=1200, freq='D')
        # days = np.sort(np.random.choice(all_days, 50))

        # # Year heatmap
        # events = pd.Series(np.random.randn(len(days)), index=days)
        # path, url = plot_year_heatmap(events)
        # plots.append({
        #     'title': 'Year heatmap',
        #     'url': url
        # })

        # # Calendar heatmap
        # events = pd.Series(np.random.randn(len(days)), index=days)
        # path, url = plot_calendar_heatmap(events)
        # plots.append({
        #     'title': 'Calendar heatmap',
        #     'url': url
        # })

        # Boxplot
        df = data('flights-2k')

        first_5 = df['origin'].unique()[:5]
        df = df[df['origin'].isin(first_5)]

        df['date'] = pd.to_datetime(df['date'])
        df['weekday_abbr'] = df['date'].dt.strftime('%a')
        df['weekday_rank'] = df['date'].dt.weekday
        df.sort_values('weekday_rank', inplace=True)

        with sns.axes_style('whitegrid'):
            ax = sns.boxplot(x='weekday_abbr', y='delay', hue='origin', data=df,
                             dodge=True, linewidth=1, flierprops={'markersize': 5, 'marker': '.'})
            # ax = sns.swarmplot(x='weekday_abbr', y='delay', hue='origin', data=df,
            #                    dodge=True, color='.3', size=3)
            sns.despine(offset=10, trim=True)
            svg = save_figure(ax.get_figure(), SVG, 900, 450)

        # df = data('iris')

        # with sns.axes_style('whitegrid'):
        #     ax = sns.scatterplot(x='petalLength', y='sepalLength', hue='species',
        #                          palette='Spectral', data=df)
        #     svg = save_figure(ax.get_figure(), SVG, 400, 300)

        plots.append({
            'title': 'Scatterplot',
            'svg': svg
        })

        # Scatterplot
        # df = data('iris')
        # path, url = plot_iris_scatter(df)
        # plots.append({
        #     'title': 'Scatterplot',
        #     'url': url
        # })

        return {
            'plots': plots
        }
