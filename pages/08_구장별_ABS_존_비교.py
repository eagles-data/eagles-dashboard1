import streamlit as st
import numpy as np
import datetime
import matplotlib.pyplot as plt

from utils.codes import *
from utils.plots import *
from utils.TMABS import *
from utils.conn import *

teams = ['전체', '한화', 'LG', 'KIA', '두산', '삼성', 'SSG', 'NC', 'KT', '롯데', '키움']

bucket_name = "baseball_app_data_cache"
parquet_file_path = f"gs://{bucket_name}/TMABS/TMABSbackdata.parquet"

st.set_page_config(
    page_title = "트랙맨 ABS 비교",
    page_icon = "🎨",
    layout='wide',
)
st.markdown("##### 트랙맨 기준, ABS에서 스트 판정 받은 공으로 그린 존.")


@st.cache_data(ttl=86400)
def load_data():
    return pd.read_parquet(parquet_file_path, 
                           engine='pyarrow', 
                           storage_options=get_storage_options())


# 데이터 읽어오기
with st.spinner('loading data...'):
    df = load_data()

최대날짜 = df.game_date.max()
최대연도 = 최대날짜.year

버튼표시영역 = st.columns(6)
with 버튼표시영역[-1]:
    if st.button("Clear Cache"):
        load_data.clear()

with 버튼표시영역[0]:
    st.markdown('##### 최근 N경기 보기')
    select_games = st.slider('최근 N경기?', 0, 20, 10)

with 버튼표시영역[1]:
    chart_color = st.color_picker("영역 색상", "#F08080")
    st.caption(chart_color)

with 버튼표시영역[2]:
    st.markdown('##### 기간 지정해서 보기')
    제일앞날짜 = datetime.date(최대연도, 2, 1)
    제일끝날짜 = 최대날짜
    앞날짜선택 = st.date_input("기간 - 시작일 선택",
                               제일앞날짜,
                               format="MM.DD.YYYY")
    뒷날짜선택 = st.date_input("기간 - 종료일 선택",
                               제일끝날짜,
                               format="MM.DD.YYYY")

set_fonts()
그림표시영역 = st.columns(2)

N경기그림들 = show_TM_ABS_diff(df,
                               select_games,
                               chart_color=chart_color)
with 그림표시영역[0]:
    st.pyplot(N경기그림들[0])
    st.pyplot(N경기그림들[1])

기간지정그림들 = show_TM_ABS_diff2(df,
                                   앞날짜선택,
                                   뒷날짜선택,
                                   chart_color=chart_color)
with 그림표시영역[1]:
    st.pyplot(기간지정그림들[0])
    st.pyplot(기간지정그림들[1])
