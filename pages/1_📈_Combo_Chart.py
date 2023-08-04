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

import warnings
warnings.filterwarnings("ignore",category=FutureWarning)

logo =  Image.open("C:\\Users\\Kailasa Capital\\Desktop\\Trial\\straddle graph 2\\images\\Kailasa Favicon.png")
st.set_page_config(
    page_title = 'KAILASA CAPITAL',
    page_icon = logo,
    layout = 'wide'
)


##! FUNCTIONS ##

@st.cache_resource
def redis_connection(host,port):
    # create a Redis client instance by defualt database 0
    r = redis.Redis(host, port, db=0)
    return r

@st.cache_resource
def list_trading_symbol():
    with open('C:\\Users\\Kailasa Capital\\Desktop\\Trial\\redis\\instruments_final.json') as f:
        data = json.load(f)
    list_trading_symbol = list(data.keys())
    return list_trading_symbol


def create_df(stream_name,ltp_col_name):
    stream_data = r.xrange(stream_name)
    #! Making a df for CE & PE individually
    decoded_list = [(item[0].decode(), {key.decode(): value.decode() for key, value in item[1].items()}) for item in stream_data]
    
    time_values = [item[0] for item in decoded_list]
    ltp_values = [item[1]['LTP'] for item in decoded_list]

    df = pd.DataFrame({'Time': time_values, ltp_col_name: ltp_values})

    #! Cleaning CE & PE individual dataframe
    df['Time'] = df['Time'].apply(lambda x : int(x.split('-')[0])/1000)

    df['Time'] = df['Time'].apply(lambda x: datetime.fromtimestamp(x).time())

    df['Time'] = df['Time'].apply(lambda x: time(x.hour, x.minute))

    df = df.drop_duplicates(subset=['Time'], keep='first')

    df.reset_index(inplace=True,drop=True)

    return df


def merge_df(df_1,df_2):
    df = pd.merge(df_1, df_2, on ='Time')

    df['LTP CE'] = df['LTP CE'].astype(float)
    df['LTP PE'] = df['LTP PE'].astype(float)

    df['Strangle Price'] = round(df['LTP CE'] + df['LTP PE'],2)
    # df.drop(['LTP CE','LTP PE'], axis=1, inplace=True)
    # df['Time'] = df['Time'].apply(lambda x: x.strftime('%H:%M'))
    
    # print(df)

    return df


def upload_to_chart_studio(fig):
    chart_studio.plotly.plot(fig, filename = 'basic-line', auto_open=False)


def create_plotly_graph(df):

    #! Plotly Graph
    graph_title = f'Combo Price ( {instrument_1}{strike_price_1}{call_put_1} + {instrument_2}{strike_price_2}{call_put_2} )'
    st.markdown(f"<h1 style='text-align: center; color: white; font-size: 30px;'>{graph_title}</h1>", unsafe_allow_html=True)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df.Time, y=df['Strangle Price'], mode='lines+markers+text',line=dict(color="#0000ff"), name='Combo Price')) 
    fig.add_trace(go.Scatter(x=df.Time, y=df['LTP CE'], mode='lines+markers+text',line=dict(color="#ff0000"), name='CE Price')) 
    fig.add_trace(go.Scatter(x=df.Time, y=df['LTP PE'], mode='lines+markers+text',line=dict(color="#3cb371"), name='PE Price')) 

    # fig = px.line(df, x="Time", y=['Strangle Price','LTP CE','LTP PE'], title=graph_title ,markers=True)


    #! Customize the plot
    fig.update_layout(
        # title_text=graph_title,
        
        # title=dict(
        #     text=graph_title,
        #     font=dict(size=24),
        #     x=0.5,
        #     font_family="Times New Roman",
        #     xref="paper"
        #     ),

        height = 700,
        hovermode='x unified',

        # title_font=dict(size=25),
        # title_x=0.35,
        
        xaxis=dict(title = 'Time', title_standoff=20,color='white',showline=True, title_font=dict(size=28)),  # Adjust x-axis title properties
        yaxis=dict(title = 'Price', title_standoff=20,color='white',showline=True, title_font=dict(size=28)),  # Adjust y-axis title properties

        hoverlabel=dict(
            font_size=25,
            font_family="Rockwell"
            )
        )


    # Creating white dots 
    # fig.update_traces(marker=dict(color='rgba(255, 255, 255, 1)'), textfont=dict(color='white'))

    #! Setting y axis range
    y_axis_max = max(df['Strangle Price'].max(),df['LTP CE'].max(),df['LTP PE'].max()) 
    y_axis_min = min(df['Strangle Price'].min(),df['LTP CE'].min(),df['LTP PE'].min())

    fig.update_layout(yaxis_range=[y_axis_min,y_axis_max])

    return fig


def ltp(stream_id_1,stream_id_2):  
    try:
        #! Live data stream
        stream_1_ltp = float(r.xread(stream_id_1, block=0)[0][1][0][1][b'LTP'].decode())
        print('stream_1_ltp :::', stream_1_ltp)
        stream_2_ltp = float(r.xread(stream_id_2, block=0)[0][1][0][1][b'LTP'].decode())

        ltp_strangle = round(stream_2_ltp+stream_1_ltp,2)
        # ltp_strangle = stream_2_ltp+stream_1_ltp

        # st.write(f'LTP : {ltp_strangle}')
        # print(f'LTP : {ltp_strangle}')
        time.sleep(1)

    except:
        print('no ltp')
        pass
    return ltp_strangle


##! STREAMLIT ##

#! Basic UI

full_logo = Image.open("C:\\Users\\Kailasa Capital\\Desktop\\Trial\\straddle graph 2\\images\\Kailasa Full Logo.png")

col1, col2,col3 = st.columns([4, 2, 4])

with col1:
    st.write(' ')

with col2:     
    st.image(full_logo)  

with col3:
    st.write(' ')

placeholder = st.empty()


#! Form for Combo graph
with st.form(key='Option Chart'):
    # st.write("Combo Form")
    # col1, col2, col3 = st.columns([1,1,1])
    # col2.header('Combo Chart')
    st.markdown(f"<h1 style='text-align: center; color: white; font-size: 30px;'>Combo Chart</h1>", unsafe_allow_html=True)
    instrument_1 = instrument_2 = st.radio("Select any one index",('Nifty', 'Banknifty', 'Finnifty'),key="horizontal").upper()

    strike_price_1 = st.text_input(label='CE Strike')
    strike_price_2 = st.text_input(label='PE Strike')

    call_put_1 = 'CE'
    call_put_2 = 'PE'

    submit_button = st.form_submit_button(label='Submit')

r = redis_connection(host='localhost', port=6379)

list_trading_symbol = list_trading_symbol()

##! Submit buttons for Combo Graph  ##
if submit_button:

    ##! Main ##
    # Define the stream name to read from
    try:
        stream_name_1 = [s for s in list_trading_symbol if all(x in s for x in [instrument_1, call_put_1, strike_price_1])][0]
        stream_name_2 = [s for s in list_trading_symbol if all(x in s for x in [instrument_2, call_put_2, strike_price_2])][0]

        # Set the starting Stream IDs for each stream
        stream_id_1 = {stream_name_1: '$'}
        stream_id_2 = {stream_name_2: '$'}

        if (instrument_1 == 'NIFTY') and ('BANKNIFTY' in stream_name_1):
            stream_name_1 = None
            stream_name_2 = None

            st.write('Please select correct combination of Index and Strike')

        else:
            count = 1
            while True:
                #! LTP function
                with placeholder.container():
                    # if datetime.now.time() < time(15,30):
                    ltp_strangle = ltp(stream_id_1,stream_id_2)
                    st.markdown(
                                """
                                <style>
                                    [data-testid="stMetricValue"] {
                                        font-size: 40px;
                                    }
                                </style>
                                """,
                                    unsafe_allow_html=True,
                                )
                    try:
                        st.metric(label="LTP", value=f'₹{ltp_strangle}',delta=f'{delta_value} %')
                    except:
                        st.metric(label="LTP", value=f'₹{ltp_strangle}')
                    # placeholder.empty()
    
                    if count ==1:
                        #! Creating clean datframe for CE and PE
                        df_1 = create_df(stream_name_1,ltp_col_name = 'LTP CE')
                        df_2 = create_df(stream_name_2,ltp_col_name = 'LTP PE')

                        #! Merging both dataframe for strangle 
                        df = merge_df(df_1,df_2)
                        delta_value = round((((df['Strangle Price'].iloc[-1] - df['Strangle Price'].iloc[0])/df['Strangle Price'].iloc[0])*100),2)
                
                        #! Create graph
                        fig = create_plotly_graph(df)
                        count = 2

                        #! Placeholder
                        # with placeholder.container():        
                        st.plotly_chart(fig,use_container_width=True) 

                    elif int(datetime.now().time().strftime("%S")) == 1:

                        #! Creating clean datframe for CE and PE
                        df_1 = create_df(stream_name_1,ltp_col_name = 'LTP CE')
                        df_2 = create_df(stream_name_2,ltp_col_name = 'LTP PE')

                        #! Merging both dataframe for strangle 
                        df = merge_df(df_1,df_2)
                
                        #! Create graph
                        fig = create_plotly_graph(df)

                        #! Placeholder
                        # with placeholder.container():        
                        st.plotly_chart(fig,use_container_width=True)  
                # placeholder.empty()                                
    except Exception as e:
        st.write('Please select correct combination of Index and Strike in except',e)

