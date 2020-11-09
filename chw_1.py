import time
import pandas as pd

from bokeh.io import output_file, show
from bokeh.layouts import row, column
from bokeh.models import HoverTool, ColumnDataSource, Slider, CustomJS
from bokeh.plotting import figure
from bokeh.sampledata.stocks import MSFT

if __name__ == '__main__':
    now = time.strftime("%Y%m%d%H%M%S", time.localtime())
    output_file("log_lines_%s.html" % (str(now)[0:17]))

    size = 50
    dataset = pd.DataFrame(MSFT)[:size]
    dataset.date_num = pd.to_datetime(dataset['date'])

    source = ColumnDataSource(data=dict(
        date=dataset.date.tolist(),
        date_num=dataset.date_num.tolist(),
        close=dataset.close.tolist(),
        open=dataset.open.tolist(),
        high=dataset.high.tolist(),
        low=dataset.low.tolist(),
        alpha=[1 for i in range(size)]
    ))

    inc = dataset.close > dataset.open
    source_inc = ColumnDataSource(data=dict(
        date_num=dataset.date_num[inc].tolist(),
        inc_top=dataset.open[inc].tolist(),
        inc_bottom=dataset.close[inc].tolist(),
        alpha=[1 for i in range(len(dataset.open[inc]))]
    ))

    dec = dataset.close < dataset.open
    source_dec = ColumnDataSource(data=dict(
        date_num=dataset.date_num[dec].tolist(),
        dec_top=dataset.open[dec].tolist(),
        dec_bottom=dataset.close[dec].tolist(),
        alpha=[1 for i in range(len(dataset.open[dec]))]
    ))
    # print(dataset.date)

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
    p.segment(x0="date_num", y0="high", x1="date_num", y1="low", color='black', source=source, alpha="alpha")
    w = 23 * 60 * 15000
    p.vbar(x="date_num", width=w, bottom="inc_bottom", top="inc_top", alpha="alpha", source=source_inc, fill_color='#F2583E', line_color='black')  # 红色'#F2583E'
    p.vbar(x="date_num", width=w, bottom="dec_bottom", top="dec_top", alpha="alpha", source=source_dec, fill_color='#D5E1DD', line_color='black')

    slider = Slider(start=0, end=1, value=0.7, step=.01, title='light')
    callback = CustomJS(args=dict(source_inc=source_inc, source_dec=source_dec, slider=slider), code="""
                const v = slider.value;
                for (var i = 0; i < source_inc.data.alpha.length; i++) {
                    source_inc.data.alpha[i] = v
                }
                for (var i = 0; i < source_dec.data.alpha.length; i++) {
                    source_dec.data.alpha[i] = v
                }
                source_inc.change.emit();
                source_dec.change.emit();
                
            """)
    slider.js_on_change('value', callback)
    layout = row([p, column(slider)])
    show(layout)