import streamlit as st
import pandas as pd
import numpy as np
import base64
from utils.codes import *
from utils.conn import *

st.set_page_config(
    page_title="트래킹 데이터 리더보드",
    page_icon="📊",
    layout='wide',
)

engine = get_conn()
최대연도 = get_max_year(engine)

@st.cache_data(ttl=86400)
def load_pitchtype_data():
    query = f"""
    WITH psr_all AS (
        SELECT 
            `year`, 
            tmid, 
            IF(team='고양', '키움', team) AS 시즌소속팀,
            ROW_NUMBER() OVER (PARTITION BY `year`, tmid ORDER BY CASE WHEN level_eng = 'KBO' THEN 1 ELSE 2 END) as rn
        FROM `stats_logs`.stats_pitcher
        WHERE `year` BETWEEN {최대연도-4} AND {최대연도}
    ),
    psr AS (
        SELECT `year`, tmid, 시즌소속팀
        FROM psr_all
        WHERE rn = 1
    )
    SELECT
        pinfo.name AS 이름,
        IF(substr(pinfo.bat_throw, 1, 1)='우', '우', '좌') AS `손(투)`,
        spa.pitchtype AS 구종명_영문,
        spa.cnt AS 투구수,
        spa.speed_avg AS 평균구속,
        spa.speed_max AS 최고구속,
        spa.spin_avg AS 평균회전수,
        spa.ivb_avg AS 평균수직무브먼트,
        spa.hb_avg AS 평균좌우무브먼트,
        spa.relheight_avg AS 평균릴리즈높이,
        spa.extension_avg AS 평균익스텐션,
        spa.year,
        spa.level,
        pinfo.team AS 현소속팀,
        psr.시즌소속팀,
        pinfo.tm_id,
        pinfo.team_code AS 팀코드
    FROM
        service_mart.season_pitchtype_agg spa
    JOIN
        master_meta.player_info pinfo ON spa.pitcherid = pinfo.tm_id
    LEFT JOIN
        psr ON psr.tmid = spa.pitcherid 
            AND psr.year = spa.year
    WHERE
        spa.year BETWEEN {최대연도-4} AND {최대연도}
    """
    df = get_sql_df(query, engine)
    df = df[df.팀코드 != 'SOFTBANK']

    # 구종명 한글 변환
    df['구종'] = df['구종명_영문'].apply(lambda x: 구종영문_한글로변환.get(x, x))

    return df

st.markdown("##### 투수 시즌/구종 별 트래킹 데이터")

# 데이터 로드 (5년치 전체)
with st.spinner('loading data...'):
    raw_df = load_pitchtype_data()

# 필터 영역
시즌옵션 = list(range(최대연도-4, 최대연도+1))[::-1]
팀옵션 = ["전체", "한화", "KIA", "KT", "LG", "NC", "SSG", "두산", "롯데", "삼성", "키움", "상무", "없음"]
구종옵션 = ["전체", "직구", "투심", "슬라", "커터", "스위퍼", "커브", "체인", "포크"]

셀렉터영역 = st.columns([1, 1, 1, 1, 1, 1, 1, 3]) # 총 10 비율

with 셀렉터영역[0]:
    선택시즌 = st.selectbox("연도 선택", 시즌옵션, index=0)

with 셀렉터영역[1]:
    선택레벨 = st.selectbox("레벨 선택", ["전체", "1군", "퓨처스"], index=0)

with 셀렉터영역[2]:
    현시즌구분 = st.radio("팀 분류", ["현재", "시즌"], index=1, horizontal=True)
    선택팀 = st.selectbox("소속팀 선택", 팀옵션, index=0)

with 셀렉터영역[3]:
    선택구종 = st.selectbox("구종 선택", 구종옵션, index=1)

with 셀렉터영역[4]:
    선택Hand = st.radio("우투/좌투", ["전체", "우", "좌"], index=0)

with 셀렉터영역[5]:
    최소투구수 = st.number_input("최소 투구수", min_value=0, value=500, step=50)

with 셀렉터영역[6]:
    if st.button("Clear Cache"):
        load_pitchtype_data.clear()
        st.rerun()

# 클라이언트 사이드 필터링 적용
df = raw_df[raw_df['year'] == 선택시즌]

if 선택레벨 == "1군":
    df = df[df['level'] == 'KBO']
elif 선택레벨 == "퓨처스":
    df = df[df['level'] == 'KBO Minors']
elif 선택레벨 == "전체":
    df = df[df['level'] == 'ALL']

# 현소속팀 vs 시즌소속팀 기준 적용
if 현시즌구분 == "현재":
    df['소속팀'] = df['현소속팀']
else:
    # 시즌소속팀 정보가 없는 경우 현소속팀으로 보안
    df['소속팀'] = np.where(df['시즌소속팀'].isna(), df['현소속팀'], df['시즌소속팀'])

df['팀'] = df['소속팀'].apply(get_base64_emblem)

if 선택팀 != "전체":
    df = df[df['소속팀'] == 선택팀]

if 선택구종 != "전체":
    영어구종명 = 구종한글_영문으로변환.get(선택구종)
    df = df[df['구종명_영문'] == 영어구종명]

if 선택Hand != "전체":
    df = df[df['손(투)'] == 선택Hand]

df = df[df['투구수'] >= 최소투구수]

# 리더보드 표시 (테이블 너비 제한을 위해 레이아웃 활용)
테이블영역 = st.columns([4, 1]) # 우측 여백을 두어 테이블이 너무 퍼지지 않게 함

with 테이블영역[0]:
    display_cols = [
        '이름', '팀', '손(투)', '구종', '투구수', 
        '평균구속', '최고구속', '평균회전수', 
        '평균수직무브먼트', '평균좌우무브먼트', 
        '평균릴리즈높이', '평균익스텐션'
    ]

    if not df.empty:
        st.dataframe(
            df[display_cols].sort_values('평균구속', ascending=False),
            hide_index=True,
            width='content',
            column_config={
                "팀": st.column_config.ImageColumn(label="팀", width="small"),
                "투구수": st.column_config.NumberColumn(format="%d"),
                "평균구속": st.column_config.NumberColumn(format="%.1f"),
                "최고구속": st.column_config.NumberColumn(format="%.1f"),
                "평균회전수": st.column_config.NumberColumn(format="%d"),
                "평균수직무브먼트": st.column_config.NumberColumn(format="%.1f"),
                "평균좌우무브먼트": st.column_config.NumberColumn(format="%.1f"),
                "평균릴리즈높이": st.column_config.NumberColumn(format="%.2f"),
                "평균익스텐션": st.column_config.NumberColumn(format="%.2f"),
            }
        )
    else:
        st.info("조건에 맞는 데이터가 없습니다.")
