import streamlit as st
import pandas as pd
import datetime
import sys, io, zipfile
from zoneinfo import ZoneInfo

from utils.codes import *
from utils.conn import *

##### 선수 정보 읽어오기
engine = get_conn()
query = 'select kbo_id, year(birth) 생년 from `master_meta`.player_info;'
pinfo = get_sql_df(query, engine, verbose=False)
pinfo_dict = {x: y for x, y in pinfo[['kbo_id', '생년']].values}

##### 박스스코어, 시즌기록 읽어오기
최소연도 = 2024

@st.cache_data(ttl=43200)
def load_data():
    query1 = """
SELECT *
FROM stats_logs.boxscore_pitcher
WHERE `level`='퓨처스';
    """
    query2 = """
SELECT *
FROM stats_logs.boxscore_hitter
WHERE `level`='퓨처스';
    """
    query3 = """
SELECT
name as 선수명,
kbo_id as pitcherID,
year as 연도,
team as 팀,
ERA, G, CG, SHO, W, L, SV, HLD, WPCT, TBF,
IP_STR as 이닝,
H, HR, BB, HBP, SO, R, ER, IP
FROM stats_logs.stats_pitcher
WHERE `level`='퓨처스';
    """
    query4 = """
SELECT
name as 선수명,
kbo_id as batterID,
year as 연도,
team as 팀,
`AVG` as BA,
G, PA, AB, R, H, `2B`, `3B`,
HR, TB, RBI, SB, CS, BB, HBP,
SO, GDP, SLG, OBP, E
FROM stats_logs.stats_hitter
WHERE `level`='퓨처스';
    """
    hitter_stats = get_sql_df(query4, engine)
    pitcher_stats = get_sql_df(query3, engine)
    hitter_bs = get_sql_df(query2, engine)
    pitcher_bs = get_sql_df(query1, engine)
    pitcher_stats = pitcher_stats.rename(columns={'year': '연도'})
    hitter_stats = hitter_stats.rename(columns={'year': '연도'})
    return pitcher_stats, hitter_stats, pitcher_bs, hitter_bs

####################
#### Main
####################
st.set_page_config(
    page_title = "퓨처스 팀별 포지션 정리",
    page_icon = "🧩",
    layout='wide',
)

st.markdown("##### 퓨처스 포지션 뎁스")


#### 트랙맨 파일 읽기
#### 연도: DataFrame 형식
pitcher_season_stat, batter_season_stat, pitcher_bs, batter_bs = load_data()


pitcher_bs = pitcher_bs.assign(연도 = pitcher_bs.game_id.apply(lambda x: int(x[:4])))
batter_bs = batter_bs.assign(연도 = batter_bs.game_id.apply(lambda x: int(x[:4])))
최대연도 = pitcher_bs.연도.max()

pitcher_bs = pitcher_bs.assign(나이 = pitcher_bs.연도 - pitcher_bs.pitcherID.apply(lambda x: pinfo_dict.get(x)))
batter_bs = batter_bs.assign(나이 = batter_bs.연도 - batter_bs.batterID.apply(lambda x: pinfo_dict.get(x)))

columns1 = st.columns(6)
with columns1[0]:
    teamSelect = st.selectbox("팀",
                              ["한화", "KIA", "KT", "LG", "NC", "SSG",
                               "두산", "롯데", "삼성", "키움", "상무"],
                              index=0)
with columns1[1]:
    seasonSelect = st.selectbox("연도",
                                list(range(최소연도, 최대연도+1))[::-1],
                                index=0)

if teamSelect == '키움':
    team_batter = batter_bs[(batter_bs.팀 == '고양') & (batter_bs.연도 == seasonSelect)]
    team_pitcher = pitcher_bs[(pitcher_bs.팀 == '고양') & (pitcher_bs.연도 == seasonSelect)]
else:
    team_batter = batter_bs[(batter_bs.팀 == teamSelect) & (batter_bs.연도 == seasonSelect)]
    team_pitcher = pitcher_bs[(pitcher_bs.팀 == teamSelect) & (pitcher_bs.연도 == seasonSelect)]

st.write(':red[:red-background[__"(포지션)" 붙지 않은 기록은 모두 시즌 전체 기록(포지션에 무관함)__]]')


batterTab, pitcherTab = st.tabs(['타자', '투수'])
batterColumns = ['선수명', '나이', 'G(포지션)', 'G(시즌)', '선발(포지션)', '타수', '실책',
                  '타율', '출루율', '장타율', 'OPS',
                  '안타', '홈런', '도루', '볼넷', '삼진', '포지션_출전_비중',
                  '타수(포지션)', '안타(포지션)', '홈런(포지션)', '도루(포지션)', '볼넷(포지션)', '삼진(포지션)',
                  '타율(포지션)', '장타율(포지션)']
pitcherColumns = ['선수명', '나이', '이닝', '출전', 'ERA', 'WHIP', 'K%', 'BB%', 'K/9', 'BB/9', '삼진', '볼넷', '홈런', '피안타']

with batterTab:
    posColumns1 = st.columns(3)
    posColumns2 = st.columns(3)
    posColumns3 = st.columns(3)

    with posColumns1[0]:
        st.markdown('### 1루수')
        if len(team_batter) == 0:
            st.markdown('데이터 없음')
        else:
            firstBasemen = team_batter[team_batter.pos3 > 0]
            pv_1B = firstBasemen.pivot_table(index=['선수명', 'batterID'],
                                             values=['날짜', 'AB', 'R', 'H', '2B', '3B', 'HR',
                                                     'RBI', 'SB', 'BB', 'HBP', 'SO', '선발', '나이'],
                                             aggfunc={
                                                 '날짜': 'count',
                                                 'AB': 'sum',
                                                 'R': 'sum',
                                                 'H': 'sum',
                                                 '2B': 'sum',
                                                 '3B': 'sum',
                                                 'HR': 'sum',
                                                 'RBI': 'sum',
                                                 'SB': 'sum',
                                                 'BB': 'sum',
                                                 'HBP': 'sum',
                                                 'SO': 'sum',
                                                 '선발': 'sum',
                                                 '나이': 'min'
                                             },
                                             fill_value=0).reset_index()
            pv_1B = pv_1B.rename(columns={'날짜': 'G'})
            pv_1B = pv_1B.assign(포지션_출전_비중 = pv_1B.G.apply(lambda x: f'{x / pv_1B.G.sum() *100:.0f}%'))
            pv_1B = pv_1B.assign(BA = pv_1B.H.div(pv_1B.AB),
                                 SLG = (pv_1B.H + pv_1B['2B'] +
                                        pv_1B['3B'].mul(2) + pv_1B['HR'].mul(3)).div(pv_1B.AB))
            temp_pv_1B = pd.merge(batter_season_stat[batter_season_stat.연도 == seasonSelect],
                                  pv_1B,
                                  on=['선수명', 'batterID'],
                                  suffixes=['_시즌', '_포지션'])
            temp_pv_1B = temp_pv_1B.assign(OPS = temp_pv_1B.OBP + temp_pv_1B.SLG_시즌)
            temp_pv_1B = temp_pv_1B.rename(columns = {'G_포지션': 'G(포지션)',
                                                      'G_시즌': 'G(시즌)',
                                                      '선발': '선발(포지션)',
                                                      'AB_시즌': '타수',
                                                      'H_시즌': '안타',
                                                      'HR_시즌': '홈런',
                                                      'SB_시즌': '도루',
                                                      'BB_시즌': '볼넷',
                                                      'SO_시즌': '삼진',
                                                      'BA_시즌': '타율',
                                                      'OBP': '출루율',
                                                      'SLG_시즌': '장타율',
                                                      'AB_포지션': '타수(포지션)',
                                                      'H_포지션': '안타(포지션)',
                                                      'HR_포지션': '홈런(포지션)',
                                                      'SB_포지션': '도루(포지션)',
                                                      'BB_포지션': '볼넷(포지션)',
                                                      'SO_포지션': '삼진(포지션)',
                                                      'BA_포지션': '타율(포지션)',
                                                      'SLG_포지션': '장타율(포지션)',
                                                      'E': '실책'}).sort_values('G(포지션)', ascending=False)
            st.dataframe(temp_pv_1B[batterColumns],
                         column_config={
                             "타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "출루율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "OPS": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                         },
                         hide_index=True)
    with posColumns1[1]:
        st.markdown('### 2루수')
        if len(team_batter) == 0:
            st.markdown('데이터 없음')
        else:
            secondBasemen = team_batter[team_batter.pos4 > 0]
            pv_2B = secondBasemen.pivot_table(index=['선수명', 'batterID'],
                                              values=['날짜', 'AB', 'R', 'H', '2B', '3B', 'HR',
                                                      'RBI', 'SB', 'BB', 'HBP', 'SO', '선발', '나이'],
                                              aggfunc={
                                                  '날짜': 'count',
                                                  'AB': 'sum',
                                                  'R': 'sum',
                                                  'H': 'sum',
                                                  '2B': 'sum',
                                                  '3B': 'sum',
                                                  'HR': 'sum',
                                                  'RBI': 'sum',
                                                  'SB': 'sum',
                                                  'BB': 'sum',
                                                  'HBP': 'sum',
                                                  'SO': 'sum',
                                                  '선발': 'sum',
                                                  '나이': 'min'
                                              },
                                              fill_value=0).reset_index()
            pv_2B = pv_2B.rename(columns={'날짜': 'G'})
            pv_2B = pv_2B.assign(포지션_출전_비중 = pv_2B.G.apply(lambda x: f'{x / pv_2B.G.sum() *100:.0f}%'))
            pv_2B = pv_2B.assign(BA = pv_2B.H.div(pv_2B.AB),
                                 SLG = (pv_2B.H + pv_2B['2B'] +
                                         pv_2B['3B'].mul(2) + pv_2B['HR'].mul(3)).div(pv_2B.AB))

            temp_pv_2B = pd.merge(batter_season_stat[batter_season_stat.연도 == seasonSelect],
                                  pv_2B,
                                  on=['선수명', 'batterID'],
                                  suffixes=['_시즌', '_포지션'])
            temp_pv_2B = temp_pv_2B.assign(OPS = temp_pv_2B.OBP + temp_pv_2B.SLG_시즌)
            temp_pv_2B = temp_pv_2B.rename(columns = {'G_포지션': 'G(포지션)',
                                                      'G_시즌': 'G(시즌)',
                                                      '선발': '선발(포지션)',
                                                      'AB_시즌': '타수',
                                                      'H_시즌': '안타',
                                                      'HR_시즌': '홈런',
                                                      'SB_시즌': '도루',
                                                      'BB_시즌': '볼넷',
                                                      'SO_시즌': '삼진',
                                                      'BA_시즌': '타율',
                                                      'OBP': '출루율',
                                                      'SLG_시즌': '장타율',
                                                      'AB_포지션': '타수(포지션)',
                                                      'H_포지션': '안타(포지션)',
                                                      'HR_포지션': '홈런(포지션)',
                                                      'SB_포지션': '도루(포지션)',
                                                      'BB_포지션': '볼넷(포지션)',
                                                      'SO_포지션': '삼진(포지션)',
                                                      'BA_포지션': '타율(포지션)',
                                                      'SLG_포지션': '장타율(포지션)',
                                                      'E': '실책'}).sort_values('G(포지션)', ascending=False)

            st.dataframe(temp_pv_2B[batterColumns],
                         column_config={
                             "타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "출루율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "OPS": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                         },
                         hide_index=True)
    with posColumns1[2]:
        st.markdown('### 3루수')
        if len(team_batter) == 0:
            st.markdown('데이터 없음')
        else:
            thirdBasemen = team_batter[team_batter.pos5 > 0]
            pv_3B = thirdBasemen.pivot_table(index=['선수명', 'batterID'],
                                             values=['날짜', 'AB', 'R', 'H', '2B', '3B', 'HR',
                                                     'RBI', 'SB', 'BB', 'HBP', 'SO', '선발', '나이'],
                                             aggfunc={
                                                 '날짜': 'count',
                                                 'AB': 'sum',
                                                 'R': 'sum',
                                                 'H': 'sum',
                                                 '2B': 'sum',
                                                 '3B': 'sum',
                                                 'HR': 'sum',
                                                 'RBI': 'sum',
                                                 'SB': 'sum',
                                                 'BB': 'sum',
                                                 'HBP': 'sum',
                                                 'SO': 'sum',
                                                 '선발': 'sum',
                                                 '나이': 'min'
                                             },
                                             fill_value=0).reset_index()
            pv_3B = pv_3B.rename(columns={'날짜': 'G'})
            pv_3B = pv_3B.assign(포지션_출전_비중 = pv_3B.G.apply(lambda x: f'{x / pv_3B.G.sum() *100:.0f}%'))
            pv_3B = pv_3B.assign(BA = pv_3B.H.div(pv_3B.AB),
                                 SLG = (pv_3B.H + pv_3B['2B'] +
                                         pv_3B['3B'].mul(2) + pv_3B['HR'].mul(3)).div(pv_3B.AB))

            temp_pv_3B = pd.merge(batter_season_stat[batter_season_stat.연도 == seasonSelect],
                                  pv_3B,
                                  on=['선수명', 'batterID'],
                                  suffixes=['_시즌', '_포지션'])
            temp_pv_3B = temp_pv_3B.assign(OPS = temp_pv_3B.OBP + temp_pv_3B.SLG_시즌)
            temp_pv_3B = temp_pv_3B.rename(columns = {'G_포지션': 'G(포지션)',
                                                      'G_시즌': 'G(시즌)',
                                                      '선발': '선발(포지션)',
                                                      'AB_시즌': '타수',
                                                      'H_시즌': '안타',
                                                      'HR_시즌': '홈런',
                                                      'SB_시즌': '도루',
                                                      'BB_시즌': '볼넷',
                                                      'SO_시즌': '삼진',
                                                      'BA_시즌': '타율',
                                                      'OBP': '출루율',
                                                      'SLG_시즌': '장타율',
                                                      'AB_포지션': '타수(포지션)',
                                                      'H_포지션': '안타(포지션)',
                                                      'HR_포지션': '홈런(포지션)',
                                                      'SB_포지션': '도루(포지션)',
                                                      'BB_포지션': '볼넷(포지션)',
                                                      'SO_포지션': '삼진(포지션)',
                                                      'BA_포지션': '타율(포지션)',
                                                      'SLG_포지션': '장타율(포지션)',
                                                      'E': '실책'}).sort_values('G(포지션)', ascending=False)

            st.dataframe(temp_pv_3B[batterColumns],
                         column_config={
                             "타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "출루율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "OPS": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                         },
                         hide_index=True)
    with posColumns2[0]:
        st.markdown('### 유격수')
        if len(team_batter) == 0:
            st.markdown('데이터 없음')
        else:
            shortstops = team_batter[team_batter.pos6 > 0]
            pv_SS = shortstops.pivot_table(index=['선수명', 'batterID'],
                                           values=['날짜', 'AB', 'R', 'H', '2B', '3B', 'HR',
                                                   'RBI', 'SB', 'BB', 'HBP', 'SO', '선발', '나이'],
                                           aggfunc={
                                               '날짜': 'count',
                                               'AB': 'sum',
                                               'R': 'sum',
                                               'H': 'sum',
                                               '2B': 'sum',
                                               '3B': 'sum',
                                               'HR': 'sum',
                                               'RBI': 'sum',
                                               'SB': 'sum',
                                               'BB': 'sum',
                                               'HBP': 'sum',
                                               'SO': 'sum',
                                               '선발': 'sum',
                                               '나이': 'min'
                                           },
                                           fill_value=0).reset_index()
            pv_SS = pv_SS.rename(columns={'날짜': 'G'})
            pv_SS = pv_SS.assign(포지션_출전_비중 = pv_SS.G.apply(lambda x: f'{x / pv_SS.G.sum() *100:.0f}%'))
            pv_SS = pv_SS.assign(BA = pv_SS.H.div(pv_SS.AB),
                                 SLG = (pv_SS.H + pv_SS['2B'] +
                                         pv_SS['3B'].mul(2) + pv_SS['HR'].mul(3)).div(pv_SS.AB))

            temp_pv_SS = pd.merge(batter_season_stat[batter_season_stat.연도 == seasonSelect],
                                  pv_SS,
                                  on=['선수명', 'batterID'],
                                  suffixes=['_시즌', '_포지션'])

            temp_pv_SS = temp_pv_SS.assign(OPS = temp_pv_SS.OBP + temp_pv_SS.SLG_시즌)
            temp_pv_SS = temp_pv_SS.rename(columns = {'G_포지션': 'G(포지션)',
                                                      'G_시즌': 'G(시즌)',
                                                      '선발': '선발(포지션)',
                                                      'AB_시즌': '타수',
                                                      'H_시즌': '안타',
                                                      'HR_시즌': '홈런',
                                                      'SB_시즌': '도루',
                                                      'BB_시즌': '볼넷',
                                                      'SO_시즌': '삼진',
                                                      'BA_시즌': '타율',
                                                      'OBP': '출루율',
                                                      'SLG_시즌': '장타율',
                                                      'AB_포지션': '타수(포지션)',
                                                      'H_포지션': '안타(포지션)',
                                                      'HR_포지션': '홈런(포지션)',
                                                      'SB_포지션': '도루(포지션)',
                                                      'BB_포지션': '볼넷(포지션)',
                                                      'SO_포지션': '삼진(포지션)',
                                                      'BA_포지션': '타율(포지션)',
                                                      'SLG_포지션': '장타율(포지션)',
                                                      'E': '실책'}).sort_values('G(포지션)', ascending=False)

            st.dataframe(temp_pv_SS[batterColumns],
                         column_config={
                             "타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "출루율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "OPS": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                         },
                         hide_index=True)
    with posColumns2[1]:
        st.markdown('### 포수')
        if len(team_batter) == 0:
            st.markdown('데이터 없음')
        else:
            catchers = team_batter[team_batter.pos2 > 0]
            pv_C = catchers.pivot_table(index=['선수명', 'batterID'],
                                        values=['날짜', 'AB', 'R', 'H', '2B', '3B', 'HR',
                                                'RBI', 'SB', 'BB', 'HBP', 'SO', '선발', '나이'],
                                        aggfunc={
                                            '날짜': 'count',
                                            'AB': 'sum',
                                            'R': 'sum',
                                            'H': 'sum',
                                            '2B': 'sum',
                                            '3B': 'sum',
                                            'HR': 'sum',
                                            'RBI': 'sum',
                                            'SB': 'sum',
                                            'BB': 'sum',
                                            'HBP': 'sum',
                                            'SO': 'sum',
                                            '선발': 'sum',
                                            '나이': 'min'
                                        },
                                        fill_value=0).reset_index()
            pv_C = pv_C.rename(columns={'날짜': 'G'})
            pv_C = pv_C.assign(포지션_출전_비중 = pv_C.G.apply(lambda x: f'{x / pv_C.G.sum() *100:.0f}%'))
            pv_C = pv_C.assign(BA = pv_C.H.div(pv_C.AB),
                               SLG = (pv_C.H + pv_C['2B'] +
                                       pv_C['3B'].mul(2) + pv_C['HR'].mul(3)).div(pv_C.AB))

            temp_pv_C = pd.merge(batter_season_stat[batter_season_stat.연도 == seasonSelect],
                                 pv_C,
                                 on=['선수명', 'batterID'],
                                 suffixes=['_시즌', '_포지션'])

            temp_pv_C = temp_pv_C.assign(OPS = temp_pv_C.OBP + temp_pv_C.SLG_시즌)
            temp_pv_C = temp_pv_C.rename(columns = {'G_포지션': 'G(포지션)',
                                                    'G_시즌': 'G(시즌)',
                                                    '선발': '선발(포지션)',
                                                    'AB_시즌': '타수',
                                                    'H_시즌': '안타',
                                                    'HR_시즌': '홈런',
                                                    'SB_시즌': '도루',
                                                    'BB_시즌': '볼넷',
                                                    'SO_시즌': '삼진',
                                                    'BA_시즌': '타율',
                                                    'OBP': '출루율',
                                                      'SLG_시즌': '장타율',
                                                      'AB_포지션': '타수(포지션)',
                                                      'H_포지션': '안타(포지션)',
                                                      'HR_포지션': '홈런(포지션)',
                                                      'SB_포지션': '도루(포지션)',
                                                      'BB_포지션': '볼넷(포지션)',
                                                      'SO_포지션': '삼진(포지션)',
                                                      'BA_포지션': '타율(포지션)',
                                                      'SLG_포지션': '장타율(포지션)',
                                                    'E': '실책'}).sort_values('G(포지션)', ascending=False)

            st.dataframe(temp_pv_C[batterColumns],
                         column_config={
                             "타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "출루율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "OPS": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                         },
                         hide_index=True)
    with posColumns3[0]:
        st.markdown('### 좌익수')
        if len(team_batter) == 0:
            st.markdown('데이터 없음')
        else:
            leftFielders = team_batter[team_batter.pos7 > 0]
            pv_LF = leftFielders.pivot_table(index=['선수명', 'batterID'],
                                             values=['날짜', 'AB', 'R', 'H', '2B', '3B', 'HR',
                                                     'RBI', 'SB', 'BB', 'HBP', 'SO', '선발', '나이'],
                                             aggfunc={
                                                 '날짜': 'count',
                                                 'AB': 'sum',
                                                 'R': 'sum',
                                                 'H': 'sum',
                                                 '2B': 'sum',
                                                 '3B': 'sum',
                                                 'HR': 'sum',
                                                 'RBI': 'sum',
                                                 'SB': 'sum',
                                                 'BB': 'sum',
                                                 'HBP': 'sum',
                                                 'SO': 'sum',
                                                 '선발': 'sum',
                                                 '나이': 'min'
                                             },
                                             fill_value=0).reset_index()
            pv_LF = pv_LF.rename(columns={'날짜': 'G'})
            pv_LF = pv_LF.assign(포지션_출전_비중 = pv_LF.G.apply(lambda x: f'{x / pv_LF.G.sum() *100:.0f}%'))
            pv_LF = pv_LF.assign(BA = pv_LF.H.div(pv_LF.AB),
                                 SLG = (pv_LF.H + pv_LF['2B'] +
                                         pv_LF['3B'].mul(2) + pv_LF['HR'].mul(3)).div(pv_LF.AB))

            temp_pv_LF = pd.merge(batter_season_stat[batter_season_stat.연도 == seasonSelect],
                                  pv_LF,
                                  on=['선수명', 'batterID'],
                                  suffixes=['_시즌', '_포지션'])

            temp_pv_LF = temp_pv_LF.assign(OPS = temp_pv_LF.OBP + temp_pv_LF.SLG_시즌)
            temp_pv_LF = temp_pv_LF.rename(columns = {'G_포지션': 'G(포지션)',
                                                      'G_시즌': 'G(시즌)',
                                                      '선발': '선발(포지션)',
                                                      'AB_시즌': '타수',
                                                      'H_시즌': '안타',
                                                      'HR_시즌': '홈런',
                                                      'SB_시즌': '도루',
                                                      'BB_시즌': '볼넷',
                                                      'SO_시즌': '삼진',
                                                      'BA_시즌': '타율',
                                                      'OBP': '출루율',
                                                      'SLG_시즌': '장타율',
                                                      'AB_포지션': '타수(포지션)',
                                                      'H_포지션': '안타(포지션)',
                                                      'HR_포지션': '홈런(포지션)',
                                                      'SB_포지션': '도루(포지션)',
                                                      'BB_포지션': '볼넷(포지션)',
                                                      'SO_포지션': '삼진(포지션)',
                                                      'BA_포지션': '타율(포지션)',
                                                      'SLG_포지션': '장타율(포지션)',
                                                      'E': '실책'}).sort_values('G(포지션)', ascending=False)

            st.dataframe(temp_pv_LF[batterColumns],
                         column_config={
                             "타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "출루율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "OPS": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                         },
                         hide_index=True)
    with posColumns3[1]:
        st.markdown('### 중견수')
        if len(team_batter) == 0:
            st.markdown('데이터 없음')
        else:
            centerFielders = team_batter[team_batter.pos8 > 0]
            pv_CF = centerFielders.pivot_table(index=['선수명', 'batterID'],
                                               values=['날짜', 'AB', 'R', 'H', '2B', '3B', 'HR',
                                                       'RBI', 'SB', 'BB', 'HBP', 'SO', '선발', '나이'],
                                               aggfunc={
                                                   '날짜': 'count',
                                                   'AB': 'sum',
                                                   'R': 'sum',
                                                   'H': 'sum',
                                                   '2B': 'sum',
                                                   '3B': 'sum',
                                                   'HR': 'sum',
                                                   'RBI': 'sum',
                                                   'SB': 'sum',
                                                   'BB': 'sum',
                                                   'HBP': 'sum',
                                                   'SO': 'sum',
                                                   '선발': 'sum',
                                                   '나이': 'min'
                                               },
                                               fill_value=0).reset_index()
            pv_CF = pv_CF.rename(columns={'날짜': 'G'})
            pv_CF = pv_CF.assign(포지션_출전_비중 = pv_CF.G.apply(lambda x: f'{x / pv_CF.G.sum() *100:.0f}%'))
            pv_CF = pv_CF.assign(BA = pv_CF.H.div(pv_CF.AB),
                                 SLG = (pv_CF.H + pv_CF['2B'] +
                                         pv_CF['3B'].mul(2) + pv_CF['HR'].mul(3)).div(pv_CF.AB))

            temp_pv_CF = pd.merge(batter_season_stat[batter_season_stat.연도 == seasonSelect],
                                  pv_CF,
                                  on=['선수명', 'batterID'],
                                  suffixes=['_시즌', '_포지션'])

            temp_pv_CF = temp_pv_CF.assign(OPS = temp_pv_CF.OBP + temp_pv_CF.SLG_시즌)
            temp_pv_CF = temp_pv_CF.rename(columns = {'G_포지션': 'G(포지션)',
                                                      'G_시즌': 'G(시즌)',
                                                      '선발': '선발(포지션)',
                                                      'AB_시즌': '타수',
                                                      'H_시즌': '안타',
                                                      'HR_시즌': '홈런',
                                                      'SB_시즌': '도루',
                                                      'BB_시즌': '볼넷',
                                                      'SO_시즌': '삼진',
                                                      'BA_시즌': '타율',
                                                      'OBP': '출루율',
                                                      'SLG_시즌': '장타율',
                                                      'AB_포지션': '타수(포지션)',
                                                      'H_포지션': '안타(포지션)',
                                                      'HR_포지션': '홈런(포지션)',
                                                      'SB_포지션': '도루(포지션)',
                                                      'BB_포지션': '볼넷(포지션)',
                                                      'SO_포지션': '삼진(포지션)',
                                                      'BA_포지션': '타율(포지션)',
                                                      'SLG_포지션': '장타율(포지션)',
                                                      'E': '실책'}).sort_values('G(포지션)', ascending=False)

            st.dataframe(temp_pv_CF[batterColumns],
                         column_config={
                             "타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "출루율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "OPS": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                         },
                         hide_index=True)
    with posColumns3[2]:
        st.markdown('### 우익수')
        if len(team_batter) == 0:
            st.markdown('데이터 없음')
        else:
            rightFielders = team_batter[team_batter.pos9 > 0]
            pv_RF = rightFielders.pivot_table(index=['선수명', 'batterID'],
                                              values=['날짜', 'AB', 'R', 'H', '2B', '3B', 'HR',
                                                      'RBI', 'SB', 'BB', 'HBP', 'SO', '선발', '나이'],
                                              aggfunc={
                                                  '날짜': 'count',
                                                  'AB': 'sum',
                                                  'R': 'sum',
                                                  'H': 'sum',
                                                  '2B': 'sum',
                                                  '3B': 'sum',
                                                  'HR': 'sum',
                                                  'RBI': 'sum',
                                                  'SB': 'sum',
                                                  'BB': 'sum',
                                                  'HBP': 'sum',
                                                  'SO': 'sum',
                                                  '선발': 'sum',
                                                  '나이': 'min'
                                              },
                                             fill_value=0).reset_index()
            pv_RF = pv_RF.rename(columns={'날짜': 'G'})
            pv_RF = pv_RF.assign(포지션_출전_비중 = pv_RF.G.apply(lambda x: f'{x / pv_RF.G.sum() *100:.0f}%'))
            pv_RF = pv_RF.assign(BA = pv_RF.H.div(pv_RF.AB),
                                 SLG = (pv_RF.H + pv_RF['2B'] +
                                         pv_RF['3B'].mul(2) + pv_RF['HR'].mul(3)).div(pv_RF.AB))

            temp_pv_RF = pd.merge(batter_season_stat[batter_season_stat.연도 == seasonSelect],
                                  pv_RF,
                                  on=['선수명', 'batterID'],
                                  suffixes=['_시즌', '_포지션'])

            temp_pv_RF = temp_pv_RF.assign(OPS = temp_pv_RF.OBP + temp_pv_RF.SLG_시즌)
            temp_pv_RF = temp_pv_RF.rename(columns = {'G_포지션': 'G(포지션)',
                                                      'G_시즌': 'G(시즌)',
                                                      '선발': '선발(포지션)',
                                                      'AB_시즌': '타수',
                                                      'H_시즌': '안타',
                                                      'HR_시즌': '홈런',
                                                      'SB_시즌': '도루',
                                                      'BB_시즌': '볼넷',
                                                      'SO_시즌': '삼진',
                                                      'BA_시즌': '타율',
                                                      'OBP': '출루율',
                                                      'SLG_시즌': '장타율',
                                                      'AB_포지션': '타수(포지션)',
                                                      'H_포지션': '안타(포지션)',
                                                      'HR_포지션': '홈런(포지션)',
                                                      'SB_포지션': '도루(포지션)',
                                                      'BB_포지션': '볼넷(포지션)',
                                                      'SO_포지션': '삼진(포지션)',
                                                      'BA_포지션': '타율(포지션)',
                                                      'SLG_포지션': '장타율(포지션)',
                                                      'E': '실책'}).sort_values('G(포지션)', ascending=False)

            st.dataframe(temp_pv_RF[batterColumns],
                         column_config={
                             "타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "출루율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "OPS": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                             "장타율(포지션)": st.column_config.NumberColumn(
                                 format='%.3f'
                             ),
                         },
                         hide_index=True)

with pitcherTab:
    pitColumns = st.columns(2)

    with pitColumns[0]:
        st.markdown('### 선발')
        if len(team_pitcher) == 0:
            st.markdown('데이터 없음')
        else:
            starter = team_pitcher[team_pitcher.등판 == '선발']
            pv_SP = starter.pivot_table(index=['선수명', 'pitcherID'],
                                        values=['날짜', 'IP', 'ER', 'H', 'HR',
                                                'SO', 'BB', 'TBF', '나이'],
                                        aggfunc={
                                            '날짜': 'count',
                                            'IP': 'sum',
                                            'ER': 'sum',
                                            'H': 'sum',
                                            'HR': 'sum',
                                            'SO': 'sum',
                                            'BB': 'sum',
                                            'TBF': 'sum',
                                            '나이': 'min'
                                        },
                                        fill_value=0).reset_index()
            pv_SP = pv_SP.assign(이닝 = pv_SP.IP.apply(lambda x: x//1 + (x%1 * 3 / 10)))
            pv_SP = pv_SP.assign(ERA = pv_SP.ER.div(pv_SP.IP).mul(9))
            pv_SP.insert(pv_SP.columns.to_list().index('ERA')+1,
                         'K%',
                         pv_SP.SO.div(pv_SP.TBF).mul(100))
            pv_SP.insert(pv_SP.columns.to_list().index('ERA')+2,
                         'BB%',
                         pv_SP.BB.div(pv_SP.TBF).mul(100))
            pv_SP.insert(pv_SP.columns.to_list().index('ERA')+3,
                         'K/9',
                         pv_SP.SO.div(pv_SP.IP).mul(9))
            pv_SP.insert(pv_SP.columns.to_list().index('ERA')+4,
                         'BB/9',
                         pv_SP.BB.div(pv_SP.IP).mul(9))
            pv_SP.insert(pv_SP.columns.to_list().index('ERA')+5,
                         'WHIP',
                         (pv_SP.H + pv_SP.BB).div(pv_SP.IP))
            pv_SP = pv_SP.rename(columns = {'날짜': '출전',
                                            'ER': '자책',
                                            'H': '피안타',
                                            'SO': '삼진',
                                            'HR': '홈런',
                                            'BB': '볼넷'}).sort_values('이닝', ascending=False)

            st.dataframe(pv_SP[pitcherColumns],
                         column_config={
                             "ERA": st.column_config.NumberColumn(
                                 format='%.2f'
                             ),
                             "K%": st.column_config.NumberColumn(
                                 format='%.1f'
                             ),
                             "BB%": st.column_config.NumberColumn(
                                 format='%.1f'
                             ),
                             "K/9": st.column_config.NumberColumn(
                                 format='%.1f'
                             ),
                             "BB/9": st.column_config.NumberColumn(
                                 format='%.1f'
                             ),
                             "WHIP": st.column_config.NumberColumn(
                                 format='%.2f'
                             ),
                             "이닝": st.column_config.NumberColumn(
                                 format='%.1f'
                             ),
                         },
                         hide_index=True)


    with pitColumns[1]:
        st.markdown('### 불펜')
        if len(team_pitcher) == 0:
            st.markdown('데이터 없음')
        else:
            reliever = team_pitcher[team_pitcher.등판 != '선발']
            pv_RP = reliever.pivot_table(index=['선수명', 'pitcherID'],
                                         values=['날짜', 'IP', 'ER', 'H', 'HR',
                                                 'SO', 'BB', 'TBF', '나이'],
                                         aggfunc={
                                             '날짜': 'count',
                                             'IP': 'sum',
                                             'ER': 'sum',
                                             'H': 'sum',
                                             'HR': 'sum',
                                             'SO': 'sum',
                                             'BB': 'sum',
                                             'TBF': 'sum',
                                             '나이': 'min'
                                         },
                                         fill_value=0).reset_index()
            pv_RP = pv_RP.assign(이닝 = pv_RP.IP.apply(lambda x: x//1 + (x%1 * 3 / 10)))
            pv_RP = pv_RP.assign(ERA = pv_RP.ER.div(pv_RP.IP).mul(9))
            pv_RP.insert(pv_RP.columns.to_list().index('ERA')+1,
                         'K%',
                         pv_RP.SO.div(pv_RP.TBF).mul(100))
            pv_RP.insert(pv_RP.columns.to_list().index('ERA')+2,
                         'BB%',
                         pv_RP.BB.div(pv_RP.TBF).mul(100))
            pv_RP.insert(pv_RP.columns.to_list().index('ERA')+3,
                         'K/9',
                         pv_RP.SO.div(pv_RP.IP).mul(9))
            pv_RP.insert(pv_RP.columns.to_list().index('ERA')+4,
                         'BB/9',
                         pv_RP.BB.div(pv_RP.IP).mul(9))
            pv_RP.insert(pv_RP.columns.to_list().index('ERA')+5,
                         'WHIP',
                         (pv_RP.H + pv_RP.BB).div(pv_RP.IP))
            pv_RP = pv_RP.rename(columns = {'날짜': '출전',
                                            'ER': '자책',
                                            'H': '피안타',
                                            'SO': '삼진',
                                            'HR': '홈런',
                                            'BB': '볼넷'}).sort_values('이닝', ascending=False)

            st.dataframe(pv_RP[pitcherColumns],
                         column_config={
                             "ERA": st.column_config.NumberColumn(
                                 format='%.2f'
                             ),
                             "K%": st.column_config.NumberColumn(
                                 format='%.1f'
                             ),
                             "BB%": st.column_config.NumberColumn(
                                 format='%.1f'
                             ),
                             "K/9": st.column_config.NumberColumn(
                                 format='%.1f'
                             ),
                             "BB/9": st.column_config.NumberColumn(
                                 format='%.1f'
                             ),
                             "WHIP": st.column_config.NumberColumn(
                                 format='%.2f'
                             ),
                             "이닝": st.column_config.NumberColumn(
                                 format='%.1f'
                             ),
                         },
                         hide_index=True)
