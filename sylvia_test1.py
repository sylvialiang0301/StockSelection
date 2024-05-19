import streamlit as st
import pandas as pd
import numpy as np
import yahooquery as yq
import mplfinance as mpf
import matplotlib.pyplot as plt

# For data exporting
from io import BytesIO
import xlsxwriter
from pyxlsb import open_workbook as open_xlsb
from yahooquery import Ticker
from datetime import timedelta

from datetime import datetime
import pytz

def is_market_hours():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now(eastern)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close

#The last five quarterly EPS are all greater than expected.    
def eps_greater_than_expected(ticker):
    earnings = ticker.earning_history
    earnings['eps_greater'] = earnings.apply(compare_eps, axis=1)
    
    if (earnings['eps_greater'] == 'Yes').all():
        result= 'Passed'
    else:
        result= 'Failed'
                
    return result

def compare_eps(row):
    if row['epsActual'] > row['epsEstimate']:
        return 'Yes'
    else:
        return 'No'

#The past 50 days’ volume changing rate is between 0~3%. (The period is discussable)
def past_50_days_volume_change(ticker):
    if is_market_hours():
        price = ticker.history(period='51d')[:-1]
    else:
        price = ticker.history(period='50d')
    price['daily_change_rate']=price['volume'].pct_change()
    price=price.dropna()

    if (price['daily_change_rate'] <= 0.03).all():
        result= 'Passed'
    else:
        result= 'Failed'
                
    return result

#The stock price >= $12.
def stock_price_greater_12(ticker):
    price = ticker.history()
    current_stock_price= price.iloc[-1]['close']
    
    if current_stock_price >= 12:
        result= 'Passed'
    else:
        result= 'Failed'               
    return result

#The current price change from 52wk high >= -15%.
          
# def price_change_52wk(stock):
#     ticker = Ticker(stock)
#     price_change=ticker.key_stats[stock]['52WeekChange']

#     if price_change>= -0.15:
#         result= 'Passed'
#     else:
#         result= 'Failed'                
#     return result

def price_change_52wk(stock):
    ticker = Ticker(stock)
    modules = 'assetProfile earnings defaultKeyStatistics'

    price_change=ticker.get_modules(modules)[stock]['defaultKeyStatistics']['52WeekChange']

    if price_change>= -0.15:
        result= 'Passed'
    else:
        result= 'Failed'                
    return result

#The past 50 days' average volume >= 2000k. (The period is discussable)
def past_50_days_avg_volume(ticker):
    if is_market_hours():
        price = ticker.history(period='51d')[:-1]
    else:
        price = ticker.history(period='50d')
        
    avg_volume=price['volume'].mean()

    if avg_volume>= 2000000:
        result= 'Passed'
    else:
        result= 'Failed'
                
    return result

#The current price > MA20
def cur_price_ma20(ticker):
    
    if is_market_hours():
        price = ticker.history(period='21d')[:-1]
    else:
        price = ticker.history(period='20d')

    current_stock_price= price.iloc[-1]['close']
    ma20=price['close'].mean()
    
    if current_stock_price >= ma20:
        result= 'Passed'
    else:
        result= 'Failed'               
    return result

#MA10 > MA50
def ma10_ma50(ticker):
    if is_market_hours():
        price = ticker.history(period='51d')[:-1]
    else:
        price = ticker.history(period='50d')

    ma10=price[-10:]['close'].mean()
    ma50=price['close'].mean()
    
    if ma10 >= ma50:
        result= 'Passed'
    else:
        result= 'Failed'               
    return result

#MA20 > MA200
def ma20_ma200(ticker):
    if is_market_hours():
        price = ticker.history(period='201d')[:-1]
    else:
        price = ticker.history(period='200d')
    ma20=price[-20:]['close'].mean()
    ma200=price['close'].mean()
    
    if ma20 >= ma200:
        result= 'Passed'
    else:
        result= 'Failed'               
    return result

#MA50 > MA200
def ma50_ma200(ticker):
    if is_market_hours():
        price = ticker.history(period='201d')[:-1]
    else:
        price = ticker.history(period='200d')
    ma50=price[-50:]['close'].mean()
    ma200=price['close'].mean()
    
    if ma50 >= ma200:
        result= 'Passed'
    else:
        result= 'Failed'               
    return result

# def plot_candlestick(stock):
#     ticker = Ticker(stock)
#     if is_market_hours():
#         price = ticker.history(period='21d')[:-1]
#     else:
#         price = ticker.history(period='20d')
    
#     price=price.reset_index()
#     price['date'] = pd.to_datetime(price['date'])
    
#     price=price.set_index('date')
#     plot=mpf.plot(price, type='candle', style='charles')

#     return plot

def plot_candlestick(stock):
    ticker = Ticker(stock)
    if is_market_hours():
        price = ticker.history(period='21d')[:-1]
    else:
        price = ticker.history(period='20d')

    price = price.reset_index()
    price['date'] = pd.to_datetime(price['date'])
    price = price.set_index('date')
    
    fig, ax = plt.subplots()
    mpf.plot(price, type='candle', style='charles', ax=ax)

    return fig

#['The current price change from 52wk high >= -15%.', price_change_52wk(stock)],

def stock_selection(stock):
    ticker = Ticker(stock)
    
    data = np.array([['The last five quarterly EPS are all greater than expected.', eps_greater_than_expected(ticker)],
                    ['The past 50 days’ volume changing rate is between 0~3%.', past_50_days_volume_change(ticker)],
                    ['The stock price >= $12.', stock_price_greater_12(ticker)],
                    ['The past 50 days avg volume >= 2000k. ', past_50_days_avg_volume(ticker)],
                    ['The current price > MA20.', cur_price_ma20(ticker)],
                    ['MA10 > MA50.', ma10_ma50(ticker)],
                    ['MA20 > MA200.', ma20_ma200(ticker)],
                    ['MA50 > MA200.', ma50_ma200(ticker)],
                    ])
    df = pd.DataFrame(data, columns=['Criteria', 'Result'])
    
    #df.to_excel('stock_selection_result.xlsx', index=False, engine='xlsxwriter')

    return df
#print(stock_selection('aapl'))

# Page setup
st.set_page_config(  # Alternate names: setup_page, page, layout
layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
page_title='Stock Selection System',  # String or None. Strings get appended with "• Streamlit".
page_icon='jams_icon.ico',  # String, anything supported by st.image, or None.
)
image_url = "https://i.imgur.com/cnx9XYd.png"
st.image(image_url, output_format="PNG", width=200)
header = '<p style="font-family:Times New Roman; color:black; font-size: 30px;">Stock Selection System</p>'
st.markdown(header, unsafe_allow_html=True)

stock = st.text_input('Enter company\'s ticker:')


fetch_button = st.button('Check')
if fetch_button:
    st.subheader('Stock Data:')
    df = stock_selection(stock)  # Make sure you have this function defined somewhere
    st.dataframe(df)

    st.subheader('Stock Price Trend:')
    fig = plot_candlestick(stock)
    st.pyplot(fig)

# plot = None

# fetch_button = st.button('Check')
# if fetch_button:
#     st.subheader('Stock Data:')
#     df=stock_selection(stock)
#     st.dataframe(df)

#     st.subheader('Stock Price Trend:')
#     plot=plot_candlestick(stock)
#     st.pyplot(plot)
#     plot=plot_candlestick(stock)

# # Display DataFrame
# st.subheader('Stock Data:')
# st.dataframe(df)
    
# # Display Plot
# st.subheader('Stock Price Trend:')
# st.pyplot(plot)

# Display rights
def load_css(file_name):
     with open(file_name) as f:
         st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
load_css('example.css')
# Footer
st.markdown(
    """
    <div class="footer">
        Developed by JAMS Investment. All rights reserved. Version 2 2024.5
    </div>
    """,
    unsafe_allow_html=True
)
