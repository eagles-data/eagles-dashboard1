import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
import base64
from pathlib import Path
from zoneinfo import ZoneInfo
import datetime

from utils.conn import *
from utils.codes import *

def get_font_style():
    """로컬 Fonts 폴더의 나눔고딕을 Streamlit CSS로 주입하는 헬퍼 함수"""
    font_path = Path(__file__).resolve().parent / "Fonts" / "NanumGothic.ttf"
    if font_path.exists():
        with open(font_path, "rb") as f:
            font_data = base64.b64encode(f.read()).decode()
        return f"""
        <style>
        @font-face {{
            font-family: 'NanumGothic';
            src: url(data:font/ttf;base64,{font_data}) format('truetype');
        }}
        * {{ font-family: 'NanumGothic'; }}
        </style>
        """
    return ""


def get_smart_labels(y_data, fmt, threshold_sigma=2.0):
    """중요한 지점만 골라내어 레이블 리스트를 반환하는 함수"""
    y_series = pd.Series(y_data)
    n = len(y_series)
    
    # 1. 기초 통계량 계산 (Threshold 용)
    mean_val = y_series.mean()
    std_val = y_series.std()
    
    labels = []
    for i in range(n):
        curr = y_series.iloc[i]
        
        # 데이터가 없으면 패스
        if pd.isna(curr):
            labels.append("")
            continue
            
        # [조건 A] 첫 번째와 마지막 경기는 항상 표시 (전체 흐름의 시작과 끝)
        if i == 0 or i == n - 1:
            labels.append(format(curr, fmt))
            continue
            
        # [조건 B] Local Extrema (전후 값이 있을 때만 비교)
        prev_val = y_series.iloc[i-1]
        next_val = y_series.iloc[i+1]
        is_extrema = False
        if pd.notnull(prev_val) and pd.notnull(next_val):
            # 전후보다 크거나(Peak), 전후보다 작을 때(Valley)
            if (curr > prev_val and curr > next_val) or (curr < prev_val and curr < next_val):
                is_extrema = True
        
        # [조건 C] Threshold (시즌 평균 대비 1.5 표준편차 이상 특이치)
        is_outlier = False
        if std_val > 0: # 변동성이 있을 때만 계산
            if abs(curr - mean_val) > (threshold_sigma * std_val):
                is_outlier = True
                
        # 두 조건 중 하나라도 만족하면 레이블 추가
        if is_extrema or is_outlier:
            labels.append(format(curr, fmt))
        else:
            labels.append("")
            
    return labels


def draw_final_pitcher_chart(df):
    # 1. 데이터 정렬 및 인덱스 초기화 (선 꼬임 방지 핵심)
    df = df.copy()
    df['game_date'] = pd.to_datetime(df['game_date'])
    df = df.sort_values('game_date').reset_index(drop=True) # 날짜순으로 줄 세우기
    
    df['date_label'] = df['game_date'].dt.strftime('%y/%m/%d')
    df['year'] = df['game_date'].dt.year.astype(str)
    
    years = sorted(df['year'].unique())
    # 2023: 노랑, 2024: 퍼플 (요청하신 이미지 배색 반영)
    custom_colors = ['#f1c40f', '#a6719a', '#3498db', '#e74c3c'] 
    color_map = {year: custom_colors[i % len(custom_colors)] for i, year in enumerate(years)}

    # 경기당 70px 보장하여 쾌적한 가로폭 확보
    px_per_game = 80
    dynamic_width = max(1000, len(df) * px_per_game)

    metrics = [
        ("평균 구속", "avg_speed", ".1f"),
        ("최고 구속", "max_speed", ".1f"),
        ("회전수", "avg_spinrate", ".0f"),
        ("릴리즈 높이", "avg_relh", ".2f"),
        ("익스텐션", "avg_ext", ".2f"),
        ("수직무브먼트", "avg_ivb", ".1f"),
        ("수평무브먼트", "avg_hb", ".1f")
    ]

    fig = make_subplots(
        rows=7, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.02,
        subplot_titles=[f"<b>{m[0]}</b>" for m in metrics]
    )

    # 2. 지표별/연도별 데이터 추가
    for i, (title, col, fmt) in enumerate(metrics, 1):
        # Y축 자동 범위 설정 및 스타일링 위함
        y_val = df[col].dropna()
        y_all = df[col] # dropna() 하지 말고 전체 길이를 유지해야 인덱스가 일치함
        full_smart_labels = get_smart_labels(y_all.values, fmt)

        for year in years:
            # 해당 연도의 인덱스 추출
            year_df = df[df['year'] == year]
            if year_df.empty: continue

            # 전체 스마트 레이블 리스트에서 해당 연도의 인덱스에 해당하는 것만 추출
            current_year_labels = [full_smart_labels[idx] for idx in year_df.index]
            # smart_labels = get_smart_labels(y_val, fmt)

            # Scatter의 x값으로 df의 실제 index를 사용해야 선이 꼬이지 않습니다.
            fig.add_trace(
                go.Scatter(
                    x=year_df.index, # 인덱스 사용으로 선 꼬임 원천 봉쇄
                    y=year_df[col],
                    mode='lines+markers+text',
                    # [핵심] 선별된 레이블 리스트 주입
                    text=current_year_labels,
                    # text=smart_labels,  # 모든 점이 아닌 선별된 레이블만 주입
                    # [주의] texttemplate은 삭제해야 합니다. (있으면 필터링이 무시됨)
                    # texttemplate=f"%{{y:{fmt}}}",
                    #text=year_df[col].apply(lambda v: format(v, fmt) if pd.notnull(v) else ""),
                    textposition="top center",
                    textfont=dict(family="NanumGothic", size=12, color="black"),
                    line=dict(color=color_map[year], width=3),
                    marker=dict(size=8, color=color_map[year], line=dict(width=1, color='white')),
                    name=f"{year}년",
                    legendgroup=year,
                    showlegend=(i == 1),
                    connectgaps=False, # 데이터 끊김 지점 유지
                    cliponaxis=False, # 글자가 차트 경계선에 걸려도 사라지지 않게
                ),
                row=i, col=1
            )
        if not y_val.empty:
            y_min, y_max = y_val.min(), y_val.max()
            padding = (y_max - y_min) * 0.6 # 레이블 공간 확보를 위해 패딩 증가
            fig.update_yaxes(range=[y_min - padding, y_max + padding], row=i, col=1, 
                             showticklabels=False, showgrid=False, zeroline=False)
        
        fig.add_hrect(y0=0, y1=1, line_width=0, fillcolor="#f4f4f4", opacity=0.3, layer="below", row=i, col=1)

    # 3. 레이아웃 설정
    fig.update_layout(
        height=720,
        width=dynamic_width,
        autosize=False,
        margin=dict(l=20, r=20, t=60, b=40),
        template="plotly_white",
        font=dict(family="NanumGothic"),
        hovermode="x unified",
        title=dict(
            text="경기별 트래킹 기록",
            x=0.02, y=0.97, font=dict(size=22, color="black", family="NanumGothic")
        ),
        xaxis7=dict(
            tickmode='array',
            tickvals=df.index,
            ticktext=df['date_label'],
            type="linear", # category 대신 linear를 써야 인덱스 간격이 정확합니다.
            showgrid=True,
            gridcolor="#eeeeee"
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )


    # 유니코드 마이너스 문제 방지 (축 설정 강제)
    fig.update_xaxes(exponentformat="none", separatethousands=True)
    st.plotly_chart(fig, width='content')

    return fig

st.markdown(get_font_style(), unsafe_allow_html=True) # 폰트 CSS 주입

st.set_page_config(
    page_title = "경기별 트래킹 기록",
    page_icon = "🎨",
    layout='wide',
)

KST = ZoneInfo('Asia/Seoul')
오늘 = datetime.datetime.now(KST)
올해 = 오늘.year

engine = get_conn()
최대연도 = get_max_year(engine)

# 투수 명단(이름, ID) 가져오기
@st.cache_data(ttl=43200)
def 투수ID이름가져오기():
    query = f"""
SELECT
    distinct pinfo.name, sap.pitcherid pid
FROM
    service_mart.season_agg_pitcher sap,
    master_meta.player_info pinfo
WHERE
    sap.year >= {최대연도-5}
    AND sap.pitcherid = pinfo.tm_id
    """;
    df = get_sql_df(query, engine)

    return df.values

def 투수데이터(레벨: str=None,
               연도: int=None,
               투수ID: int=None,
               날짜쿼리: str=None,
               선택구종: str=None):

    쿼리 = f"""
SELECT
    game_date,
    AVG(relspeed) AS avg_speed,
    MAX(relspeed) AS max_speed,
    AVG(spinrate) AS avg_spinrate,
    AVG(relheight) AS avg_relh,
    AVG(extension) AS avg_ext,
    AVG(inducedvertbreak) AS avg_ivb,
    AVG(horzbreak) AS avg_hb
FROM
    raw_tracking.tm
WHERE
    pitcherid = {투수ID}
    AND taggedpitchtype = '{구종한글_영문으로변환[선택구종]}'
    AND stadium not in ('Gwangju', 'Pohang', 'Ulsan', 'Cheongju')
"""

    if 연도 is None:
        pass
    elif 연도 != '전체':
        쿼리 += f' AND year = {연도} '
    if 날짜쿼리 is not None:
        쿼리 += f"AND {날짜쿼리} "

    if 레벨 == '1군':
        쿼리 += f" AND level = 'KBO'"
    elif 레벨 == '퓨처스':
        쿼리 += f" AND level = 'KBO Minors'"
    elif 레벨 == '시범':
        쿼리 += f" AND level = 'Exhibition'"
    elif 레벨 == '정규':
        쿼리 += f" AND level IN ('KBO', 'KBO Minors')"
    elif 레벨 == '포스트시즌':
        쿼리 += f" AND league = 'KBOPostseason'"
    elif 레벨 == '정규+포시':
        쿼리 += f" AND ((league='KBOPostseason') OR (level IN ('KBO', 'KBO Minors')))"

    쿼리 += " GROUP BY game_date"

    df = get_sql_df(쿼리, engine)

    return df


# 데이터 읽어오기
with st.spinner('loading data...'):
    투수ID이름 = 투수ID이름가져오기()
# idNames 컬럼
투수이름리스트 = [f'{x[0]} ({x[1]})' for x in 투수ID이름]
투수이름리스트.sort(reverse=False)

투수이름_ID_딕셔너리 = {f'{x[0]} ({x[1]})': [x[0], x[1]] for x in 투수ID이름}

st.markdown("##### Daily 트래킹 데이터 그래프")

#######################
# 선택 영역1: 연도, 레벨, 팀, 투수 선택
#######################
셀렉터구역1 = st.columns(8)
시즌들 = list(range(최대연도-4, 최대연도+1))[::-1]
최소시즌 = min(시즌들)

with 셀렉터구역1[0]:
    선택한연도 = st.selectbox(label="시즌",
                               options=['전체']+시즌들,
                               placeholder='...연도 선택',
                               index=1)
    if 선택한연도 == '전체':
        선택한연도 = None

with 셀렉터구역1[1]:
    선택한레벨 = st.selectbox(label = '1군/퓨처스',
                              options = ('전체', '1군', '퓨처스', '정규', '포스트시즌', '정규+포시', '시범'),
                              placeholder = '...레벨 선택',
                              index=0)

with 셀렉터구역1[2]:
    선택한투수 = st.selectbox(label = "투수",
                              options = 투수이름리스트,
                              placeholder = '...투수')

if 선택한투수:
    선택한투수이름 = 투수이름_ID_딕셔너리[선택한투수][0]
    선택한투수ID = 투수이름_ID_딕셔너리[선택한투수][1]
else:
    선택한투수이름 = None
    선택한투수ID = None

#######################
# 선택 영역2: 날짜, 경기 옵션 선택
#######################
# 날짜 선택
if 선택한연도 is None:
    제일앞날짜 = datetime.date(최소시즌, 2, 1)
    제일끝날짜 = 오늘.date()
else:
    제일앞날짜 = datetime.date(선택한연도, 2, 1)
    if 선택한연도 == 최대연도:
        if 최대연도 == 올해:
            제일끝날짜 = 오늘.date()
        else:
            제일끝날짜 = datetime.date(최대연도, 12, 31)
    else:
        제일끝날짜 = datetime.date(선택한연도, 12, 31)

with 셀렉터구역1[3]:
    앞날짜 = st.date_input("시작일",
                           제일앞날짜,
                           format="YYYY.MM.DD")
with 셀렉터구역1[4]:
    뒷날짜 = st.date_input("종료일",
                           제일끝날짜,
                           format="YYYY.MM.DD")
    앞날짜텍스트 = 앞날짜.strftime('%y.%m.%d')
    뒷날짜텍스트 = 뒷날짜.strftime('%y.%m.%d')
if 앞날짜 and 뒷날짜:
    날짜범위 = (앞날짜, 뒷날짜)
else:
    날짜범위 = (제일앞날짜, 제일끝날짜)

if len(날짜범위) > 1:
    시작날, 끝날 = 날짜범위
    시작날_텍스트 = 시작날.strftime('%Y-%m-%d')
    끝날_텍스트 = 끝날.strftime('%Y-%m-%d')

    날짜쿼리 = f" game_date >= '{시작날_텍스트}' and game_date <= '{끝날_텍스트}'"
else:
    시작날 = 날짜범위[0]
    끝날 = None
    시작날_텍스트 = 시작날.strftime('%Y-%m-%d')

    날짜쿼리 = f" game_date >= '{시작날_텍스트}'"

#######################
# 선택 영역4: 구종 옵션 선택
#######################
with 셀렉터구역1[5]:
    ### 구종 체크박스
    구종옵션 = ['직구', '투심', '슬라', '커터', '스위퍼', '커브', '체인', '포크']
    선택구종 = st.selectbox("구종", 구종옵션)


#### 선택한 투수 투구 데이터 가져오기
df = 투수데이터(선택한레벨, 선택한연도, 선택한투수ID, 날짜쿼리, 선택구종)

fig = draw_final_pitcher_chart(df)
