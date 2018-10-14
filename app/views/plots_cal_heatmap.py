import altair as alt
import numpy as np
import pandas as pd

from pprint import pprint
from bokeh.palettes import YlGn
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
        start = bins[i]
        end = bins[i + 1]
        if end - start == 1:
            labels.append(str(start))
            if i == stop - 1:
                labels.append(str(end))
        else:
            labels.append('{}{}{}'.format(str(start), separator, str(end)))
    return labels


def plot_year_heatmap(data, bins, palette, legend_labels, expand=False, fill_value=None, size=17, tooltip_date_format='%-d %b %Y'):
    # Get subset series of first year's data
    subset = data.first('1A')

    if expand:
        # Make datetime index for each calendar day of subset
        subset_index = pd.date_range(
            start=pd.tseries.offsets.YearBegin().rollback(subset.index.min()),
            end=pd.tseries.offsets.YearEnd().rollforward(subset.index.max()),
            freq='D')

        # Add missing datetime index, if any
        subset = subset.resample('1D').sum(min_count=1).reindex(subset_index)

    if fill_value is not None:
        subset.fillna(fill_value, inplace=True)

    subset_df = pd.DataFrame({'value': subset})
    subset_df['week'] = subset_df.index.map(lambda index: index.isocalendar()[1])

    # last_iso_week = date(subset_index.max().year, 12, 28).isocalendar()[1]
    # def get_gregorian_week(index):
    #     iso_year, iso_week, iso_day = index.isocalendar()
    #     if iso_week == 1 and index.month > 1:
    #         return last_iso_week + 1
    #     elif iso_week >= last_iso_week and index.month < 12:
    #         return 0
    #     else:
    #         return iso_week
    # subset_df['week'] = subset_df.index.map(get_gregorian_week)

    # https://github.com/altair-viz/altair/issues/1027#issuecomment-408481253
    subset_df['date'] = subset_df.index.strftime('%Y-%m-%dT%H:%M:%SZ')
    subset_df['color'] = pd.cut(subset_df['value'], bins=bins, right=False, labels=palette)

    # X axis labels
    x = subset_df.groupby('week').first().sort_values('date').loc[:, ['date']]
    x['month'] = pd.to_datetime(x['date']).dt.strftime('%b')
    x = x.reset_index(level=0).loc[:, ['week', 'month']]
    x['index'] = x.index
    x_mean_index = x.groupby('month')['index'].mean().astype(int).get_values()
    x.loc[~x['index'].isin(x_mean_index), 'month'] = ''
    x = x.loc[:, ['week', 'month']]

    # Prepare data for Vega
    subset_values = subset_df.to_dict('records')
    x_labels = x.to_dict('records')

    # Make container chart
    chart = alt.LayerChart(alt.Data(values=subset_values)).configure_axis(grid=False).\
        configure_legend(symbolType='square').\
        configure_scale(rangeStep=size, textXRangeStep=size).configure_view(strokeWidth=0)

    # Add chart for data
    chart += alt.Chart().mark_rect().encode(
        alt.Color('color:N', scale=alt.Scale(domain=palette, range=palette), legend=None),
        # alt.X('week:N', sort=None, axis=alt.Axis(
        #     title=None, ticks=False, offset=5, domain=False)),
        alt.X('week:N', sort=None, axis=None),
        alt.Y('date:N', sort=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
              timeUnit='day', axis=alt.Axis(
                  format='%a', title=None, ticks=False, offset=5, domain=False)),
        tooltip=[alt.Tooltip(field='date', type='temporal', format=tooltip_date_format), 'value:Q']
    )

    # Add empty chart for legend
    chart += alt.Chart(alt.Data(values=legend_labels)).mark_rect().encode(
        alt.Color('color:N', scale=alt.Scale(domain=legend_labels),
                  legend=alt.Legend(title='value', values=legend_labels)))

    # Add empty chart for X axis labels
    # chart += alt.Chart(alt.Data(values=x_labels)).mark_text(
    #     dy=-10, fontSize=10, tooltip='').encode(
    #         alt.X('week:N', sort=None, axis=None), alt.Y(value=0), alt.Text('month:N'))
    chart += alt.Chart(alt.Data(values=x_labels)).mark_text(
        baseline='top', dy=7, fontSize=10, tooltip='').encode(
            alt.X('week:N', sort=None, axis=None), alt.Y(value=size*7), alt.Text('month:N'))

    return chart


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
        multiple_years_days = pd.date_range('1/1/2016', periods=400, freq='D')

        rows = pd.Series(np.random.randint(0, 100, size=len(partial_year_days)),
                         index=partial_year_days)
        bins = [0, 1, 25, 50, 100]
        palette = ['#eee'] + YlGn[3][::-1]
        legend_labels = get_bin_labels(bins)
        p = plot_year_heatmap(rows, bins, palette, legend_labels)
        plots.append({
            'title': 'Year heatmap with partial data, semi-auto bin labels (expand=False, fill_value=None, low=0, high=100)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        rows = pd.Series(np.random.randint(0, 100, size=len(partial_year_days)),
                         index=partial_year_days)
        bins = [0, 1, 25, 50, 100]
        palette = ['#eee'] + YlGn[3][::-1]
        legend_labels = get_bin_labels(bins)
        p = plot_year_heatmap(rows, bins, palette, legend_labels, expand=True)
        plots.append({
            'title': 'Year heatmap with partial data, semi-auto bin labels (expand=True, fill_value=None, low=0, high=100)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        rows = pd.Series(np.random.randint(0, 100, size=len(partial_year_days)),
                         index=partial_year_days)
        bins = [0, 1, 25, 50, 100]
        palette = ['#eee'] + YlGn[3][::-1]
        legend_labels = get_bin_labels(bins)
        p = plot_year_heatmap(rows, bins, palette, legend_labels, expand=True, fill_value=0)
        plots.append({
            'title': 'Year heatmap with partial data, semi-auto bin labels (expand=True, fill_value=0, low=0, high=100)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        rows = pd.Series(np.random.randint(0, 20, size=len(multiple_years_days)),
                         index=multiple_years_days)
        bins = [0, 1, 25, 50, 100]
        palette = ['#eee'] + YlGn[3][::-1]
        legend_labels = get_bin_labels(bins)
        p = plot_year_heatmap(rows, bins, palette, legend_labels)
        plots.append({
            'title': 'Year heatmap with semi-auto bin labels (expand=False, fill_value=None, low=0, high=20)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        rows = pd.Series(np.random.randint(0, 100, size=len(multiple_years_days)),
                         index=multiple_years_days)
        bins = [0, 1, 25, 50, 100]
        palette = ['#eee'] + YlGn[3][::-1]
        legend_labels = get_bin_labels(bins)
        p = plot_year_heatmap(rows, bins, palette, legend_labels)
        plots.append({
            'title': 'Year heatmap with semi-auto bin labels (expand=False, fill_value=None, low=0, high=100)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        rows = pd.Series(np.random.randint(0, 110, size=len(multiple_years_days)),
                         index=multiple_years_days)
        bins = [0, 1, 25, 50, 101, rows.max()+1]
        palette = ['#eee'] + YlGn[4][::-1]
        legend_labels = ['0', '1-25', '25-50', '50-100', '>100']
        p = plot_year_heatmap(rows, bins, palette, legend_labels)
        plots.append({
            'title': 'Year heatmap with manual bin labels (expand=False, fill_value=None, low=0, high=110)',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        return {
            'plots': plots
        }
