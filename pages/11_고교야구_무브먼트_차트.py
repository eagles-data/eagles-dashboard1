import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl

from utils.codes import *
from utils.plots import *
from utils.conn import *

dpi=100

st.set_page_config(
    page_title = "고교야구 무브먼트 플롯",
    page_icon = "🏫",
    layout='wide',
)
st.markdown("##### 고교야구 무브먼트 플롯")

engine = get_conn()
최대연도 = get_max_year(engine)

@st.cache_data(ttl=86400)
def load_data():
    query = """SELECT DISTINCT ht.pitcherid as tm_id,
coalesce(htim.player_name, ht.pitcher) AS pitcher_name
FROM raw_tracking.tm_hs ht
LEFT JOIN master_meta.player_info_hs_tmidmap htim ON ht.pitcherid = htim.tm_playerid
WHERE ht.pitcherid is not null;"""
    df = get_sql_df(query, engine, verbose=False)
    return df


def 투수게임날짜(연도=None,
                 투수ID=None):
    쿼리 = f"""SELECT distinct game_date, gameid
FROM raw_tracking.tm_hs
WHERE pitcherid={투수ID}
    """
    if 연도:
        쿼리 += f" AND year={연도}"
        
    df = get_sql_df(쿼리, engine, verbose=False)
    df['game_date'] = pd.to_datetime(df.game_date).dt.date

    return df


def 투수데이터(연도: int=None,
               투수ID: int=None,
               선택구종_텍스트: str=None):
    query = 'select year, PitcherId, Pitcher, PitcherThrows, BatterSide, Level, TaggedPitchType, '+\
            'PlateLocSide, PlateLocHeight, PitchCall, PlayResult, '+\
            'ExitSpeed, Angle, Strikes, Balls, Bearing, Distance, '+\
            'VertApprAngle, VertRelAngle, '+\
            'RelSpeed, SpinRate, InducedVertBreak, HorzBreak, '+\
            'RelHeight, Extension, PitchNo, GameID, game_date from raw_tracking.tm_hs '+\
            f'where pitcherid={투수ID} '+\
            f"and taggedpitchtype in {선택구종_텍스트} "+\
            "and taggedpitchtype not in ('Other', 'Undefined', 'Knuckleball') "

    if 연도:
        query += f' and year = {연도}'
    df = get_sql_df(query, engine, verbose=False)

    return df


def 리그평균데이터(df):
    #### 구종 평균 데이터 가져오기
    if len(df) > 0:
        구종목록 = df.TaggedPitchType.unique().tolist()
        구종목록 = [x for x in 구종목록 if x not in ('Other', 'Undefined', 'Knuckleball')]
        if len(구종목록) > 0:
            구종목록쿼리문자열 = "('" + "', '".join(구종목록) + "')"
        else:
            구종목록쿼리문자열 = f"('{구종목록}')"

        유니크_구종목록 = df.PitcherThrows.unique()
        던지는손쿼리문자열 = 유니크_구종목록[0]

        유니크_연도목록 = df.year.unique().tolist()
        if len(유니크_연도목록) > 0:
            연도쿼리문자열 = max(유니크_연도목록)
        else:
            연도쿼리문자열 = 유니크_연도목록[0]
        쿼리 = 'Select * from service_mart.season_pitchtype_agg_lg '+\
               f"where pthrows = '{던지는손쿼리문자열}' and "+\
               f"pitch_type in {구종목록쿼리문자열} "+\
               f"and year = {연도쿼리문자열};"

        구종DF = get_sql_df(쿼리, engine, verbose=False)

        return 구종DF
    else:
        return None


# 데이터 읽어오기
with st.spinner('loading data...'):
    idNames = load_data()

st.markdown('연도/리그/투수 선택')

셀렉터영역 = st.columns(9)
seasons = list(range(최대연도-4, 최대연도+1))[::-1]
최소시즌 = min(seasons)

with 셀렉터영역[0]:
    선택한연도 = st.selectbox(label="연도 선택",
                              options=['전체'] + seasons,
                              placeholder='...연도 선택',
                              index=1)
with 셀렉터영역[1]:
    팀선택 = st.selectbox(label = '팀 선택',
                          options = ['전체'] + list(고교야구팀들.keys()),
                          placeholder = '...팀 선택',
                          index=0)

    if 팀선택 !='전체':
        팀영문코드 = 고교야구팀들[팀선택]
    else:
        팀영문코드 = '전체'

# idNames 컬럼
# year,league,pitcherId,pitcher,pitcherthrows
이름_ID리스트 = idNames[['pitcher_name', 'tm_id']].values

투수이름_ID조합 = [f'{x[0]} ({x[1]})' for x in 이름_ID리스트]
# 한글 여부 판별 함수
def sort_key(word):
    # 첫 글자가 한글이면 우선순위 0, 아니면 1
    if '가' <= word[0] <= '힣':
        return (0, word)  # (우선순위, 단어)
    else:
        return (1, word)

투수이름_ID조합.sort(key=sort_key, reverse=False)

투수딕셔너리 = {f'{x[0]} ({x[1]})': [x[0], x[1]] for x in 이름_ID리스트}

with 셀렉터영역[2]:
    투수선택 = st.selectbox(label = "투수 선택",
                            options = 투수이름_ID조합,
                            placeholder = '...투수')

선택한투수이름 = 투수딕셔너리[투수선택][0]
선택한투수ID = 투수딕셔너리[투수선택][1]

#######################
# 경기 선택
#######################
with 셀렉터영역[3]:
    if 선택한투수ID:
        경기들 = 투수게임날짜(연도=선택한연도, 투수ID=선택한투수ID)
        경기일옵션 = [x[0] for x in 경기들.values]
        경기일옵션.sort(reverse=True)
        경기일옵션 = ['전체'] + 경기일옵션

        선택한경기날 = st.selectbox(label = '경기일 선택',
                                    options = 경기일옵션,
                                    placeholder = '...경기일 선택',
                                    index=0)


with 셀렉터영역[4]:
    def 꾸미기2(str):
        색상 = {'무브_투구1': 'blue', '무브_분포1': 'red'}
        텍스트 = {'무브_투구1': '개별', '무브_분포1': '분포'}
        return f":{색상[str]}[{텍스트[str]}]"

    무브먼트표시방식1 = st.radio('무브먼트',
                                 ['무브_투구1', '무브_분포1'],
                                 index=1,
                                 format_func=꾸미기2,
                                 horizontal=True)

    _개별투구표시1 = True if 무브먼트표시방식1 == '무브_투구1' else False


with 셀렉터영역[5]:
    def 꾸미기6(str):
        색상 = {'X': 'blue', 'O': 'red'}
        return f":{색상[str]}[{str}]"

    평균표시방식 = st.radio('1군 평균 표시',
                            ['X', 'O'],
                            index=1,
                            format_func=꾸미기6,
                            horizontal=True)

    _1군평균표시 = True if 평균표시방식 == 'O' else False


with 셀렉터영역[6]:
    def 꾸미기7(str):
        색상 = {'구사율': 'blue', '구종별': 'red'}
        return f":{색상[str]}[{str}]"

    표시방식 = st.radio('무브먼트 범위',
                        ['구사율', '구종별'],
                        index=1,
                        format_func=꾸미기7,
                        horizontal=True)
    _구사율로표시 = True if 표시방식 == '구사율' else False
        
with 셀렉터영역[7]:
    def 꾸미기8(str):
        색상 = {'개별': 'blue', '분포': 'red'}
        return f":{색상[str]}[{str}]"

    로케이션표시방식 = st.radio('로케이션',
                                ['개별', '분포'],
                                index=1,
                                format_func=꾸미기8,
                                horizontal=True)
    _분포표시 = True if 로케이션표시방식 == '분포' else False


with 셀렉터영역[-1]:
    ### 구종 체크박스
    구종옵션 = ['직구', '투심', '슬라', '커터', '스위퍼', '커브', '체인', '포크']

    선택한구종들 = st.pills("구종선택", 구종옵션, default=구종옵션, selection_mode="multi")

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


#### 선택한 투수 투구 데이터 가져오기
if 선택한투수ID is None:
    st.write('데이터 없음')
if 선택한투수ID:
    시즌전체데이터 = 투수데이터(연도=선택한연도,
                                투수ID=선택한투수ID,
                                선택구종_텍스트=선택구종_텍스트)
    if 시즌전체데이터 is None:
        st.markdown('데이터 없음')

    if 선택한경기날 != '전체':
        그날데이터 = 시즌전체데이터[시즌전체데이터.game_date == 선택한경기날]
    else:
        그날데이터 = 시즌전체데이터
    리그평균 = 리그평균데이터(시즌전체데이터)


#####
플롯영역 = st.columns([1, 1, 1, 1])

#######################
# 무브먼트
#######################
with 플롯영역[0]:
    if 선택한경기날 == '전체':
        st.markdown('**:red[시즌 전체]**')
    else:
        st.markdown(선택한경기날)
    if 시즌전체데이터 is None:
        st.markdown('데이터 없음')
    elif len(그날데이터) > 0:
        fig1, ax1 = plt.subplots(figsize=(5, 5), dpi=dpi)

        ax1 = movement_plot(그날데이터,
                            futures=True,
                            draw_dots=_개별투구표시1,
                            draw_usage=_구사율로표시,
                            draw_lg_avg=_1군평균표시,
                            lg_avg_df=리그평균,
                            freq_th=0,
                            eng=False,
                            ax=ax1)

        타이틀1 = f'{선택한투수이름}'
        if 선택한연도 != '전체':
            if 선택한경기날 == '전체':
                타이틀1 += f' {선택한연도}'
            else:
                타이틀1 += f" {선택한경기날.strftime('%Y/%m/%d')}"
        else:
            if len(시즌전체데이터.year.unique()) > 1:
                타이틀1 += f' {시즌전체데이터.year.min()}-{시즌전체데이터.year.max()}'
            else:
                타이틀1 += f' {시즌전체데이터.year.unique()[0]}'

        if ax1 is not None:
            if isinstance(ax1, mpl.axes.Axes):
                ax1.set_title(타이틀1)
        st.pyplot(fig1)
    else:
        st.markdown('데이터 없음')

#######################
# 로케이션
#######################
with 플롯영역[1]:
    if 시즌전체데이터 is None:
        st.markdown('데이터 없음')
    elif len(그날데이터) > 0:
        st.markdown(f"**vs 우타 {len(그날데이터[그날데이터.BatterSide == 'Right'])}구**")
        우타상대_로케이션 = 로케이션그리기(그날데이터, '우', _분포표시)
        타이틀3 = f'{선택한투수이름} vs 우타자'

        if len(그날데이터) == len(시즌전체데이터):
            if len(시즌전체데이터.year.unique()) > 1:
                타이틀3 += f'\n{시즌전체데이터.year.min()}-{시즌전체데이터.year.max()}'
            else:
                타이틀3 += f'\n{시즌전체데이터.year.unique()[0]}'
        else:
            타이틀3 += f"\n{선택한경기날}"

        if 우타상대_로케이션 is not None:
            if isinstance(우타상대_로케이션, mpl.figure.Figure):
                우타상대_로케이션.gca().set_title(타이틀3, fontsize=12)
        st.pyplot(우타상대_로케이션)

with 플롯영역[2]:
    if 시즌전체데이터 is None:
        st.markdown('데이터 없음')
    elif len(그날데이터) > 0:
        st.markdown(f"**vs 좌타 {len(그날데이터[그날데이터.BatterSide == 'Left'])}구**")
        좌타상대_로케이션 = 로케이션그리기(그날데이터, '좌', _분포표시)
        타이틀2 = f'{선택한투수이름} vs 좌타자'

        if len(그날데이터) == len(시즌전체데이터):
            if len(시즌전체데이터.year.unique()) > 1:
                타이틀2 += f'\n{시즌전체데이터.year.min()}-{시즌전체데이터.year.max()}'
            else:
                타이틀2 += f'\n{시즌전체데이터.year.unique()[0]}'
        else:
            타이틀2 += f"\n{선택한경기날}"

        if 좌타상대_로케이션 is not None:
            if isinstance(좌타상대_로케이션, mpl.figure.Figure):
                좌타상대_로케이션.gca().set_title(타이틀2, fontsize=12)
        st.pyplot(좌타상대_로케이션)

if len(시즌전체데이터) > 0:
    ### 테이블
    t = 시즌전체데이터.pivot_table(index='TaggedPitchType',
           values=['RelSpeed', 'SpinRate', 'InducedVertBreak', 'HorzBreak',
                   'RelHeight', 'Extension', 'PitchNo'],
           aggfunc={'RelSpeed': 'mean',
                    'SpinRate': 'mean',
                    'InducedVertBreak': 'mean',
                    'HorzBreak': 'mean',
                    'RelHeight': 'mean',
                    'Extension': 'mean',
                    'PitchNo': 'count'})
    g = 시즌전체데이터.groupby('TaggedPitchType')
    t = t.assign(비율 = t.PitchNo.div(t.PitchNo.sum()).mul(100))
    t = t.assign(구종 = t.index)
    t = t.assign(구종 = t.구종.apply(lambda x: 구종영문_한글로변환.get(x)))
    t = t.assign(구종 = t.구종.astype('category'))
    t = t.assign(구종 = t.구종.cat.set_categories(ptype_sortlist))
    t.insert(t.shape[1], '최고구속', g.RelSpeed.max())
    t = t.sort_values('구종')
    t = t.rename(columns = {
                            'RelSpeed': '구속',
                            'SpinRate': '회전수',
                            'InducedVertBreak': '수직무브',
                            'HorzBreak': '좌우무브',
                            'RelHeight': '릴리즈높이',
                            'Extension': '익스텐션',
                            'PitchNo': '투구수'
                            })
    st.dataframe(t[['구종', '투구수', '비율',
                    '구속', '최고구속', '회전수', '수직무브', '좌우무브',
                    '릴리즈높이', '익스텐션']],
                 hide_index=True,
                 width='content',
                 column_config={
                     "구속": st.column_config.NumberColumn(
                         format="%.1f"
                     ),
                     "최고구속": st.column_config.NumberColumn(
                         format="%.1f"
                     ),
                     "비율": st.column_config.NumberColumn(
                         format="%d%%"
                     ),
                     "회전수": st.column_config.NumberColumn(
                         format="%d"
                     ),
                     "수직무브": st.column_config.NumberColumn(
                         format="%.1f"
                     ),
                     "좌우무브": st.column_config.NumberColumn(
                         format="%.1f"
                     ),
                     "릴리즈높이": st.column_config.NumberColumn(
                         format="%.2f"
                     ),
                     "익스텐션": st.column_config.NumberColumn(
                         format="%.2f"
                     ),
                 })
else:
    st.markdown('데이터 없음')

