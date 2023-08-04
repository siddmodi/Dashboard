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
def price_at_given_time_form_3(df_data,instrument,ce_strike,pe_strike,hour,minute):
    
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

    combo_price = close_price_ce + close_price_pe
    return close_price_ce,close_price_pe,combo_price


@st.cache_resource
def calculate_sl(instrument,single_leg_or_comb,custom_price_or_fetch_price,short_or_long,sl_perc,ce_price,pe_price,   hour,minute,ce_strike,pe_strike):
    if custom_price_or_fetch_price == 'Custom Price':
        combo_price = float(ce_price) + float(pe_price)

    elif custom_price_or_fetch_price == 'Fetch Price':
        #! Calculate price at specific time using historical API
        df_data = pd.DataFrame(kite.instruments())
        ce_price,pe_price,combo_price = price_at_given_time_form_3(df_data,instrument,ce_strike,pe_strike,hour,minute)
        

    if single_leg_or_comb == 'Single Leg':
        if short_or_long == 'Short':
            sl_ce = float(ce_price)*(1+(float(sl_perc)/100))
            sl_pe = float(pe_price)*(1+(float(sl_perc)/100))
        if short_or_long == 'Long':
            sl_ce = float(ce_price)*(1-(float(sl_perc)/100))
            sl_pe = float(pe_price)*(1-(float(sl_perc)/100))
        sl_combo = None

        st.write('Stop Loss CE : ',round(sl_ce,2))
        st.write('Stop Loss PE : ',round(sl_pe,2))
       
    elif single_leg_or_comb == 'Combo':   
        if short_or_long == 'Short':
            sl_combo = float(combo_price)*(1+(float(sl_perc)/100))
        if short_or_long == 'Long':
            sl_combo = float(combo_price)*(1-(float(sl_perc)/100))
        sl_ce = None
        sl_pe = None
        st.write('Stop Loss Combo : ',round(sl_combo,2))
        

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


#! Outside form to chnage session state , which is not possible in form before click on submit
st.markdown(f"<h1 style='text-align: center; color: white; font-size: 30px;'>Calculate SL</h1>", unsafe_allow_html=True)
st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

custom_price_or_fetch_price_form_3 = st.radio("Select an option", ["Custom Price", "Fetch Price"],key='hide_or_show')


#! Form for calculating SL  
with st.form(key='Calculate SL Form'):

    if custom_price_or_fetch_price_form_3 == "Custom Price":
        ce_price_form_3 = st.text_input(label='CE Price')
        pe_price_form_3 = st.text_input(label='PE Price')

        hour_form_3 = minute_form_3 = ce_strike_form_3 = pe_strike_form_3 = instrument_1_form_3 = None

    elif custom_price_or_fetch_price_form_3 == "Fetch Price":
        instrument_1_form_3 = st.radio("Select any one index",('Nifty', 'Banknifty', 'Finnifty'),key="horizontal_3").upper()
        hour_form_3 = st.text_input(label='Hour')
        minute_form_3 = st.text_input(label='Minute')   
        ce_strike_form_3 = st.text_input(label='CE Strike')
        pe_strike_form_3 = st.text_input(label='PE Strike')
        
        ce_price_form_3 = pe_price_form_3 = None

    sl_perc_form_3 = st.text_input(label='Stop loss percentage')  
    single_leg_or_comb_form_3 = st.radio("Select any one of them",('Single Leg', 'Combo'),key="horizontal_3_leg")
    short_or_long_form_3 = st.radio("Select any one of them",('Short', 'Long'),key="horizontal_3_direction")

    submit_button_3 = st.form_submit_button(label='Submit')


#! Submit Button
if submit_button_3:
    try:
        calculate_sl(instrument = instrument_1_form_3,
                    single_leg_or_comb = single_leg_or_comb_form_3,
                    custom_price_or_fetch_price = custom_price_or_fetch_price_form_3,
                    short_or_long = short_or_long_form_3,
                    sl_perc = sl_perc_form_3,
                    ce_price = ce_price_form_3,
                    pe_price = pe_price_form_3,
                    hour = hour_form_3,
                    minute = minute_form_3,
                    ce_strike = ce_strike_form_3,
                    pe_strike = pe_strike_form_3)
    except Exception as e:
        st.write('Please check all the input values', e)
