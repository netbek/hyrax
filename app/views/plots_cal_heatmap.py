import altair as alt
import numpy as np
import pandas as pd

from pprint import pprint
from bokeh.palettes import viridis, YlGn
from datetime import date, datetime
from uuid import uuid4
from pyramid.view import view_config
from .helpers.plots import to_vega


def get_bin_labels(bins, separator='-'):
    if not bins:
        return []

    count = len(bins)

    if count == 1:
        return [str(bins[0])]

    labels = []
    stop = count - 1
    for i in range(stop):
        left = bins[i]
        right = bins[i + 1]
        if right - left == 1:
            labels.append(str(left))
            if i == stop - 1:
                labels.append(str(right))
        else:
            labels.append('{}{}{}'.format(str(left), separator, str(right)))
    return labels


def format_label(value, type='int'):
    if type == 'int':
        return str(int(value))
    elif type == 'float':
        return str(float(value))
    else:
        return str(value)


def make_bins_and_labels(values, quantiles, precision=0, type='int', separator='-'):
    bin_values = pd.qcut(values, quantiles, precision=precision).cat.categories.values
    bins = [v.left for v in bin_values]
    bins.append(bin_values[-1].right)

    labels = ['{}{}{}'.format(
        format_label(v.left, type), separator, format_label(v.right, type)) for v in bin_values]

    return bins, labels


def year_heatmap(data, bins, palette, legend_labels, expand=False, fill_value=None, size=17, axis_offset=7, date_format='%-d %b %Y', value_title='value'):
    """Build a calendar heatmap (Altair/Vega)."""
    values = data.copy(deep=True)

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
        'color': pd.cut(values, bins=bins, right=False, labels=palette)
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
        alt.Color('color:N', scale=alt.Scale(domain=palette, range=palette), legend=None),
        alt.X('week:N', sort=None, axis=None),
        alt.Y('date:N', sort=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'], timeUnit='day',
              axis=alt.Axis(format='%a', title=None, ticks=False,
                            offset=axis_offset, domain=False)),
        tooltip=[alt.Tooltip('date:T', format=date_format),
                 alt.Tooltip('value:Q', title=value_title)]
    )

    # Empty chart for legend
    p += alt.Chart(alt.Data(values=legend_labels)).mark_rect().encode(
        alt.Color('color:N', scale=alt.Scale(domain=legend_labels),
                  legend=alt.Legend(title=value_title, values=legend_labels)))

    # Empty chart for X axis labels
    p += alt.Chart(alt.Data(values=x_labels)).mark_text(
        baseline='top', dy=axis_offset, tooltip='').encode(
            alt.X('week:N', sort=None, axis=None), alt.Y(value=size*y_count),
            alt.Text('month:N'))

    return p


class CalHeatmapViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='plots_cal_heatmap', renderer='plots_cal_heatmap.jinja2')
    def index(self):
        """Render the plots"""
        plots = []

        np.random.seed(24)

        # Year heatmap
        partial_year_days = pd.date_range('6/10/2016', periods=10, freq='2D')
        multiple_years_days = pd.date_range('6/10/2016', periods=400, freq='D')

        rows = pd.Series(np.random.randint(0, 100, size=len(partial_year_days)),
                         index=partial_year_days)

        quantiles = 5
        bins, legend_labels = make_bins_and_labels(rows, quantiles)
        palette = viridis(quantiles)

        p = year_heatmap(rows, bins, palette, legend_labels)
        plots.append({
            'title': 'Year heatmap with partial data, semi-auto bin labels (expand=False, fill_value=None, low=0, high=100)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        rows = pd.Series(np.random.randint(0, 100, size=len(partial_year_days)),
                         index=partial_year_days)
        bins = [0, 1, 25, 50, 100]
        palette = ['#ddd'] + YlGn[3][::-1]
        legend_labels = get_bin_labels(bins)
        p = year_heatmap(rows, bins, palette, legend_labels, expand=True)
        plots.append({
            'title': 'Year heatmap with partial data, semi-auto bin labels (expand=True, fill_value=None, low=0, high=100)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        rows = pd.Series(np.random.randint(0, 100, size=len(partial_year_days)),
                         index=partial_year_days)
        bins = [0, 1, 25, 50, 100]
        palette = ['#ddd'] + YlGn[3][::-1]
        legend_labels = get_bin_labels(bins)
        p = year_heatmap(rows, bins, palette, legend_labels, expand=True, fill_value=0)
        plots.append({
            'title': 'Year heatmap with partial data, semi-auto bin labels (expand=True, fill_value=0, low=0, high=100)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        rows = pd.Series(np.random.randint(0, 20, size=len(multiple_years_days)),
                         index=multiple_years_days)
        bins = [0, 1, 25, 50, 100]
        palette = ['#ddd'] + YlGn[3][::-1]
        legend_labels = get_bin_labels(bins)
        p = year_heatmap(rows, bins, palette, legend_labels)
        plots.append({
            'title': 'Year heatmap with semi-auto bin labels (expand=False, fill_value=None, low=0, high=20)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        rows = pd.Series(np.random.randint(0, 100, size=len(multiple_years_days)),
                         index=multiple_years_days)
        bins = [0, 1, 25, 50, 100]
        palette = ['#ddd'] + YlGn[3][::-1]
        legend_labels = get_bin_labels(bins)
        p = year_heatmap(rows, bins, palette, legend_labels)
        plots.append({
            'title': 'Year heatmap with semi-auto bin labels (expand=False, fill_value=None, low=0, high=100)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        rows = pd.Series(np.random.randint(0, 110, size=len(multiple_years_days)),
                         index=multiple_years_days)
        bins = [0, 1, 25, 50, 101, rows.max()+1]
        palette = ['#ddd'] + YlGn[4][::-1]
        legend_labels = ['0', '1-25', '25-50', '50-100', '>100']
        p = year_heatmap(rows, bins, palette, legend_labels)
        plots.append({
            'title': 'Year heatmap with manual bin labels (expand=False, fill_value=None, low=0, high=110)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        return {
            'plots': plots
        }
