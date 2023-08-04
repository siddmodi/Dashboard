import sys
sys.path.append('C:\\Users\\Kailasa Capital\\Desktop\\Trial\\login')
from login import *

sys.path.append('C:\\Users\\Kailasa Capital\\Desktop\\Trial\\straddle graph 2\\Home')
from Home import *

import pandas as pd
import numpy as np
from datetime import date,datetime,time
import redis
import json
import time as tim
from time import sleep
import chart_studio
import streamlit as st 
import numpy as np 
import pandas as pd 
import plotly.express as px 
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import threading

import warnings
warnings.filterwarnings("ignore",category=FutureWarning)


logo =  Image.open("C:\\Users\\Kailasa Capital\\Desktop\\Trial\\straddle graph\\images\\Kailasa Favicon.png")

st.set_page_config(
    page_title = 'KAILASA CAPITAL',
    page_icon = logo,
    layout = 'wide'
)


##! FUNCTIONS ##
@st.cache_resource
def price_at_given_time(df_data,instrument,ce_strike,pe_strike,hour,minute):
    
    try:
        #! Try to extract the df for the given CE
        temp_df_ce = df_data.loc[(df_data['name']==instrument) & (df_data['strike']==int(ce_strike)) & (df_data['instrument_type']=='CE')]
        token_ce = temp_df_ce[temp_df_ce['expiry'] == temp_df_ce['expiry'].min()]['instrument_token'].iloc[0]
        df_ce = pd.DataFrame(kite.historical_data(instrument_token=token_ce,from_date = datetime.now().date(), to_date = datetime.now().date(), interval = 'minute'))
        df_ce['time'] = df_ce['date'].apply(lambda x: x.time())
        close_price_ce = df_ce[df_ce['time']==time(int(hour),int(minute))]['close'].iloc[0]
    except:
        #! If not available (input is 0), then give 0 value
        close_price_ce = 0

    try:
        #! Try to extract the df for the given PE
        temp_df_pe = df_data.loc[(df_data['name']==instrument) & (df_data['strike']==int(pe_strike)) & (df_data['instrument_type']=='PE')]
        token_pe = temp_df_pe[temp_df_pe['expiry'] == temp_df_pe['expiry'].min()]['instrument_token'].iloc[0]
        df_pe = pd.DataFrame(kite.historical_data(instrument_token=token_pe,from_date = datetime.now().date(), to_date = datetime.now().date(), interval = 'minute'))
        df_pe['time'] = df_pe['date'].apply(lambda x: x.time())
        close_price_pe = df_pe[df_pe['time']==time(int(hour),int(minute))]['close'].iloc[0]
    except:
        #! If not available (input is 0), then give 0 value
        close_price_pe = 0

    combo_price = round(close_price_ce + close_price_pe,2)

    col1, col2, col3, col4 = st.columns([1,1,1,1])
    if int(hour)<12:
        col1.metric(f'Time', f'{hour}:{minute} AM')
    else:
        col1.metric(f'Time', f'{hour}:{minute} PM')
    col2.metric(f'{instrument}{ce_strike}CE ', f'₹{close_price_ce}')
    col3.metric(f'{instrument}{pe_strike}PE ', f'₹{close_price_pe}')
    col4.metric(f'Combo',f'₹{combo_price}')

##! STREAMLIT ##

#! Basic UI

full_logo = Image.open("C:\\Users\\Kailasa Capital\\Desktop\\Trial\\straddle graph\\images\\Kailasa Full Logo.png")

col1, col2,col3 = st.columns([4, 2, 4])

with col1:
    st.write(' ')

with col2:     
    st.image(full_logo)  

with col3:
    st.write(' ')

placeholder = st.empty()


#! Basic Requirements
@st.cache_resource
def instruments_fun():
    df_data = pd.DataFrame(kite.instruments())
    return df_data

df_data = instruments_fun()

#! Form for fetching price at a given time
with st.form(key='Fetch Price Form'):
    st.markdown(f"<h1 style='text-align: center; color: white; font-size: 30px;'>Fetch Option Price</h1>", unsafe_allow_html=True)
    instrument_1_form_2 = st.radio("Select any one index",('Nifty', 'Banknifty', 'Finnifty'),key="horizontal_2").upper()

    strike_price_1_form_2 = st.text_input(label='CE Strike')
    strike_price_2_form_2 = st.text_input(label='PE Strike')

    hour_form_2 = st.text_input(label='Hour')
    minute_form_2 = st.text_input(label='Minute')

    submit_button_2 = st.form_submit_button(label='Submit')


##! Submit buttons for 3 forms ##


if submit_button_2:
    price_at_given_time(df_data,instrument_1_form_2,ce_strike = strike_price_1_form_2
                        ,pe_strike = strike_price_2_form_2,hour = hour_form_2, minute = minute_form_2)


