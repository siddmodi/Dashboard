import streamlit as st 
from PIL import Image
import redis

import sys
sys.path.append('C:\\Users\\Kailasa Capital\\Desktop\\Trial\\login')
from login import *

import numpy as np 
import pandas as pd 

logo =  Image.open("C:\\Users\\Kailasa Capital\\Desktop\\Trial\\straddle graph\\images\\Kailasa Favicon.png")
st.set_page_config(
    page_title = 'KAILASA CAPITAL',
    page_icon = logo,
    layout = 'wide'                                                                                                                                 
)

#! Basic UI

full_logo = Image.open("C:\\Users\\Kailasa Capital\\Desktop\\Trial\\straddle graph\\images\\Kailasa Full Logo.png")

col1, col2,col3 = st.columns([1, 1, 1])

with col1:
    st.write(' ')

with col2:     
    st.image(full_logo)  

with col3:
    st.write(' ')                                                   

placeholder = st.empty()

#! Common Function

@st.cache_resource
def login_dashboard():
    credentials = pd.read_csv("C:\\Users\\Kailasa Capital\\Desktop\\Trial\\login\\credentials.csv")
    accounts = credentials['user_id'].to_list()
    for user_id in accounts:
        if user_id is np.nan:
            continue
        try:
            account_login = login(user_id)
        except:
            print("Error logging into: ",user_id)
    credentials = login_all()

    kite = credentials[credentials['user_id']=='VR2386']['object'].iloc[0]
    return kite


##! LOGIN & Redis Connection ##
kite = login_dashboard()


# streamlit run Home.py