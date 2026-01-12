import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
from zoneinfo import ZoneInfo

from utils.codes import *
from utils.plots import *
from utils.conn import *

st.set_page_config(
    page_title = "VAA 플롯",
    page_icon = "🎨",
    layout='wide',
)
st.markdown("##### 구종별 VAA 플롯")

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


def 리그평균데이터(df):
    #### 구종 평균 데이터 가져오기
    if len(df) > 0:
        구종목록 = df.TaggedPitchType.unique().tolist()
        구종목록 = [x for x in 구종목록 if x not in ('Other', 'Undefined', 'Knuckleball')]
        if len(구종목록) > 0:
            구종목록쿼리문자열 = "('" + "', '".join(구종목록) + "')"
        else:
            구종목록쿼리문자열 = f"('{구종목록}')"

        던지는손 = df.PitcherThrows.unique()[0]
        던지는손쿼리문자열 = 던지는손

        유니크_연도목록 = df.year.unique().tolist()
        if len(유니크_연도목록) > 0:
            연도쿼리문자열 = max(유니크_연도목록)
        else:
            연도쿼리문자열 = 유니크_연도목록[0]
        쿼리 = 'Select * from service_mart.season_pitchtype_agg_lg '+\
               f"where pthrows = '{던지는손쿼리문자열}' and "+\
               f"pitch_type in {구종목록쿼리문자열} "+\
               f"and year = {연도쿼리문자열};"

        구종DF = get_sql_df(쿼리, engine)

        return 구종DF
    else:
        return None


def 투수데이터(레벨: str=None,
               연도: int=None,
               투수ID: int=None,
               날짜쿼리: str=None,
               선택구종_텍스트: str=None):
    쿼리 = 'select year, PitcherId, Pitcher, PitcherThrows, Level, TaggedPitchType, '+\
           'RelSpeed, SpinRate, PlateLocHeight, InducedVertBreak, HorzBreak, VertApprAngle, HorzApprAngle, '+\
           'RelHeight, Extension, PitchNo, GameID from raw_tracking.tm '+\
           f'where pitcherid={투수ID} '+\
           "and taggedpitchtype not in ('Other', 'Undefined', 'Knuckleball') "+\
           "and stadium not in ('Gwangju', 'Pohang', 'Ulsan', 'Cheongju')"

    if 선택구종_텍스트 is not None:
        쿼리 += f"and taggedpitchtype in {선택구종_텍스트} "

    if 연도 != '전체':
        쿼리 += f' and year = {연도} '
    if 날짜쿼리 is not None:
        쿼리 += f"and {날짜쿼리} "

    if 레벨 == '1군':
        쿼리 += f" and level = 'KBO'"
    elif 레벨 == '퓨처스':
        쿼리 += f" and level = 'KBO Minors'"
    else:
        쿼리 += f" and level in ('KBO', 'KBO Minors')"
        
    df = get_sql_df(쿼리, engine)
    df = df.assign(game_date = df.GameID.apply(lambda x: datetime.datetime.strptime(x[:8], '%Y%m%d').date()))

    return df


def 투수게임날짜(레벨=None,
                 연도=None,
                 투수ID=None,
                 시작일=None,
                 종료일=None):
    if 레벨 is None:
        쿼리 = f"""
            SELECT distinct game_date, gameid
            FROM raw_tracking.tm
            WHERE pitcherid={투수ID}
        """
    elif 레벨.lower() in ('kbo', 'kbo minors', 'exhibition'):
        쿼리 = f"""
            SELECT distinct game_date, gameid
            FROM raw_tracking.tm
            WHERE pitcherid={투수ID}
            AND level='{레벨}'
        """
    else:
        쿼리 = f"""
            SELECT distinct game_date, gameid
            FROM raw_tracking.tm
            WHERE pitcherid={투수ID}
            AND level in ('KBO', 'KBO Minors')
        """
    if 연도:
        쿼리 += f" AND year={연도}"

    if 시작일:
        쿼리 += f" AND game_date >= '{시작일}'"

    if 종료일:
        쿼리 += f" AND game_date <= '{종료일}'"

    df = get_sql_df(쿼리, engine)
    df['game_date'] = pd.to_datetime(df.game_date).dt.date
    return df




# 데이터 읽어오기
with st.spinner('loading data...'):
    투수ID이름 = 투수ID이름가져오기()
# idNames 컬럼
투수이름리스트 = [f'{x[0]} ({x[1]})' for x in 투수ID이름]
투수이름리스트.sort(reverse=False)

투수이름_ID_딕셔너리 = {f'{x[0]} ({x[1]})': [x[0], x[1]] for x in 투수ID이름}

#######################
# 선택 영역1: 연도, 레벨, 팀, 투수 선택
#######################
셀렉터구역1 = st.columns(6)
시즌들 = list(range(최대연도-4, 최대연도+1))[::-1]
최소시즌 = min(시즌들)

with 셀렉터구역1[0]:
    선택한연도 = st.selectbox(label="시즌",
                               options=['전체']+시즌들,
                               placeholder='...연도 선택',
                               index=1)
    if 선택한연도 == '전체':
        선택한연도 = None

    선택한레벨 = st.selectbox(label = '1군/퓨처스',
                              options = ('전체', '1군', '퓨처스'),
                              placeholder = '...레벨 선택',
                              index=0)
    레벨 = 레벨영어변환[선택한레벨]

if 선택한레벨 != '1군':
    퓨처스임 = True
else:
    퓨처스임 = False

with 셀렉터구역1[1]:
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

with 셀렉터구역1[2]:
    앞날짜 = st.date_input("시작일",
                           제일앞날짜,
                           format="YYYY.MM.DD")
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

with 셀렉터구역1[3]:
    if 선택한투수ID:
        경기들 = 투수게임날짜(레벨=레벨, 연도=선택한연도, 투수ID=선택한투수ID,
                         시작일=시작날_텍스트, 종료일=끝날_텍스트)
        경기일옵션 = [x[0] for x in 경기들.values]
        경기일옵션.sort(reverse=True)
        경기일옵션 = ['전체'] + 경기일옵션

        선택한경기날 = st.selectbox(label = '경기일',
                                 options = 경기일옵션,
                                 placeholder = '...경기일 선택',
                                 index=0)
    if 선택한경기날 != '전체':
        날짜쿼리 += f" and game_date='{선택한경기날}'"

#######################
# 선택 영역4: 구종 옵션 선택
#######################
with 셀렉터구역1[-1]:
    ### 구종 체크박스
    구종옵션 = ['직구', '투심', '슬라', '커터', '스위퍼', '커브', '체인', '포크']

    선택한구종들 = st.pills("구종", 구종옵션, default=구종옵션, selection_mode="multi")

    선택구종 = []
    if '직구' in 선택한구종들:
        선택구종 += ['Fastball']
    if '투심' in 선택한구종들:
        선택구종 += ['Sinker']
    if '슬라' in 선택한구종들:
        선택구종 += ['Slider']
    if '커터' in 선택한구종들:
        선택구종 += ['Cutter']
    if '스위퍼' in 선택한구종들:
        선택구종 += ['Sweeper']
    if '커브' in 선택한구종들:
        선택구종 += ['Curveball']
    if '체인' in 선택한구종들:
        선택구종 += ['ChangeUp']
    if '포크' in 선택한구종들:
        선택구종 += ['Splitter']
    # 디버그
    선택구종_텍스트 = "('" + "','".join(선택구종) + "')"


#######################
# 선택 영역3: 플롯 옵션 선택
#######################
with 셀렉터구역1[4]:
    def 꾸미기2(str):
        색상 = {'개별': 'blue', '분포': 'red'}
        텍스트 = {'개별': '개별', '분포': '분포'}
        return f":{색상[str]}[{텍스트[str]}]"

    표시방식 = st.radio('VAA표시방법',
                        ['개별', '분포'],
                        index=1,
                        format_func=꾸미기2,
                        horizontal=True)

    _개별투구표시 = True if 표시방식 == '개별' else False


#######################
# 투수 데이터 로드
#######################
#### 선택한 투수 투구 데이터 가져오기
df = 투수데이터(선택한레벨, 선택한연도, 선택한투수ID, 날짜쿼리, 선택구종_텍스트)
#### 구종 평균 데이터 가져오기
리그평균 = 리그평균데이터(df)


#######################
# 플롯 그리기
#######################
#####
if len(df) > 0:
    title = f'{선택한투수이름}'
    if 선택한연도 != '전체':
        title += f' {선택한연도}'
    else:
        if len(df.year.unique()) > 1:
            title += f' {df.year.min()}-{df.year.max()}'
        else:
            title += f' {df.year.unique()[0]}'

    if 선택한레벨 != '전체':
        title += f' {선택한레벨}'
else:
    title = ''

set_fonts()
그림영역 = st.columns([3, 1])
with 그림영역[0]:
    fig_col = st.columns(4)
    with fig_col[0]:
        if len(df) > 0:
            dpi = 100
            plt.style.use('fivethirtyeight')
            fig, ax = plt.subplots(figsize=(5, 5), dpi=dpi)

            if ((퓨처스임 is False) &
                (len(df[df.Level == 'KBO']) > 0)) or (퓨처스임 is True):
                ax = vaa_plot(df,
                              futures=퓨처스임,
                              draw_dots=_개별투구표시,
                              draw_lg_avg=True,
                              lg_avg_df=리그평균,
                              freq_th=0,
                              ax=ax)

                if ax is not None:
                    if isinstance(ax, mpl.axes.Axes):
                        ax.set_title(title)
                st.pyplot(fig)
        else:
            st.markdown('데이터 없음')

    with fig_col[1]:
        상단 = df[df.PlateLocHeight >= 0.85]
        if len(상단) > 0:
            dpi = 100
            plt.style.use('fivethirtyeight')
            fig2, ax2 = plt.subplots(figsize=(5, 5), dpi=dpi)

            if ((퓨처스임 is False) &
                (len(상단[상단.Level == 'KBO']) > 0)) or (퓨처스임 is True):
                ax2 = vaa_plot(상단,
                               futures=퓨처스임,
                               draw_dots=_개별투구표시,
                               draw_lg_avg=True,
                               lg_avg_df=리그평균,
                               freq_th=0,
                               loc='top',
                               ax=ax2)

                if ax2 is not None:
                    if isinstance(ax2, mpl.axes.Axes):
                        ax2.set_title(f'{title} 상단')
                st.pyplot(fig2)
        else:
            st.markdown('데이터 없음')

    with fig_col[2]:
        중단 = df[df.PlateLocHeight.between(0.6, 0.85)]
        if len(중단) > 0:
            dpi = 100
            plt.style.use('fivethirtyeight')
            fig3, ax3 = plt.subplots(figsize=(5, 5), dpi=dpi)

            if ((퓨처스임 is False) &
                (len(중단[중단.Level == 'KBO']) > 0)) or (퓨처스임 is True):
                ax3 = vaa_plot(중단,
                               futures=퓨처스임,
                               draw_dots=_개별투구표시,
                               draw_lg_avg=True,
                               lg_avg_df=리그평균,
                               freq_th=0,
                               loc='mid',
                               ax=ax3)

                if ax3 is not None:
                    if isinstance(ax3, mpl.axes.Axes):
                        ax3.set_title(f'{title} 중단')
                st.pyplot(fig3)
        else:
            st.markdown('데이터 없음')

    with fig_col[3]:
        하단 = df[df.PlateLocHeight <= 0.6]
        if len(하단) > 0:
            dpi = 100
            plt.style.use('fivethirtyeight')
            fig3, ax3 = plt.subplots(figsize=(5, 5), dpi=dpi)

            if ((퓨처스임 is False) &
                (len(하단[하단.Level == 'KBO']) > 0)) or (퓨처스임 is True):
                ax3 = vaa_plot(하단,
                               futures=퓨처스임,
                               draw_dots=_개별투구표시,
                               draw_lg_avg=True,
                               lg_avg_df=리그평균,
                               freq_th=0,
                               loc='bot',
                               ax=ax3)

                if ax3 is not None:
                    if isinstance(ax3, mpl.axes.Axes):
                        ax3.set_title(f'{title} 하단')
                st.pyplot(fig3)
        else:
            st.markdown('데이터 없음')

설명영역 = st.columns(3)
with 설명영역[0]:
    with st.expander('상중하단 기준'):
        st.image('https://tangotiger.net/strikezone/zone%20chart.png')