import altair as alt
import numpy as np
import pandas as pd

from pprint import pprint
from bokeh.palettes import YlGn
from datetime import date
from uuid import uuid4
from pyramid.view import view_config
from .helpers.plots import to_vega


def _year_heatmap_df(data, fill_value=None):
    # Get subset series of first year's data
    subset = data.first('1A')

    # Make datetime index for each calendar day of subset
    subset_index = pd.date_range(
        start=pd.tseries.offsets.MonthBegin().rollback(subset.index.min()),
        end=pd.tseries.offsets.MonthEnd().rollforward(subset.index.max()),
        freq='D')

    # Add values missing from datetime index, if any
    subset = subset.resample('1D').sum().reindex(subset_index)

    if fill_value is not None:
        subset.fillna(fill_value, inplace=True)

    last_iso_week = date(subset_index.max().year, 12, 28).isocalendar()[1]

    # TODO Add tests
    def get_gregorian_week(index):
        iso_year, iso_week, iso_day = index.isocalendar()
        if iso_week == 1 and index.month > 1:
            return last_iso_week + 1
        elif iso_week >= last_iso_week and index.month < 12:
            return 0
        else:
            return iso_week

    subset_df = pd.DataFrame({'value': subset})
    subset_df['iso_week'] = subset_df.index.map(lambda index: index.isocalendar()[1])
    subset_df['gregorian_week'] = subset_df.index.map(get_gregorian_week)
    return subset_df


def get_year_heatmap(data, fill_value=None, date_format='%-d %b %Y', color_domain=None, color_range=None):
    df = _year_heatmap_df(data, fill_value=fill_value)
    # https://github.com/altair-viz/altair/issues/1027#issuecomment-408481253
    df['date'] = df.index.map(lambda index: index.strftime('%Y-%m-%dT%H:%M:%SZ'))
    df['color'] = pd.cut(df['value'], bins=color_domain, right=False, labels=color_range)
    return df.to_dict('records')


class CalHeatmapViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='plots_cal_heatmap', renderer='plots_cal_heatmap.jinja2')
    def index(self):
        """Render the plots"""
        plots = []

        np.random.seed(24)

        # Year heatmap
        days = pd.date_range('1/1/2016', periods=400, freq='D')
        rows = pd.Series(np.random.randint(0, 100, size=len(days)), index=days)

        domain = [0, 1, 25, 50, 100]
        range = ['#eee'] + YlGn[3][::-1]
        labels = ['0', '1-25', '25-50', '50-100']
        heatmap = get_year_heatmap(rows, fill_value=0, color_domain=domain, color_range=range)

        p = alt.LayerChart(alt.Data(values=heatmap)).configure_axis(grid=False).configure_legend(
            symbolType='square').configure_view(strokeWidth=0)

        # Plot without legend
        p += alt.Chart().mark_rect().encode(
            alt.Color('color:N', scale=alt.Scale(domain=range, range=range), legend=None),
            alt.X('iso_week:N', sort=None, axis=alt.Axis(
                title=None, ticks=False, offset=5, domain=False)),
            alt.Y('date:N', sort=['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
                  timeUnit='day', axis=alt.Axis(
                      format='%a', title=None, ticks=False, offset=5, domain=False)),
            tooltip=[alt.Tooltip(field='date', type='temporal', format='%-d %b %Y'), 'value:Q']
        )

        # Empty plot with legend
        p += alt.Chart(alt.Data(values=labels)).mark_rect().encode(
            alt.Color('color:N', scale=alt.Scale(domain=labels),
                      legend=alt.Legend(title='value', values=labels))
        )

        plots.append({
            'title': 'Year heatmap',
            'id': 'plot-{}'.format(uuid4()),
            'spec': to_vega(p)
        })

        return {
            'plots': plots
        }
