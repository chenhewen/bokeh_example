import time
import pandas as pd

from bokeh.io import output_file, show
from bokeh.layouts import row, column
from bokeh.models import HoverTool, ColumnDataSource, Slider, CustomJS
from bokeh.plotting import figure
from bokeh.sampledata.stocks import MSFT

color_red = '#F2583E'
color_black = '#D5E1DD'

if __name__ == '__main__':
    now = time.strftime("%Y%m%d%H%M%S", time.localtime())
    output_file("log_lines_%s.html" % (str(now)[0:17]))

    size = 50
    dataset = pd.DataFrame(MSFT)[:size]
    dataset.date_num = pd.to_datetime(dataset['date'])
    inc_flag_list = (dataset.close > dataset.open).tolist()
    source = ColumnDataSource(data=dict(
        date=dataset.date.tolist(),
        date_num=dataset.date_num.tolist(),
        close=dataset.close.tolist(),
        open=dataset.open.tolist(),
        high=dataset.high.tolist(),
        low=dataset.low.tolist(),
        fill_color=[color_red if i else color_black for i in inc_flag_list],
        alpha=[1 for i in range(size)]
    ))
    print(dataset.date)

    hover = HoverTool(tooltips=[
        ("date", "@date"),
        ("high", "@high"),
        ("low", "@low"),
        ("open", "@open"),
        ("close", "@close"),
    ])
    tools = [hover, 'crosshair,pan,wheel_zoom,box_zoom,zoom_in, xzoom_in, yzoom_in,zoom_out, xzoom_out, yzoom_out,reset,save']
    p = figure(x_axis_type='datetime', tools=tools, plot_width=1000, plot_height=650, toolbar_location="below")
    # p.segment(x0=dataset.date, y0=dataset.high, x1=dataset.date, y1=dataset.low, color='black', alpha=dataset.alpha)
    p.segment(x0="date_num", y0="high", x1="date_num", y1="low", color='black', source=source)
    w = 23 * 60 * 15000
    p.vbar(x="date_num", width=w, bottom="close", top="open", alpha="alpha",
           fill_color="fill_color", source=source, line_color='black')

    slider = Slider(start=0, end=1, value=0.7, step=.01, title='light')
    callback = CustomJS(args=dict(source=source, slider=slider), code="""
                const v = slider.value;
                for (var i = 0; i < source.data.alpha.length; i++) {
                    source.data.alpha[i] = v
                }
                source.change.emit();
            """)
    slider.js_on_change('value', callback)
    layout = row([p, column(slider)])
    show(layout)