import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as colors

def main():
    st.set_page_config(layout="wide")   # will make page wide, but not plotly
    
    #st.write('Difference between max and min price per month')

    df = pd.read_csv('./data/monthly_BTC_USD.csv', comment='#')
    #st.write(df)
    #st.write(df.info(verbose=True))
    
    # converting data types
    df.drop(columns=['Adj Close', 'Volume'], inplace=True)
    df["open_time"] = pd.to_datetime(df["open_time"])
    df['month'] = pd.DatetimeIndex(df['open_time']).month
    df['month'] = df['month'].astype('category')
    df['year'] = pd.DatetimeIndex(df['open_time']).year
    df['year'] = df['year'].astype('category')
    #st.write(df.info(verbose=True))

    # add columns
    df['diff'] = df['high_price'] - df['low_price']
    df['diff_up'] = (df['high_price'] / df['low_price']) * 100 - 100
    df['diff_down'] = (df['low_price'] / df['high_price']) * 100 - 100
    df['status'] = np.where(df['open_price'] < df['close_price'], '+', '-')
    # show this in bar graph, possible with different colors for + and -
    df['diff_%'] = np.where(df['status'] == '+', df['diff_up'], df['diff_down'])    
    #st.dataframe(df)
    # st.dataframe(df, 
    #                 column_order=\
    #                     ['low_price', 'high_price', 'status', 'diff', 'diff_down', 'diff_up', 'diff_%'],
    #                 column_config={
    #                     "diff": st.column_config.NumberColumn(
    #                         format="$ %.0f",
    #                     )
    #                 },
    #             )

    

    min_date_value = datetime.date(2010, 7, 1) # min_date_value
    max_date_value = datetime.date.today() # max_date_value

    a = pd.to_datetime(min_date_value)
    halving_2012 = pd.to_datetime(datetime.date(2012, 11, 28))
    halving_2016 = pd.to_datetime(datetime.date(2016, 7, 6))
    halving_2020 = pd.to_datetime(datetime.date(2020, 5, 11))
    b = pd.to_datetime(max_date_value)

    predefined_date_ranges = {'Beginning': a,
                            'Halving 2012': halving_2012,
                            'Halving 2016': halving_2016,
                            'Halving 2020': halving_2020,
                            'End': b,}
    
    # Create a Streamlit web app
    st.title("Select start and end date")

    # Create a layout with two columns
    col1, col2 = st.columns(2)
    # Add the first date picker in the first column
    with col1:
        start_date = pd.to_datetime(st.date_input("Start Date", min_date_value, min_value=min_date_value, max_value=max_date_value))
        start_button = st.selectbox("Start:", list(predefined_date_ranges.keys()), index=None)

    # Add the second date picker in the second column
    with col2:
        end_date = pd.to_datetime(st.date_input("End Date", max_date_value, min_value=min_date_value, max_value=max_date_value))
        end_button = st.selectbox("End:", list(predefined_date_ranges.keys()), index=None)
    
    # DropDown
    if start_button:
        start_date = predefined_date_ranges[start_button] - datetime.timedelta(days=30)
    if end_button:
        end_date = predefined_date_ranges[end_button] + datetime.timedelta(days=30)

    # filter according to dates
    df = df[(df['open_time'] >= start_date) & (df['open_time'] <= end_date)]
    
    # Find the row with the minimum open_time
    min_open_time_row = df[df['open_time'] == df['open_time'].min()]
    month = min_open_time_row['month'].astype(str)
    year = min_open_time_row['year'].astype(str)
    min_data_point = f"{month.values[0]}/{year.values[0]}"
    # Find the row with the maximum open_time
    max_open_time_row = df[df['open_time'] == df['open_time'].max()]
    month = max_open_time_row['month'].astype(str)
    year = max_open_time_row['year'].astype(str)
    max_data_point = f"{month.values[0]}/{year.values[0]}"

    #
    # Bar chart
    #
    fig = px.bar(df, x='open_time', y='diff_%', color='diff',          
                text='diff',
                labels={'open_time':'Time',
                        'diff_%':'Change in %',
                        'diff':'Change in $'},
                title=f"Difference between min and max Bitcoin price per month from {min_data_point} to {max_data_point}")
    
    # Halving 2012-11-28
    if (halving_2012 >= start_date) and (halving_2012 <= end_date):
        fig.add_vline(x="2012-11-28", line_color="orange")
        fig.add_annotation(x="2012-11-28", y=.5, yref='paper', 
                        xanchor="left", text='Halving 2012', showarrow=False)

    # Halving 2016-07-06
    if (halving_2016 >= start_date) and (halving_2016 <= end_date):
        fig.add_vline(x="2016-07-06", line_color="orange")
        fig.add_annotation(x="2016-07-06", y=.5, yref='paper', 
                        xanchor="left", text='Halving 2016', showarrow=False)
    
    # Halving 2020-05-11
    if (halving_2020 >= start_date) and (halving_2020 <= end_date):
        fig.add_vline(x="2020-05-11", line_color="orange")
        fig.add_annotation(x="2020-05-11", y=.5, yref='paper', 
                        xanchor="left", text='Halving 2020', showarrow=False)
    
    #st.plotly_chart(fig)
    st.plotly_chart(fig, use_container_width=True)

    #
    # Histogram
    #
    fig = px.histogram(df, x="diff_%", nbins=50, color="status", 
                        marginal="violin",
                        labels={'diff_%':'Change in %',
                                'count':'Number of'},
                        title=f'Histogram of difference between min and max Bitcoin price as % per month from {min_data_point} to {max_data_point}')
    #fig.update_layout(
    #    yaxis_title="Custom Y-Axis Label",
    #    xaxis=dict(title="Custom X-Axis Label"))
    #st.plotly_chart(fig)
    st.plotly_chart(fig, use_container_width=True)
    
    #
    # YEAR MONTH
    #
    pivot_df = df.pivot(index='year', columns='month', values='diff_%')
    custom_colors = ['red', 'white', 'green']
    # Create the diverging color scale
    rg_gr = colors.make_colorscale(custom_colors)
    #rg_gr = colors.make_colorscale(custom_colors, [0, 0.4, 1])
    fig = px.imshow(pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index, text_auto=".2f", color_continuous_scale=rg_gr, 
            color_continuous_midpoint=0, aspect="auto")
    # color_continuous_midpoint=X, depend on right scale
    fig.update_layout(title=f'Bitcoin difference between min and max price per month from {min_data_point} to {max_data_point}')

    # Show all month numbers on x-axis
    month_numbers = list(pivot_df.columns)
    # Update the x-axis tick labels to show months as numbers
    fig.update_xaxes(tickvals=month_numbers, ticktext=month_numbers)

    year_numbers = list(pivot_df.index)
    fig.update_yaxes(tickvals=year_numbers, ticktext=year_numbers)
    
    #st.plotly_chart(fig)
    st.plotly_chart(fig, use_container_width=True)

    #
    # candle stick chart 
    #
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df['open_time'], 
                                open=df['open_price'], close=df['close_price'],
                                high=df['high_price'], low=df['low_price']
                                ))
    fig.update_layout(
        title='Monthly Bitcoin price',
        yaxis_title='in USDT',
        # this is line
        #shapes = [dict(
        #    x0='2020-05-11', x1='2020-05-11', y0=0, y1=1, xref='x', yref='paper',
        #    line_width=1, line_color='orange')],
        # this is text for line
        #annotations=[dict(
        #    x='2020-05-11', y=0.5, xref='x', yref='paper',
        #    showarrow=False, xanchor='left', text='Halving')]
        )
    
    # Halving 2012-11-28
    if (halving_2012 >= start_date) and (halving_2012 <= end_date):
        fig.add_vline(x="2012-11-28", line_color="orange")
        fig.add_annotation(x="2012-11-28", y=.5, yref='paper', 
                        xanchor="left", text='Halving 2012', showarrow=False)
        
    # Halving 2016-07-06
    if (halving_2016 >= start_date) and (halving_2016 <= end_date):
        fig.add_vline(x="2016-07-06", line_color="orange")
        fig.add_annotation(x="2016-07-06", y=.5, yref='paper', 
                        xanchor="left", text='Halving 2016', showarrow=False)
        
    # Halving 2020-05-11
    if (halving_2020 >= start_date) and (halving_2020 <= end_date):
        fig.add_vline(x="2020-05-11", line_color="orange")
        fig.add_annotation(x="2020-05-11", y=.5, yref='paper', 
                        xanchor="left", text='Halving 2020', showarrow=False)

    #st.plotly_chart(fig)
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()