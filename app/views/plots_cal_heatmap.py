import altair as alt
import matplotlib as mpl
import numpy as np
import pandas as pd

from pprint import pprint
from bokeh.palettes import all_palettes
from uuid import uuid4
from pyramid.view import view_config

INF = float('inf')


def make_id():
    return 'plot-{}'.format(uuid4())


def discrete_palette(name, n=6, as_rgb=False):
    """
    Return a list of discrete colors.

    Resources:
    - https://bokeh.pydata.org/en/0.13.0/docs/reference/palettes.html
    - https://seaborn.pydata.org/generated/seaborn.color_palette.html
    - https://matplotlib.org/2.2.3/api/colors_api.html
    - https://gka.github.io/chroma.js
    - https://github.com/d3/d3-scale-chromatic
    """
    clamped_n = min(len(all_palettes[name]), max(3, n))
    palette = all_palettes[name][clamped_n][:n]

    if as_rgb:
        return [mpl.colors.to_rgb(v) for v in palette]
    else:
        return palette


def _label_bin(value, type='int'):
    if type == 'int':
        return str(int(value))
    elif type == 'float':
        return str(float(value))


def qcut_bins(data, q, precision=0, type='int', sep='-'):
    bin_values = pd.qcut(data, q, precision=precision).cat.categories.values
    bins = [(v.left, v.right) for v in bin_values]
    return make_bins(bins, type=type, sep=sep)


def make_bins(data, low=None, high=None, type='int', sep='-'):
    breaks = []
    labels = []
    count = len(data)

    for i, d in enumerate(data):
        if isinstance(d, (list, tuple)):
            left = low if d[0] == INF else d[0]
            if len(d) == 1:
                right = left
                label = _label_bin(left, type=type)
            else:
                right = high if d[1] == INF else d[1]
                if d[0] == INF:
                    label = '<= {}'.format(_label_bin(right, type=type))
                elif d[1] == INF:
                    label = '>= {}'.format(_label_bin(left, type=type))
                else:
                    label = '{}{}{}'.format(
                        _label_bin(left, type=type), sep, _label_bin(right, type=type))
        else:
            left = low if d == INF else d
            right = left
            label = _label_bin(left, type=type)

        breaks.append(left)
        if i == count-1:
            breaks.append(right+1)

        labels.append(label)

    return breaks, labels


def year_heatmap(data, palette='Viridis', bins=3, bin_labels=None, expand=False, fill_value=None, size=17, axis_offset=7, date_format='%-d %b %Y', value_title='value'):
    """Build a calendar heatmap (Altair/Vega)."""
    values = data.copy(deep=True)

    if isinstance(bins, int):
        color_breaks, color_labels = qcut_bins(data, bins)
    elif isinstance(bins, (list, tuple)):
        color_breaks = bins
        color_labels = bin_labels
    else:
        raise ValueError('"bins" must be int, list or tuple')

    if isinstance(palette, basestring):
        colors = discrete_palette(palette, len(color_labels))
    elif isinstance(palette, (list, tuple)):
        colors = palette
    else:
        raise ValueError('"palette" must be string, list or tuple')

    if expand:
        # Add missing days
        values = values.reindex(pd.date_range(
            start=pd.tseries.offsets.YearBegin().rollback(values.index.min()),
            end=pd.tseries.offsets.YearEnd().rollforward(values.index.max()),
            freq='D'))

    if fill_value is not None:
        values.fillna(fill_value, inplace=True)

    values = pd.DataFrame({
        'value': values,
        # https://github.com/altair-viz/altair/issues/1027#issuecomment-408481253
        'date': values.index.strftime('%Y-%m-%dT%H:%M:%SZ'),
        'color': pd.cut(values, bins=color_breaks, right=False, labels=colors)
    })

    # Number of unique weekdays
    y_count = values.index.dayofweek.nunique()

    # Add zero-based week number. We compute the value manually instead of using ISO week because
    # it's easier to handle date ranges over multiple years.
    week_start = values.index.to_period('W').start_time
    unique_week_start = list(week_start.unique())
    week = [unique_week_start.index(ts) for ts in week_start]
    values['week'] = week

    # Make labels for X axis. We operate on a narrower dataframe because it's more performant.
    x = pd.DataFrame({'week': week, 'week_start': week_start}, index=values.index)
    x_labels = x.groupby('week').first()
    x_labels['month'] = x_labels['week_start'].dt.strftime('%b')
    x_labels['year'] = x_labels['week_start'].dt.strftime('%Y')
    x_labels = x_labels.reset_index(level=0)
    x_labels['index'] = x_labels.index
    x_labels_mean = x_labels.groupby(['year', 'month'])['index'].mean().astype(int).get_values()
    x_labels.loc[~x_labels['index'].isin(x_labels_mean), 'month'] = ''
    x_labels = x_labels.loc[:, ['week', 'month']]

    # Prepare data for Vega
    values = values.to_dict('records')
    x_labels = x_labels.to_dict('records')

    # Container chart
    p = alt.LayerChart(alt.Data(values=values)).configure_axis(grid=False).\
        configure_legend(symbolType='square').configure_scale(rangeStep=size, textXRangeStep=size).\
        configure_view(strokeWidth=0)

    # Chart for data
    p += alt.Chart().mark_rect().encode(
        x=alt.X('week:N', sort=None, axis=None),
        y=alt.Y(
            'date:N', sort=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'], timeUnit='day',
            axis=alt.Axis(format='%a', title=None, ticks=False, offset=axis_offset, domain=False)),
        color=alt.Color('color:N', scale=alt.Scale(domain=colors, range=colors), legend=None),
        tooltip=[alt.Tooltip('date:T', format=date_format),
                 alt.Tooltip('value:Q', title=value_title)]
    )

    # Empty chart for legend
    p += alt.Chart(alt.Data(values=color_labels)).mark_rect().encode(
        color=alt.Color(
            'color:N', scale=alt.Scale(domain=color_labels),
            legend=alt.Legend(title=value_title, values=color_labels)))

    # Empty chart for X axis labels
    p += alt.Chart(alt.Data(values=x_labels)).mark_text(
        baseline='top', dy=axis_offset, tooltip='').encode(
        x=alt.X('week:N', sort=None, axis=None),
        y=alt.Y(value=size*y_count),
        text=alt.Text('month:N'))

    return p


class CalHeatmapViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='plots_cal_heatmap', renderer='plots_cal_heatmap.jinja2')
    def index(self):
        """Render the plots"""
        altair_plots = []

        np.random.seed(24)

        # Year heatmap
        partial_year_days = pd.date_range('6/10/2001', periods=20, freq='2D')
        multiple_years_days = pd.date_range('1/1/2001', periods=400, freq='D')

        rows = pd.Series(
            np.random.randint(0, 100, size=len(partial_year_days)), index=partial_year_days)
        p = year_heatmap(rows, bins=4, value_title='exercises')
        altair_plots.append({
            'title': 'Partial year heatmap with auto bins and labels (low=0, high=100, bins=4, expand=False, fill_value=None)',
            'id': make_id(),
            'spec': p.to_json()
        })

        # rows = pd.Series(
        #     np.random.randint(0, 100, size=len(partial_year_days)), index=partial_year_days)
        # palette = ['#ddd'] + discrete_palette('YlGn', 3)[::-1]
        # bins = [0, 1, 25, 50, 100]
        # bin_labels = label_bins(bins)
        # p = year_heatmap(
        #     rows, palette=palette, bins=bins, bin_labels=bin_labels, expand=True, value_title='exercises')
        # altair_plots.append({
        #     'title': 'Partial year heatmap with manual bins and auto labels (low=0, high=100, expand=True, fill_value=None)',
        #     'id': make_id(),
        #     'spec': p.to_json()
        # })

        # rows = pd.Series(
        #     np.random.randint(0, 100, size=len(partial_year_days)), index=partial_year_days)
        # palette = ['#ddd'] + discrete_palette('YlGn', 3)[::-1]
        # bins = [0, 1, 25, 50, 100]
        # bin_labels = label_bins(bins)
        # p = year_heatmap(
        #     rows, palette=palette, bins=bins, bin_labels=bin_labels, expand=True, fill_value=0, value_title='exercises')
        # altair_plots.append({
        #     'title': 'Partial year heatmap with manual bins and auto labels (low=0, high=100, expand=True, fill_value=0)',
        #     'id': make_id(),
        #     'spec': p.to_json()
        # })

        # rows = pd.Series(
        #     np.random.randint(0, 20, size=len(multiple_years_days)), index=multiple_years_days)
        # palette = ['#ddd'] + discrete_palette('YlGn', 3)[::-1]
        # bins = [0, 1, 25, 50, 100]
        # bin_labels = label_bins(bins)
        # p = year_heatmap(
        #     rows, palette=palette, bins=bins, bin_labels=bin_labels, value_title='exercises')
        # altair_plots.append({
        #     'title': 'Multiple year heatmap with manual bins and auto labels (low=0, high=20, expand=False, fill_value=None)',
        #     'id': make_id(),
        #     'spec': p.to_json()
        # })

        # rows = pd.Series(
        #     np.random.randint(0, 100, size=len(multiple_years_days)), index=multiple_years_days)
        # palette = ['#ddd'] + discrete_palette('YlGn', 3)[::-1]
        # bins = [0, 1, 25, 50, 100]
        # bin_labels = label_bins(bins)
        # p = year_heatmap(
        #     rows, palette=palette, bins=bins, bin_labels=bin_labels, value_title='exercises')
        # altair_plots.append({
        #     'title': 'Multiple year heatmap with manual bins and auto labels (low=0, high=100, expand=False, fill_value=None)',
        #     'id': make_id(),
        #     'spec': p.to_json()
        # })

        rows = pd.Series(
            np.random.randint(0, 110, size=len(multiple_years_days)), index=multiple_years_days)
        # palette = ['#ddd'] + discrete_palette('YlGn', 4)[::-1]
        # bins = [0, 1, 25, 50, 101, max(102, rows.max()+1)]
        # bin_labels = ['0', '1-25', '25-50', '50-100', '>100']
        # p = year_heatmap(
        #     rows, palette=palette, bins=bins, bin_labels=bin_labels, value_title='exercises')
        # altair_plots.append({
        #     'title': 'Multiple year heatmap with manual bins and labels (low=0, high=110, expand=False, fill_value=None)',
        #     'id': make_id(),
        #     'spec': p.to_json()
        # })

        breaks, labels = make_bins(
            [0, (1, 25), (25, 50), (50, 100), (101, INF)], high=rows.max())
        palette = ['#ddd'] + discrete_palette('YlGn', len(labels)-1)[::-1]

        p = year_heatmap(
            rows, palette=palette, bins=breaks, bin_labels=labels, value_title='exercises')
        altair_plots.append({
            'title': 'Multiple year heatmap with manual bins and labels (low=0, high=110, expand=False, fill_value=None)',
            'id': make_id(),
            'spec': p.to_json()
        })

        return {
            'plots': altair_plots
        }
