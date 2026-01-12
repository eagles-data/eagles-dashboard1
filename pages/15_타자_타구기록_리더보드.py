import streamlit as st
import pandas as pd
import numpy as np
from utils.codes import *
from utils.conn import *

st.set_page_config(layout="wide")

engine = get_conn()
최대연도 = get_max_year(engine)

@st.cache_data(ttl=86400)
def load_data():
    query = f"""
WITH bsr_all AS (
    SELECT 
        `year`, 
        tmid, 
        IF(team='고양', '키움', team) AS 시즌소속팀,
        ROW_NUMBER() OVER (PARTITION BY `year`, tmid ORDER BY CASE WHEN level_eng = 'KBO' THEN 1 ELSE 2 END) as rn
    FROM `stats_logs`.stats_hitter
    WHERE `year` BETWEEN {최대연도-4} AND {최대연도}
),
bsr AS (
    SELECT `year`, tmid, 시즌소속팀
    FROM bsr_all
    WHERE rn = 1
)
SELECT
    pi2.name AS 이름,
    pi2.team AS 현소속팀,
    bsr.시즌소속팀,
    agg.year,
    agg.level,
    agg.PA,
    agg.BIPs,
    agg.mean_la,
    agg.mean_ev,
    agg.max_ev,
    agg.t10_ev,
    agg.hardhits,
    agg.hardhit_rate,
    agg.barrel_rate,
    agg.flareburner_rate,
    agg.pullair_rate
FROM
    `service_mart`.season_agg_hitter agg
JOIN
    `master_meta`.player_info pi2 ON agg.BatterId = pi2.tm_id
LEFT JOIN
    bsr ON bsr.tmid = agg.BatterId
        AND bsr.year = agg.year
WHERE
    agg.year BETWEEN {최대연도-4} AND {최대연도}
    """
    return get_sql_df(query, engine).rename(columns=타자컬럼명변환)

st.markdown("##### 타자 타구기록 리더보드")
st.markdown("##### 시즌별 타자의 타구 속도, 발사각 등 상세 타구 지표를 제공합니다.")

with st.spinner('loading data...'):
    raw_df = load_data()

# 필터 영역
시즌옵션 = list(range(최대연도-4, 최대연도+1))[::-1]
팀옵션 = ["전체", "한화", "KIA", "KT", "LG", "NC", "SSG", "두산", "롯데", "삼성", "키움", "상무", "없음"]

셀렉터영역 = st.columns(11) 

with 셀렉터영역[0]:
    선택시즌 = st.selectbox("시즌", 시즌옵션, index=0)

with 셀렉터영역[1]:
    선택레벨 = st.selectbox("1군/퓨처스", ["1군", "퓨처스"], index=0)

with 셀렉터영역[2]:
    현시즌구분 = st.radio("팀 분류", ["현재", "시즌"], index=1, horizontal=True)
    선택팀 = st.selectbox("소속팀", 팀옵션, index=0)

with 셀렉터영역[3]:
    최소타구수 = st.number_input("최소 인플레이 타구수", min_value=0, value=50, step=10)

with 셀렉터영역[-1]:
    if st.button("Clear Cache"):
        load_data.clear()
        st.rerun()

# 클라이언트 사이드 필터링 적용
df = raw_df[raw_df['연도'] == 선택시즌]

if 선택레벨 == "1군":
    df = df[df['레벨'] == 'KBO']
elif 선택레벨 == "퓨처스":
    df = df[df['레벨'] == 'KBO Minors']

# 현소속팀 vs 시즌소속팀 기준 적용
if 현시즌구분 == "현재":
    df['소속팀'] = df['현소속팀']
else:
    df['소속팀'] = np.where(df['시즌소속팀'].isna(), df['현소속팀'], df['시즌소속팀'])

df['팀'] = df['소속팀'].apply(get_base64_emblem)

if 선택팀 != "전체":
    df = df[df['소속팀'] == 선택팀]

df = df[df['인플레이 타구수'] >= 최소타구수]

# 정렬 및 컬럼 정의
display_cols = [
    '이름', '팀', '타석', '인플레이 타구수', 
    '평균 발사각도', '평균 타구속도', '최대 타구속도', 'T-10', 
    '강한 타구수', '강한타구%', '배럴%', '단타성타구%', 'PullAir%'
]

st.dataframe(
    df[display_cols]\
    .set_index(['이름', '팀'])\
    .sort_values(by='최대 타구속도', ascending=False),
    hide_index=False,
    width='content',
    column_config={
        "팀": st.column_config.ImageColumn(label="팀", width="small"),
        **타자컬럼포맷설정
    }
)
