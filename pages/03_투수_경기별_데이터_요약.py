import streamlit as st
import pandas as pd
import numpy as np
import datetime, sys, math
from zoneinfo import ZoneInfo
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Ellipse
import matplotlib.gridspec as gridspec

from utils.codes import *
from utils.plots import *
from utils.conn import *

올해 = datetime.datetime.now(ZoneInfo('Asia/Seoul')).year
오늘 = datetime.datetime.now(ZoneInfo('Asia/Seoul'))

engine = get_conn()
최대연도 = get_max_year(engine)
연도목록 = get_season_list(engine)

컬럼표시설정 = {
    "구속": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "최고구속": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "비율": st.column_config.NumberColumn(
     label="%",
     format="%d%%"
    ),
    "회전수": st.column_config.NumberColumn(
     format="%d"
    ),
    "수직무브": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "좌우무브": st.column_config.NumberColumn(
     label="수평무브",
     format="%.1f"
    ),
    "릴리즈높이": st.column_config.NumberColumn(
     format="%.2f"
    ),
    "익스텐션": st.column_config.NumberColumn(
     format="%.2f"
    ),
    "스트%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "존%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "스윙%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "헛스윙%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "CSW%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "초구비율%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "초구스트%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "초구스윙%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "타구속도": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "땅볼%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "뜬공%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "라이너%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "팝업%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "강한타구%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "배럴타구%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "VRA": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "VAA": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "회전효율": st.column_config.NumberColumn(
     format="%d%%"
    ),
}


컬럼표시설정_영문 = {
    "Velo": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "Max": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "Usage": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "Spinrate": st.column_config.NumberColumn(
     format="%d"
    ),
    "IndVertBreak": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "HorzBreak": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "Rel.Height": st.column_config.NumberColumn(
     format="%.2f"
    ),
    "Extension": st.column_config.NumberColumn(
     format="%.2f"
    ),
    "Strike%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "Zone%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "Swing%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "Whiff%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "CSW%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "FirstPitch%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "FP.Strike%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "FP.Swing%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "Exit Velo": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "GB%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "FB%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "LD%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "PU%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "HardHit%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "Barrel%": st.column_config.NumberColumn(
     format="%d%%"
    ),
    "VRA": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "VAA": st.column_config.NumberColumn(
     format="%.1f"
    ),
    "SpinEfficiency": st.column_config.NumberColumn(
     format="%d%%"
    ),
}

테이블표시컬럼 = [
    #'구종',
    '투구수', '비율',
    '스트%', '존%', 
    '구속', '최고구속', '회전수', '수직무브', '좌우무브',
    '릴리즈높이', '익스텐션',
    '스윙%', '헛스윙%', 'CSW%', '초구비율%', '초구스트%', '초구스윙%',
    '인플레이', '피안타', '타구속도', '땅볼%', '뜬공%', '라이너%', '팝업%', '강한타구%', '배럴타구%',
    'VRA', 'VAA',
    '회전효율', '회전방향(무브기준)', '회전방향(실제)',
]

테이블표시컬럼_영문 = [
    #'Pitchtype',
    'Pitches', 'Usage',
    'Strike%', 'Zone%', 
    'Velo', 'Max', 'Spinrate', 'IndVertBreak', 'HorzBreak',
    'Rel.Height', 'Extension',
    'Swing%', 'Whiff%', 'CSW%', 'FirstPitch%', 'FP.Strike%', 'FP.Swing%',
    'Inplays', 'Hits', 'Exit Velo', 'GB%', 'FB%', 'LD%', 'PU%', 'HardHit%', 'Barrel%',
    'VRA', 'VAA',
    'SpinEfficiency', 'MovementBasedAxis', 'SpinBasedAxis',
]

테이블표시컬럼_타입 = {}
for 정수형컬럼 in ['투구수', '인플레이', '피안타', '회전수']:
    테이블표시컬럼_타입[정수형컬럼] = 'Int64'

for 실수형컬럼 in ['비율', '스트%', '존%', '구속', '최고구속',
                   '수직무브', '좌우무브',
                   '릴리즈높이', '익스텐션',
                   '스윙%', '헛스윙%', 'CSW%', '초구비율%', '초구스트%', '초구스윙%',
                   '타구속도', '땅볼%', '뜬공%', '라이너%', '팝업%', '강한타구%', '배럴타구%',
                   'VRA', 'VAA',
                   '회전효율',]:
    테이블표시컬럼_타입[실수형컬럼] = float
    
for 문자형컬럼 in ['회전방향(무브기준)', '회전방향(실제)',]:
    테이블표시컬럼_타입[문자형컬럼] = str


영문으로_컬럼바꾸기 = {x:y for (x, y) in zip(테이블표시컬럼, 테이블표시컬럼_영문)}
영문으로_컬럼바꾸기['구종'] = 'Type'

def 차트용테이블변환(df, 컬럼, ax=None, row_px=35, header_px=44, col_px=1.2, dpi=100, fontsize=36):
    ###################
    구종개수 = df.shape[0]
    n_rows = len(df)
    n_cols = len(df.columns)
    # 전체 figure 높이(인치) = (헤더 + 바디행수)*px / dpi
    fig_h_in = (header_px + n_rows * row_px) / dpi
    # 폭은 비율만 적당히(열 수 대비) 잡고, 실제 스트림릿에서 컨테이너폭으로 스케일링
    fig_w_in = max(6, n_cols * col_px)

    ###################
    # 리그 스탯에 없는 항목들
    # 최고구속, 초구비율%, 인플레이, 피안타, VRA, VAA
    # Max Velo, FirstPitch%, Inplays, Hits, VRA, VAA
    ###################

    df_fmt = df.copy()
    for col in ['비율', 'Usage']:
        if col in 컬럼:
            df_fmt[col] = (
                df_fmt[col]
                .round(0)  # 소수점 제거(반올림)
                .astype(int)  # int로 변환 (원하면 생략 가능)
                .astype(str) + '%'  # 문자열 변환, 뒤에 % 붙이기
            )
    for col in ['회전수', '투구수', '인플레이', '피안타',
                'Spinrate', 'Pitches', 'Inplay', 'Hits',]:
        if col in 컬럼:
            if df_fmt[col].isnull().all():
                df_fmt[col] = df_fmt[col].astype(str).replace({'nan': "", '<NA>': ""})
            elif df_fmt[col].isna().all():
                df_fmt[col] = df_fmt[col].astype(str).replace({'nan': "", '<NA>': ""})
            else:
                df_fmt[col] = df_fmt[col].round(0).astype(int)

    for col in ['스트%', '존%',
                '스윙%', '헛스윙%', 'CSW%', '초구비율%', '초구스트%', '초구스윙%',
                '땅볼%', '뜬공%', '라이너%', '팝업%', '강한타구%', '배럴타구%',
                '회전효율',
                'Strike%', 'Zone%',
                'Swing%', 'Whiff%', 'FirstPitch%', 'FP.Strike%', 'FP.Swing%',
                'GB%', 'FB%', 'LD%', 'PU%', 'HardHit%', 'Barrel%',
                'SpinEfficiency',]:
        if col in 컬럼:
            try:
                df_fmt[col] = df_fmt[col].fillna(-1).astype(int).replace({-1: None}).round(0)\
                                         .astype(str).map(lambda x: f"{x}%").replace({'None%': ""})
            except TypeError:
                df_fmt[col] = df_fmt[col].fillna(-1).astype(int).round(0)\
                                         .astype(str).map(lambda x: f"{x}%").replace({'-1%': ""})
                
    for col in ['회전방향(실제)',
                'SpinBasedAxis']:
        if col in 컬럼:
            df_fmt[col] = df_fmt[col].replace({'nan': ""})

    for col in ['구속', '최고구속',
                '수직무브', '좌우무브',
                '타구속도',
                'Velo', 'Max',
                'IndVertBreak', 'HorzBreak',
                'Exit Velo',
                'VRA', 'VAA',]:
        if col in 컬럼:
            try:
                df_fmt[col] = df_fmt[col].round(1).map(lambda x: f"{x:.1f}")
            except TypeError:
                df_fmt[col] = df_fmt[col].astype(float).round(1).map(lambda x: f"{x:.1f}")

    for col in ['릴리즈높이', '익스텐션',
                'Rel.Height', 'Extension',]:
        if col in 컬럼:
            try:
                df_fmt[col] = df_fmt[col].round(2).map(lambda x: f"{x:.2f}")
            except TypeError:
                df_fmt[col] = df_fmt[col].astype(float).round(2).map(lambda x: f"{x:.2f}")

    if ax is None:
        fig, ax = plt.subplots(figsize=(fig_w_in, fig_h_in), dpi=dpi)
    ax.axis('off')

    컬럼길이변환 = {
        '릴리즈높이': '릴리즈\n높이',
        '초구비율%': '초구\n비율%',
        '초구스트%': '초구\n스트%',
        '초구스윙%': '초구\n스윙%',
        '강한타구%': '강한\n타구%',
        '배럴타구%': '배럴\n타구%',
        '회전효율': '회전\n효율',
        '회전축3D': '회전축\n(3D)',
        '회전방향(무브기준)': '회전방향\n(무브기준)',
        '회전방향(실제)': '회전방향\n(실제)',
        'Rel.Height': 'Rel.\nHeight',
        'IndVertBreak': 'Ind.Vert\nBreak',
        'HorzBreak': 'Horz\nBreak',
        'Extension': 'Ext.',
        'FirstPitch%': 'First\nPitch%',
        'FP.Strike%': 'FP.\nStrike%',
        'FP.Swing%': 'FP.\nSwing%',
        'Exit Velo': 'Exit\nVelo',
        'HardHit%': 'Hard\nHit%',
        'SpinEfficiency': 'Spin\nEfficiency',
        'MovementBasedAxis': 'Spin Dir.\n(Look)',
        'SpinBasedAxis': 'Spin Dir.\n(Real)',
    }

    df_fmt.columns = [(lambda x: 컬럼길이변환.get(x) if x in 컬럼길이변환 else x)(x) for x in df_fmt.columns]
    컬럼 = [(lambda x: 컬럼길이변환.get(x) if x in 컬럼길이변환 else x)(x) for x in 컬럼]
    df_fmt = df_fmt.astype(object).mask(df_fmt == 'nan', '')

    table = ax.table(
        cellText=df_fmt[컬럼].values,
        colLabels=컬럼,
        cellLoc='center',
        loc='center'
    )
    # 셀 높이 강제 (인치)
    header_h_in = header_px / dpi
    row_h_in = row_px / dpi

    # 헤더(행 index 0), 바디(행 index 1..)
    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_height(header_h_in)
            cell.set_facecolor("#F0F2F6")           # 헤더 배경색 (Streamlit 기본 톤 비슷)
            cell.set_text_props(weight='bold')      # 헤더 볼드
        else:
            cell.set_height(row_h_in)
            # 홀짝 줄무늬 예시 (선택)
            if r % 2 == 1:
                cell.set_facecolor("white")
            else:
                cell.set_facecolor("#FAFAFA")

    # 표가 그림 영역을 넘지 않게 bbox 조정
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)

    # 여백 줄이기
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    return ax


def 연도별_리그_평균_가져오기(year: int=None):
    sql = f"""
        SELECT *
        FROM service_mart.season_pitchtype_agg_lg
    """
    if year is not None:
        sql += f' WHERE year={year}'
    else:
        sql += ' WHERE year >= 2021'
    df = get_sql_df(sql, engine)
    return df

구종별컬럼명바꾸기 = {
    'year': '연도',
    'pitch_type': '구종',
    'pthrows': '던지는손',
    'speed_mean': '구속',
    'spin_mean': '회전수',
    'hb_mean': '좌우무브',
    'ivb_mean': '수직무브',
    'ext_mean': '익스텐션',
    'relh_mean': '릴리즈높이',
    'ratio': '비율',
    'strike_pct': '스트%',
    'zone_pct': '존%',
    'swing_pct': '스윙%',
    'whiff_pct': '헛스윙%',
    'csw_pct': 'CSW%',
    'fp_strike_pct': '초구스트%', 
    'fp_swing_pct': '초구스윙%',
    'exit_velo': '타구속도',
    'gb_pct': '땅볼%',
    'fb_pct': '뜬공%',
    'ld_pct': '라이너%',
    'pu_pct': '팝업%',
    'hardhit_pct': '강한타구%',
    'barrel_pct': '배럴타구%',
}


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
    elif 레벨.lower() == 'regular':
        쿼리 = f"""
            SELECT distinct game_date, gameid
            FROM raw_tracking.tm
            WHERE pitcherid={투수ID}
            AND level in ('KBO', 'KBO Minors')
        """
    elif 레벨.lower() == 'postseason':
        쿼리 = f"""
            SELECT distinct game_date, gameid
            FROM raw_tracking.tm
            WHERE pitcherid={투수ID}
            AND league = 'KBOPostseason'
        """
    elif 레벨.lower() == 'regular and postseason':
        쿼리 = f"""
            SELECT distinct game_date, gameid
            FROM raw_tracking.tm
            WHERE pitcherid={투수ID}
            AND ((league = 'KBOPostseason') OR (`level` in ('KBO', 'KBO Minors')))
        """
    else:
        쿼리 = f"""
            SELECT distinct game_date, gameid
            FROM raw_tracking.tm
            WHERE pitcherid={투수ID}
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


def 투수박스스코어가져오기(레벨=None,
                           날짜=None,
                           투수ID: int=None,
                           영어: bool=False):
    if 날짜 == '전체':
        return None
    else:
        if 영어 is False:
            query = f"""
SELECT tn.team 상대팀, 이닝, 실점, 자책,
타자, 피안타, 삼진, 볼넷, 사구
FROM
(SELECT 이닝, 실점, 자책,
타자, 피안타, 삼진, 볼넷, 사구, team_name, team,
if (tn.team_code = substr(kgpl.game_id, 9, 2),
substr(kgpl.game_id, 9, 2), substr(kgpl.game_id, 11, 2)) 상대팀코드
            """
        else:
            query = f"""
SELECT tn.team_eng OPPO, IP, R, ER,
BF, H, K, BB, HBP
FROM
(SELECT 이닝 as IP, 실점 as R, 자책 as ER,
타자 as BF, 피안타 as H, 삼진 as K, 볼넷 as BB, 사구 as HBP, team_name, team,
if (tn.team_code = substr(kgpl.game_id, 9, 2),
substr(kgpl.game_id, 9, 2), substr(kgpl.game_id, 11, 2)) 상대팀코드
            """

        if (레벨 is None) or (레벨=='전체'):
            query += f"""FROM stats_logs.gamelog_pitcher kgpl, master_meta.team_info tn
WHERE tm_id={투수ID}
AND tn.team <> '고양'
AND tn.year = year(kgpl.tm_game_date)
AND tm_game_date='{날짜}') a, master_meta.team_info tn
WHERE a.상대팀코드 = tn.team_code
AND tn.year={날짜.year}
AND a.team = tn.team
AND a.team_name <> tn.team
    """
        elif 레벨 in ('정규', '포스트시즌', '정규+포시'):
            query += f"""FROM stats_logs.gamelog_pitcher kgpl, master_meta.team_info tn
WHERE tm_id={투수ID}
AND tn.team <> '고양'
AND tn.year = year(kgpl.tm_game_date)
AND kgpl.level in ('1군', '퓨처스')
AND tm_game_date='{날짜}') a, master_meta.team_info tn
WHERE a.상대팀코드 = tn.team_code
AND tn.year={날짜.year}
AND a.team = tn.team
AND a.team_name <> tn.team
    """
        else:
            query += f"""FROM stats_logs.gamelog_pitcher kgpl, master_meta.team_info tn
WHERE tm_id={투수ID}
AND tn.team <> '고양'
AND tn.year = year(kgpl.tm_game_date)
AND level='{레벨}'
AND tm_game_date='{날짜}') a, master_meta.team_info tn
WHERE a.상대팀코드 = tn.team_code
AND tn.year={날짜.year}
AND a.team = tn.team
AND a.team_name <> tn.team
    """

        df = get_sql_df(query, engine)
        return df


def 투수데이터(레벨=None,
               연도: int=None,
               투수ID: int=None,
               선택구종_텍스트: str=None):
    쿼리 = 'select year, PitcherId, Pitcher, PitcherThrows, BatterSide, Level, TaggedPitchType, '+\
           'PlateLocSide, PlateLocHeight, PitchCall, PitchResultGameDay, PlayResult, PAResultGameDay, '+\
           'ExitSpeed, Angle, Strikes, Balls, Bearing, Distance, '+\
           'VertApprAngle, VertRelAngle, '+\
           'RelSpeedGameDay, InducedVertBreakGameDay, HorzBreakGameDay, '+\
           'PlateLocSideGameDay, PlateLocHeightGameDay, '+\
           'RelSpeed, SpinRate, InducedVertBreak, HorzBreak, '+\
           'RelHeight, Extension, SpinAxis3dSpinEfficiency, SpinAxis, SpinAxis3dTransverseAngle, '+\
           'PitchNo, GameID, game_date '+\
           'from raw_tracking.tm '+\
           f'where pitcherid={투수ID} '+\
           f"and taggedpitchtype in {선택구종_텍스트} "+\
           "and taggedpitchtype not in ('Other', 'Undefined', 'Knuckleball') "+\
           "and stadium not in ('Gwangju', 'Pohang', 'Ulsan', 'Cheongju')"

    if 연도:
        쿼리 += f' and year = {연도}'

    if 레벨 == '1군':
        쿼리 += f" and level = 'KBO'"
    elif 레벨 == '퓨처스':
        쿼리 += f" and level = 'KBO Minors'"
    elif 레벨 == '시범':
        쿼리 += f" and level = 'Exhibition'"
    elif 레벨 == '정규':
        쿼리 += f" and level in ('KBO', 'KBO Minors')"
    elif 레벨 == '포스트시즌':
        쿼리 += f" and league = 'KBOPostseason'"
    elif 레벨 == '정규+포시':
        쿼리 += f" and ((league='KBOPostseason') or (level in ('KBO', 'KBO Minors')))"

    df = get_sql_df(쿼리, engine)
    df = df.assign(game_date = pd.to_datetime(df.game_date).dt.date)
    df = df.assign(strike = np.where(df.PitchCall.isin(['StrikeCalled', 'StrikeSwinging',
                                                        'InPlay', 'FoulBall', 'FoulBallNotFieldable',
                                                        'FoulBallFieldable']),
                                    1, 0),
                   first_pitch = np.where((df.Strikes == 0) & (df.Balls == 0), 1, 0),
                   fp_strike = np.where(df.PitchCall.isin(['StrikeCalled', 'StrikeSwinging',
                                                           'InPlay', 'FoulBall', 'FoulBallNotFieldable',
                                                           'FoulBallFieldable']),
                                np.where((df.Strikes == 0) & (df.Balls == 0), 1, 0), 0),
                   in_zone = np.where(df.PlateLocSide.between(-0.254, 0.254),
                                      np.where(df.PlateLocHeight.between(0.4572, 1.0), 1, 0),
                                      np.where(df.PlateLocSide.isnull(),
                                           np.where(df.PlateLocSideGameDay.between(-0.254, 0.254),
                                              np.where(df.PlateLocHeightGameDay.between(0.4572, 1.0), 1, 0), 0),
                                               0)
                                     ),
                   csw = np.where(df.PitchCall.isin(['StrikeCalled', 'StrikeSwinging']), 1, 0),
                   bip_ev = np.where((df.PitchCall == 'InPlay'),
                                      df.ExitSpeed, None),
                   hardhit = np.where((df.PitchCall == 'InPlay') &
                                      (df.ExitSpeed >= 153), 1, 0),
                   bip = np.where(df.PitchCall == 'InPlay', 1, 0),
                   hit = np.where(df.PlayResult.isin(['Single', 'Double', 'Triple', 'HomeRun']), 1,
                         np.where(df.PAResultGameDay.isin(['안타', '1루타', '내야안타', '번트 안타',
                                                           '2루타', '3루타', '홈런']), 1, 0)),
                   bip_EVLA = np.where((df.PitchCall == 'InPlay') &
                                     df.ExitSpeed.notnull() &
                                     df.Angle.notnull(), 1, 0),
                   swing = np.where(df.PitchCall.isin(['InPlay', 'FoulBall',
                                                       'FoulBallNotFieldable', 'FoulBallFieldable',
                                                       'StrikeSwinging']), 1,
                              np.where(df.PitchResultGameDay.isin(['타격', '파울', '번트파울',
                                                                   '번트헛스윙', '헛스윙']), 1, 0)),
                   fp_swing = np.where(df.PitchCall.isin(['InPlay', 'FoulBall',
                                                          'FoulBallNotFieldable', 'FoulBallFieldable',
                                                          'StrikeSwinging']),
                                       np.where((df.Strikes == 0) & (df.Balls == 0), 1, 0),
                                 np.where(df.PitchResultGameDay.isin(['타격', '파울', '번트파울',
                                                                      '번트헛스윙', '헛스윙']),
                                          np.where((df.Strikes == 0) & (df.Balls == 0), 1, 0), 0)),
                   contact = np.where(df.PitchCall.isin(['InPlay', 'FoulBall',
                                                         'FoulBallNotFieldable', 'FoulBallFieldable']), 1,
                              np.where(df.PitchResultGameDay.isin(['타격', '파울', '번트파울']), 1, 0)),
                   whiff = np.where(df.PitchCall == 'StrikeSwinging', 1, 0),
                   SpeedAngle_Code = np.where(df.PitchCall != 'InPlay', None,
                                     np.where(df.ExitSpeed.isnull(), None,
                                     np.where(df.Angle.isnull(), None,
                                     np.where(((df.ExitSpeed/1.609344 * 1.5 - df.Angle) >= 117)
                                              & ((df.ExitSpeed/1.609344 + df.Angle) >= 124)
                                              & (df.ExitSpeed/1.609344 >= 98)
                                              & (df.Angle >= 4) & (df.Angle <= 50), SACode.Barrel,
                                     np.where(((df.ExitSpeed/1.609344 * 1.5 - df.Angle) >= 111)
                                              & ((df.ExitSpeed/1.609344 + df.Angle) >= 119)
                                              & (df.ExitSpeed/1.609344 >= 95)
                                              & (df.Angle >= 0) & (df.Angle <= 52), SACode.SolidContact,
                                     np.where((df.ExitSpeed/1.609344 <= 59), SACode.PoorlyWeak,
                                     np.where(((df.ExitSpeed/1.609344 * 2 - df.Angle) >= 87)
                                              & (df.Angle <= 41)
                                              & ((df.ExitSpeed/1.609344 * 2 + df.Angle) <= 175)
                                              & ((df.ExitSpeed/1.609344 + df.Angle * 1.3) >= 89)
                                              & (df.ExitSpeed/1.609344 >= 59)
                                              & (df.ExitSpeed/1.609344 <= 72), SACode.FlareBurner,
                                     np.where(((df.ExitSpeed/1.609344 + df.Angle * 1.3) <= 112)
                                              & ((df.ExitSpeed/1.609344 + df.Angle * 1.55) >= 92)
                                              & (df.ExitSpeed/1.609344 >= 72)
                                              & (df.ExitSpeed/1.609344 <= 86), SACode.FlareBurner,
                                     np.where((df.Angle <= 20)
                                              & ((df.ExitSpeed/1.609344 + df.Angle * 2.4) >= 98)
                                              & (df.ExitSpeed/1.609344 >= 86)
                                              & (df.ExitSpeed/1.609344 <= 95), SACode.FlareBurner,
                                     np.where(((df.ExitSpeed/1.609344 - df.Angle) >= 76)
                                              & ((df.ExitSpeed/1.609344 + df.Angle * 2.4) >= 98)
                                              & (df.ExitSpeed/1.609344 >= 95)
                                              & (df.Angle <= 30), SACode.FlareBurner,
                                     np.where(((df.ExitSpeed/1.609344 + df.Angle * 2) >= 116),
                                              SACode.PoorlyUnder,
                                     np.where(((df.ExitSpeed/1.609344 + df.Angle * 2) <= 116),
                                              SACode.PoorlyTopped,
                                              SACode.Unclassified)))))))))))))
    df = df.assign(EVLA_BB_CLASS = np.where(df.SpeedAngle_Code.isin([SACode.Barrel, SACode.SolidContact]),
                                     np.where(df.Angle > 24, EVLABBClass.FB, EVLABBClass.LD),
                                   np.where(df.SpeedAngle_Code == SACode.FlareBurner,
                                     np.where(df.Angle > 24, EVLABBClass.FB,
                                     np.where(df.Angle > 10, EVLABBClass.LD,
                                     np.where(df.Angle < 6, EVLABBClass.GB,
                                     np.where(df.Angle > 0,
                                       np.where(df.Distance.isnull(), EVLABBClass.GB,
                                       np.where(df.Distance > 60, EVLABBClass.LD, EVLABBClass.GB)),
                                              EVLABBClass.GB)))),
                                   np.where(df.SpeedAngle_Code == SACode.PoorlyUnder,
                                     np.where(df.Angle < 24, EVLABBClass.LD,
                                     np.where(df.Angle < 30, EVLABBClass.FB,
                                     np.where((df.Angle > 50) & (df.Distance >= 60), EVLABBClass.FB,
                                     np.where((df.Angle > 50) & (df.Distance < 60), EVLABBClass.PU,
                                     np.where(df.Distance.isnull(), EVLABBClass.PU,
                                     np.where(df.Distance > 60, EVLABBClass.FB, EVLABBClass.PU)))))),
                                   np.where(df.SpeedAngle_Code == SACode.PoorlyTopped,
                                     np.where(df.Angle >= 10, EVLABBClass.LD, EVLABBClass.GB),
                                   np.where(df.SpeedAngle_Code == SACode.PoorlyWeak,
                                     np.where(df.Angle > 10, EVLABBClass.PU, EVLABBClass.GB),
                                     np.where(df.SpeedAngle_Code == SACode.Unclassified, EVLABBClass.UC, None)))))))

    df = df.assign(barrel = np.where(df.SpeedAngle_Code.isin([SACode.Barrel,
                                                              SACode.SolidContact]), 1, 0),
                   GB = np.where(df.EVLA_BB_CLASS == EVLABBClass.GB, 1, 0),
                   FB = np.where(df.EVLA_BB_CLASS == EVLABBClass.FB, 1, 0),
                   LD = np.where(df.EVLA_BB_CLASS == EVLABBClass.LD, 1, 0),
                   PU = np.where(df.EVLA_BB_CLASS == EVLABBClass.PU, 1, 0),
                  )

    return df


def 각도를시계로변환(각도):
    """
    각도를 시계 방향의 'HH:MM' 형식으로 변환합니다.

    Args:
        angle (float or int): 변환할 각도 (0 ~ 360).

    Returns:
        str: 'HH:MM' 형식의 문자열.
    """
    if math.isnan(각도):
        return f""
    else:
        # 각도를 0-360 범위로 정규화
        정규화된_각도 = 각도 % 360

        # 각도를 시계 방향 시간으로 변환
        # 180도 -> 12시, 270도 -> 3시, 360도 -> 6시, 90도 -> 9시
        시계방향_각도 = (180 + 정규화된_각도) % 360
        # 15분 단위로만 각도를 표시
        시계방향_각도2 = round(시계방향_각도 / 7.5) * 7.5

        # 총 분으로 변환 (360도 = 12시간 * 60분 = 720분)
        분단위_변환결과 = (시계방향_각도2 / 360) * 720

        # 시(hour)와 분(minute) 계산
        시침 = int(분단위_변환결과 // 60)
        분침 = int(분단위_변환결과 % 60)

        # 'HH:MM' 형식으로 포맷팅
        return f"{시침:2d}:{분침:02d}"


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

        구종DF = get_sql_df(쿼리, engine)

        return 구종DF
    else:
        return None




def 구종색상범례_문자열생성(구종색상딕셔너리,
                            영문:bool = False):
    # 텍스트를 담을 HTML 문자열 생성
    html_string = "<div style='text-align: center;'>" # 전체를 중앙 정렬하는 div

    if 영문 is False:
        for key in ptype_sortlist:
            if key in 구종색상딕셔너리:
                color_code = 구종색상딕셔너리[key]
                html_string += f'<span style="color: {color_code}; font-size: 1em; vertical-align: middle; line-height: 1;">&#9679;</span>'+\
                               f'<span style="color: {color_code}; font-size: 1em; font-weight: bold; margin-right: 15px; vertical-align: middle; line-height: 1;">{key}</span>'
    else:
        for key in pitchtype_sortlist:
            if key in 구종색상딕셔너리:
                color_code = 구종색상딕셔너리[key]
                html_string += f'<span style="color: {color_code}; font-size: 1em; vertical-align: middle; line-height: 1;">&#9679;</span>'+\
                               f'<span style="color: {color_code}; font-size: 1em; font-weight: bold; margin-right: 15px; vertical-align: middle; line-height: 1;">{key}</span>'

    # &#9679;는 검정색 원(●)의 HTML 엔티티 코드입니다.
    # font-size를 조절하여 원과 텍스트의 크기를 맞춥니다.
    # margin-right로 각 아이템 사이에 간격을 줍니다.

    html_string += "</div>" # div 닫기
    return html_string


#######################
# 메인 영역
#######################

st.set_page_config(
    page_title = "투수 경기별 데이터 요약",
    page_icon = "📝",
    layout='wide',
)
st.markdown("##### 투수 경기별 데이터요약")

dpi = 100
plt.style.use('fivethirtyeight')
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

셀렉터구역1 = st.columns(9)
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
                              options = ('전체', '1군', '퓨처스', '정규', '포스트시즌', '정규+포시', '시범'),
                              placeholder = '...레벨 선택',
                              index=0)
    레벨 = 레벨영어변환[선택한레벨]

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
    if 선택한연도 == 올해:
        제일끝날짜 = 오늘.date()
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
    def 꾸미기1(str):
        색상 = {'한글': 'blue', '영어': 'red'}
        return f":{색상[str]}[{str}]"

    한글영문 = st.radio("언어", ['한글', '영어'],
                        index=0,
                        format_func=꾸미기1,
                        horizontal=True)

#######################
# 선택 영역3: 플롯 옵션 선택
#######################
_샘플표시 = False

with 셀렉터구역1[4]:
    def 꾸미기2(str):
        색상 = {'무브_투구1': 'blue', '무브_분포1': 'red'}
        텍스트 = {'무브_투구1': '개별', '무브_분포1': '분포'}
        return f":{색상[str]}[{텍스트[str]}]"

    무브먼트표시방식1 = st.radio('무브먼트(전체)',
                                 ['무브_투구1', '무브_분포1'],
                                 index=1,
                                 format_func=꾸미기2,
                                 horizontal=True)

    _개별투구표시1 = True if 무브먼트표시방식1 == '무브_투구1' else False

    def 꾸미기3(str):
        색상 = {'샘플_전체1': 'blue', '샘플_샘플1': 'red'}
        텍스트 = {'샘플_전체1': '전체', '샘플_샘플1': '샘플'}
        return f":{색상[str]}[{텍스트[str]}]"

    샘플표시방식1 = st.radio('100구 샘플(전체)',
                             ['샘플_전체1', '샘플_샘플1'],
                             index=1,
                             format_func=꾸미기3,
                             disabled=(_개별투구표시1 is False),
                             horizontal=True)

    _샘플표시 = True if 샘플표시방식1 == '샘플_샘플1' else False

with 셀렉터구역1[5]:
    def 꾸미기4(str):
        색상 = {'무브_투구2': 'blue', '무브_분포2': 'red'}
        텍스트 = {'무브_투구2': '개별', '무브_분포2': '분포'}
        return f":{색상[str]}[{텍스트[str]}]"

    무브먼트표시방식2 = st.radio('무브먼트(경기)',
                                 ['무브_투구2', '무브_분포2'],
                                 index=0,
                                 format_func=꾸미기4,
                                 horizontal=True)

    _개별투구표시2 = True if 무브먼트표시방식2 == '무브_투구2' else False

    def 꾸미기5(str):
        색상 = {'cm/m': 'blue', 'in/ft': 'red'}
        return f":{색상[str]}[{str}]"

    단위방식 = st.radio('단위',
                        ['cm/m', 'in/ft'],
                        index=0,
                        format_func=꾸미기5,
                        horizontal=True)

    _단위_미터 = True if 단위방식 == 'cm/m' else False

with 셀렉터구역1[6]:
    def 꾸미기6(str):
        색상 = {'X': 'blue', 'O': 'red'}
        return f":{색상[str]}[{str}]"

    평균표시방식 = st.radio('1군 평균 표시',
                            ['X', 'O'],
                            index=1,
                            format_func=꾸미기6,
                            horizontal=True)

    _1군평균표시 = True if 평균표시방식 == 'O' else False

    if (_1군평균표시 is True) or (_샘플표시 is False):
        def 꾸미기7(str):
            색상 = {'구사율': 'blue', '구종별': 'red'}
            return f":{색상[str]}[{str}]"

        표시방식 = st.radio('무브먼트 범위',
                            ['구사율', '구종별'],
                            index=1,
                            format_func=꾸미기7,
                            horizontal=True)
        _구사율로표시 = True if 표시방식 == '구사율' else False
    else:
        _구사율로표시 = False

with 셀렉터구역1[7]:
    def 꾸미기8(str):
        색상 = {'개별': 'blue', '분포': 'red'}
        return f":{색상[str]}[{str}]"

    로케이션표시방식 = st.radio('로케이션',
                                ['개별', '분포'],
                                index=1,
                                format_func=꾸미기8,
                                horizontal=True)
    _분포표시 = True if 로케이션표시방식 == '분포' else False

    def 꾸미기9(str):
        색상 = {'없음': 'blue', 'HITS식': 'red'}
        return f":{색상[str]}[{str}]"

    구종마커표시방식 = st.radio('구종 마커',
                                ['없음', 'HITS식'],
                                index=1,
                                format_func=꾸미기9,
                                horizontal=True)

    _구종별마커표시 = True if 구종마커표시방식 == 'HITS식' else False

#######################
# 선택 영역4: 구종 옵션 선택
#######################

with 셀렉터구역1[-1]:
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



#######################
# 영역4: 플롯
#######################

박스스코어 = 투수박스스코어가져오기(선택한레벨,
                                    선택한경기날,
                                    선택한투수ID,
                                    영어=(한글영문 == '영어'))
if 박스스코어 is not None:
    css_style = """
    <style>
      .center-table {
        margin-left: auto;
        margin-right: auto;
      }
    </style>
    """
    # .center-table 클래스를 table 태그에 추가합니다.
    # to_html()에 classes='center-table' 옵션을 사용하여 클래스를 추가할 수 있습니다.

    html_table_with_class = 박스스코어.to_html(index=False, classes='center-table')

    st.markdown(css_style, unsafe_allow_html=True)
    st.markdown(html_table_with_class, unsafe_allow_html=True)

플롯영역 = st.columns([1, 1, 1, 1, 1, 1])

if 선택한투수ID is None:
    st.write('데이터 없음')
if 선택한투수ID:
    시즌전체데이터 = 투수데이터(레벨=선택한레벨,
                                연도=선택한연도,
                                투수ID=선택한투수ID,
                                선택구종_텍스트=선택구종_텍스트)
    if 시즌전체데이터 is None:
        st.markdown('데이터 없음')
    if 선택한경기날 != '전체':
        그날데이터 = 시즌전체데이터[시즌전체데이터.game_date == 선택한경기날]
    else:
        그날데이터 = 시즌전체데이터[(시즌전체데이터.game_date >= 앞날짜) &
                                    (시즌전체데이터.game_date <= 뒷날짜)]

    리그평균 = 리그평균데이터(시즌전체데이터)

    # 혹시 모를 영어이름용
    if len(시즌전체데이터) > 0:
        영어이름원본 = 시즌전체데이터.Pitcher.unique()[0]
        부분 = [part.strip() for part in 영어이름원본.split(',')]

        # 리스트의 순서를 바꾸어 '이름 성' 형태로 만듭니다.
        # join()을 사용하여 공백으로 연결합니다.
        영어이름 = ' '.join(reversed(부분))
    else:
        영어이름 = 선택한투수

    #######################
    # 시즌 전체 무브먼트 플롯
    #######################
    with 플롯영역[2]:
        if 한글영문 == '한글':
            st.markdown('**:red[시즌 전체]**')
        else:
            st.markdown('**:red[All]**')
        if 한글영문 == '영어':
            타이틀1 = 영어이름
        else:
            타이틀1 = 선택한투수이름

        if 선택한연도 != '전체':
            타이틀1 += f' {선택한연도}'
        else:
            if 시즌전체데이터 is not None and len(시즌전체데이터) > 0:
                if len(시즌전체데이터.year.unique()) > 1:
                    타이틀1 += f' {시즌전체데이터.year.min()}-{시즌전체데이터.year.max()}'
                else:
                    타이틀1 += f' {시즌전체데이터.year.unique()[0]}'
            else:
                타이틀1 += '전체'

        if 선택한레벨 != '전체':
            타이틀1 += f' {선택한레벨}'

        if 시즌전체데이터 is None:
            st.markdown('데이터 없음')
        elif len(시즌전체데이터) > 0:
            fig1, ax1 = plt.subplots(figsize=(5, 5), dpi=dpi)
            if 선택한레벨 != '1군':
                퓨처스임 = True
            else:
                퓨처스임 = False

            if ((퓨처스임 is False) &
                (len(시즌전체데이터[시즌전체데이터.Level == 'KBO']) > 0)) or (퓨처스임 is True):
                ax1 = movement_plot(시즌전체데이터,
                                    futures=퓨처스임,
                                    draw_dots=_개별투구표시1,
                                    sample_dots=_샘플표시,
                                    draw_usage=_구사율로표시,
                                    draw_lg_avg=_1군평균표시,
                                    lg_avg_df=리그평균,
                                    freq_th=0,
                                    eng=(한글영문 == '영어'),
                                    ax=ax1)

                if ax1 is not None:
                    if isinstance(ax1, mpl.axes.Axes):
                        ax1.set_title(타이틀1)
                st.pyplot(fig1)
        else:
            st.markdown('데이터 없음')

    #######################
    # 선택한 경기 무브먼트 플롯
    #######################
    with 플롯영역[3]:
        if 한글영문 == '영어':
            타이틀2 = 영어이름
        else:
            타이틀2 = 선택한투수이름
        if 시즌전체데이터 is not None and len(시즌전체데이터) > 0:
            if len(그날데이터) == len(시즌전체데이터):
                if len(시즌전체데이터.year.unique()) > 1:
                    타이틀2 += f' {시즌전체데이터.year.min()}-{시즌전체데이터.year.max()}'
                    st.markdown(f'**{시즌전체데이터.year.min()}-{시즌전체데이터.year.max()}**')
                else:
                    타이틀2 += f' {시즌전체데이터.year.unique()[0]}'
                    if 한글영문 == '영어':
                        st.markdown(f'**{시즌전체데이터.year.unique()[0]} Season**')
                    else:
                        st.markdown(f'**{시즌전체데이터.year.unique()[0]} 시즌**')
            elif len(그날데이터.game_date.unique()) >= 1:
                if 선택한경기날 == '전체':
                    st.markdown(f"**{앞날짜텍스트} - {뒷날짜텍스트}**")
                    타이틀2 += f" {앞날짜텍스트} - {뒷날짜텍스트}"
                else:
                    st.markdown(f"**{선택한경기날}**")
                    타이틀2 += f" {선택한경기날}"
        else:
            st.markdown(f"**{선택한경기날}**")
            타이틀2 += f" {선택한경기날}"

        if 그날데이터 is None:
            st.markdown('데이터 없음')
        elif len(그날데이터) > 0:
            fig2, ax2 = plt.subplots(figsize=(5, 5), dpi=dpi)

            ax2 = movement_plot(그날데이터,
                                futures=퓨처스임,
                                draw_dots=_개별투구표시2,
                                sample_dots=False,
                                draw_usage=_구사율로표시,
                                draw_lg_avg=_1군평균표시,
                                lg_avg_df=리그평균,
                                freq_th=0,
                                eng=(한글영문 == '영어'),
                                ax=ax2)

            if ax2 is not None:
                if isinstance(ax2, mpl.axes.Axes):
                    ax2.set_title(타이틀2)
            st.pyplot(fig2)

    #######################
    # 선택한 경기 vs좌타자 로케이션
    #######################
    with 플롯영역[1]:
        if 그날데이터 is None:
            st.markdown('데이터 없음')
        elif len(그날데이터) > 0:
            if 한글영문 == '한글':
                st.markdown(f"**vs 좌타 {len(그날데이터[그날데이터.BatterSide == 'Left'])}구**")
            else:
                st.markdown(f"**vs LHH {len(그날데이터[그날데이터.BatterSide == 'Left'])} Pitches**")
            좌타상대_로케이션 = 로케이션그리기(그날데이터, '좌', _분포표시, _구종별마커표시)
            if 한글영문 == '한글':
                타이틀3 = f'{선택한투수이름} vs 좌타자'
            else:
                타이틀3 = f'vs LHH'

            if len(그날데이터) == len(시즌전체데이터):
                if len(시즌전체데이터.year.unique()) > 1:
                    타이틀3 += f'\n{시즌전체데이터.year.min()}-{시즌전체데이터.year.max()}'
                else:
                    타이틀3 += f'\n{시즌전체데이터.year.unique()[0]}'
            elif len(그날데이터.game_date.unique()) > 1:
                타이틀3 += f"\n{앞날짜텍스트} - {뒷날짜텍스트}"
            elif 선택한경기날 == '전체':
                타이틀3 += f"\n{앞날짜텍스트} - {뒷날짜텍스트}"
            else:
                타이틀3 += f"\n{선택한경기날}"

            if 좌타상대_로케이션 is not None:
                if isinstance(좌타상대_로케이션, mpl.figure.Figure):
                    좌타상대_로케이션.gca().set_title(타이틀3, fontsize=12)
            st.pyplot(좌타상대_로케이션)


    #######################
    # 선택한 경기 vs우타자 로케이션
    #######################
    with 플롯영역[4]:
        if 그날데이터 is None:
            st.markdown('데이터 없음')
        elif len(그날데이터) > 0:
            if 한글영문 == '한글':
                st.markdown(f"**vs 우타 {len(그날데이터[그날데이터.BatterSide == 'Right'])}구**")
            else:
                st.markdown(f"**vs RHH {len(그날데이터[그날데이터.BatterSide == 'Right'])} Pitches**")
            우타상대_로케이션 = 로케이션그리기(그날데이터, '우', _분포표시, _구종별마커표시)
            if 한글영문 == '한글':
                타이틀4 = f'{선택한투수이름} vs 우타자'
            else:
                타이틀4 = f'vs RHH'

            if len(그날데이터) == len(시즌전체데이터):
                if len(시즌전체데이터.year.unique()) > 1:
                    타이틀4 += f'\n{시즌전체데이터.year.min()}-{시즌전체데이터.year.max()}'
                else:
                    타이틀4 += f'\n{시즌전체데이터.year.unique()[0]}'
            elif len(그날데이터.game_date.unique()) > 1:
                타이틀4 += f"\n{앞날짜텍스트} - {뒷날짜텍스트}"
            elif 선택한경기날 == '전체':
                타이틀4 += f"\n{앞날짜텍스트} - {뒷날짜텍스트}"
            else:
                타이틀4 += f"\n{선택한경기날}"

            if 우타상대_로케이션 is not None:
                if isinstance(우타상대_로케이션, mpl.figure.Figure):
                    우타상대_로케이션.gca().set_title(타이틀4, fontsize=12)
            st.pyplot(우타상대_로케이션)

if 한글영문 == '한글':
    구종색상 = {구종영문_한글로변환[구종]: ball_colors[구종] for 구종 in 시즌전체데이터.TaggedPitchType.unique()}
else:
    구종색상 = {구종: ball_colors[구종] for 구종 in 시즌전체데이터.TaggedPitchType.unique()}
범례 = 구종색상범례_문자열생성(구종색상, (한글영문=='영어'))

# Streamlit에 HTML 문자열을 Markdown으로 렌더링
st.write(범례, unsafe_allow_html=True)


#######################
# 데이터 요약 테이블 표시
#######################

테이블세팅 = st.columns([1, 12, 1])
with 테이블세팅[1]:
    if len(그날데이터) > 0:
        if len(그날데이터.game_date.unique()) > 1:
            st.markdown(f"**{앞날짜텍스트} - {뒷날짜텍스트}**")
        elif 선택한경기날 == '전체':
            st.markdown(f"**{앞날짜텍스트} - {뒷날짜텍스트}**")
        else:
            st.markdown(f"**{선택한경기날}**")
        지정기간평균 = 그날데이터.pivot_table(index='TaggedPitchType',
                                              values=['RelSpeed', 'SpinRate', 'InducedVertBreak', 'HorzBreak',
                                                      'RelHeight', 'Extension', 'PitchNo',
                                                      'VertApprAngle', 'VertRelAngle',
                                                      'strike', 'fp_strike', 'first_pitch',
                                                      'in_zone', 'csw', 'hardhit',
                                                      'bip', 'hit', 'bip_EVLA', 'swing', 'whiff',
                                                      'barrel', 'GB', 'FB', 'LD', 'PU', 'fp_swing', 'bip_ev',
                                                      'SpinAxis3dSpinEfficiency', 'SpinAxis', 'SpinAxis3dTransverseAngle', 
                                                     ],
                                              aggfunc={'RelSpeed': 'mean',
                                                       'SpinRate': 'mean',
                                                       'InducedVertBreak': 'mean',
                                                       'HorzBreak': 'mean',
                                                       'RelHeight': 'mean',
                                                       'Extension': 'mean',
                                                       'PitchNo': 'count',
                                                       'VertApprAngle': 'mean',
                                                       'VertRelAngle': 'mean',
                                                       'strike': 'sum', 'fp_strike': 'sum', 'first_pitch': 'sum',
                                                       'in_zone': 'sum', 'csw': 'sum',
                                                       'bip': 'sum', 'bip_EVLA': 'sum',
                                                       'swing': 'sum', 'whiff': 'sum',
                                                       'barrel': 'sum', 'hardhit': 'sum',
                                                       'GB': 'sum', 'FB': 'sum', 'LD': 'sum', 'PU': 'sum',
                                                       'fp_swing': 'sum', 'bip_ev': 'mean',
                                                       'hit': 'sum',
                                                       'SpinAxis3dSpinEfficiency': 'mean',
                                                       'SpinAxis': 'mean',
                                                       'SpinAxis3dTransverseAngle': 'mean',
                                                      })

        if 'SpinAxis3dSpinEfficiency' not in 지정기간평균.columns:
            null_df = pd.DataFrame(index=지정기간평균.index,
                                   columns=['SpinAxis3dSpinEfficiency'])
            지정기간평균 = pd.concat([지정기간평균, null_df], axis=1)
        if 'SpinAxis' not in 지정기간평균.columns:
            null_df = pd.DataFrame(index=지정기간평균.index,
                                   columns=['SpinAxis', 'MovementBasedAxis'])
            지정기간평균 = pd.concat([지정기간평균, null_df], axis=1)
            지정기간평균.MovementBasedAxis = 지정기간평균.MovementBasedAxis.astype(str)
        else:
            지정기간평균.insert(지정기간평균.shape[1], 'MovementBasedAxis', 지정기간평균.SpinAxis.apply(각도를시계로변환))
        if 'SpinAxis3dTransverseAngle' not in 지정기간평균.columns:
            null_df = pd.DataFrame(index=지정기간평균.index,
                                   columns=['SpinAxis3dTransverseAngle', 'SpinBasedAxis'])
            지정기간평균 = pd.concat([지정기간평균, null_df], axis=1)
            지정기간평균.SpinBasedAxis = 지정기간평균.SpinBasedAxis.astype(str).replace({'nan': None})
        else:
            지정기간평균.insert(지정기간평균.shape[1], 'SpinBasedAxis', 지정기간평균.SpinAxis3dTransverseAngle.apply(각도를시계로변환))
        g2 = 그날데이터.groupby('TaggedPitchType')
        지정기간평균 = 지정기간평균.assign(비율 = 지정기간평균.PitchNo.div(지정기간평균.PitchNo.sum()).mul(100))
        지정기간평균 = 지정기간평균.assign(구종 = 지정기간평균.index)
        지정기간평균 = 지정기간평균.assign(구종 = 지정기간평균.구종.apply(lambda x: 구종영문_한글로변환.get(x)))
        지정기간평균 = 지정기간평균.assign(구종 = 지정기간평균.구종.astype('category'))
        지정기간평균 = 지정기간평균.assign(구종 = 지정기간평균.구종.cat.set_categories(ptype_sortlist))
        지정기간평균 = 지정기간평균.assign(SpinAxis3dSpinEfficiency = 지정기간평균.SpinAxis3dSpinEfficiency.mul(100))
        지정기간평균 = 지정기간평균.sort_values('구종')
        지정기간평균.insert(지정기간평균.shape[1], '최고구속', g2.RelSpeed.max())
        지정기간평균 = 지정기간평균.rename(columns = {
            'RelSpeed': '구속',
            'SpinRate': '회전수',
            'InducedVertBreak': '수직무브',
            'HorzBreak': '좌우무브',
            'RelHeight': '릴리즈높이',
            'Extension': '익스텐션',
            'PitchNo': '투구수',
            'hardhit': '강한타구',
            'barrel': '배럴타구',
            'strike': '스트라이크',
            'in_zone': '인존',
            'whiff': '헛스윙',
            'first_pitch': '초구',
            'fp_strike': '초구스트',
            'fp_swing': '초구스윙',
            'swing': '스윙',
            'GB': '땅볼',
            'FB': '뜬공',
            'LD': '라이너',
            'PU': '팝업',
            'bip': '인플레이',
            'hit': '피안타',
            'bip_ev': '타구속도',
            'VertRelAngle': 'VRA',
            'VertApprAngle': 'VAA',
            'SpinAxis3dSpinEfficiency': '회전효율',
            'SpinAxis': '회전축',
            'SpinAxis3dTransverseAngle': '회전축3D',
            'MovementBasedAxis': '회전방향(무브기준)',
            'SpinBasedAxis': '회전방향(실제)',
        })
        지정기간평균.insert(지정기간평균.shape[1], '스트%', 지정기간평균.스트라이크.div(지정기간평균.투구수).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '존%', 지정기간평균.인존.div(지정기간평균.투구수).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '스윙%', 지정기간평균.스윙.div(지정기간평균.투구수).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '헛스윙%', 지정기간평균.헛스윙.div(지정기간평균.스윙).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], 'CSW%', 지정기간평균.csw.div(지정기간평균.투구수).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '초구비율%', 지정기간평균.초구.div(지정기간평균.초구.sum()).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '초구스트%', 지정기간평균.초구스트.div(지정기간평균.초구).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '초구스윙%', 지정기간평균.초구스윙.div(지정기간평균.초구스트).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '강한타구%', 지정기간평균.강한타구.div(지정기간평균.bip_EVLA).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '배럴타구%', 지정기간평균.배럴타구.div(지정기간평균.bip_EVLA).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '땅볼%', 지정기간평균.땅볼.div(지정기간평균.bip_EVLA).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '라이너%', 지정기간평균.라이너.div(지정기간평균.bip_EVLA).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '뜬공%', 지정기간평균.뜬공.div(지정기간평균.bip_EVLA).mul(100))
        지정기간평균.insert(지정기간평균.shape[1], '팝업%', 지정기간평균.팝업.div(지정기간평균.bip_EVLA).mul(100))

        if _단위_미터 is False:
            지정기간평균['구속'] = 지정기간평균.구속.div(1.609344)
            지정기간평균['최고구속'] = 지정기간평균.최고구속.div(1.609344)
            지정기간평균['수직무브'] = 지정기간평균.수직무브.div(2.54)
            지정기간평균['좌우무브'] = 지정기간평균.좌우무브.div(2.54)
            지정기간평균['릴리즈높이'] = 지정기간평균.릴리즈높이.div(0.3048)
            지정기간평균['익스텐션'] = 지정기간평균.익스텐션.div(0.3048)
            지정기간평균['타구속도'] = 지정기간평균.타구속도.div(1.609344)

        없는컬럼 = [x for x in 테이블표시컬럼 if x not in 지정기간평균.columns]
        if 없는컬럼 and len(없는컬럼) > 0:
            null_df = pd.DataFrame(index=지정기간평균.index,
                                   columns=없는컬럼)
            지정기간평균 = pd.concat([지정기간평균, null_df], axis=1)
            for col in 없는컬럼:
                지정기간평균[col] = 지정기간평균[col].astype(테이블표시컬럼_타입[col])

        if 한글영문 == '한글':
            st.dataframe(지정기간평균.set_index('구종')[테이블표시컬럼],
                         hide_index=False,
                         column_config=컬럼표시설정)
        else:
            지정기간평균['구종'] = 지정기간평균.구종.apply(lambda x: 구종한글_영문으로변환.get(x))
            st.dataframe(지정기간평균.rename(columns=영문으로_컬럼바꾸기).set_index('Type')[테이블표시컬럼_영문],
                         hide_index=False,
                         column_config=컬럼표시설정_영문)
    else:
        st.markdown('**데이터 없음**')

    if len(시즌전체데이터) > 0:
        if 한글영문 == '한글':
            st.markdown('**시즌 평균**')
        else:
            st.markdown('**Season Summary**')
        시즌전체평균 = 시즌전체데이터.pivot_table(index='TaggedPitchType',
                                                  values=['RelSpeed', 'SpinRate', 'InducedVertBreak', 'HorzBreak',
                                                          'RelHeight', 'Extension', 'PitchNo',
                                                          'VertApprAngle', 'VertRelAngle',
                                                          'strike', 'fp_strike', 'first_pitch',
                                                          'in_zone', 'csw', 'hardhit',
                                                          'bip', 'hit', 'bip_EVLA', 'swing', 'whiff',
                                                          'barrel', 'GB', 'FB', 'LD', 'PU', 'fp_swing', 'bip_ev',
                                                          'SpinAxis3dSpinEfficiency', 'SpinAxis', 'SpinAxis3dTransverseAngle', 
                                                         ],
                                                  aggfunc={'RelSpeed': 'mean',
                                                           'SpinRate': 'mean',
                                                           'InducedVertBreak': 'mean',
                                                           'HorzBreak': 'mean',
                                                           'RelHeight': 'mean',
                                                           'Extension': 'mean',
                                                           'PitchNo': 'count',
                                                           'VertApprAngle': 'mean',
                                                           'VertRelAngle': 'mean',
                                                           'strike': 'sum', 'fp_strike': 'sum', 'first_pitch': 'sum',
                                                           'in_zone': 'sum', 'csw': 'sum',
                                                           'bip': 'sum', 'bip_EVLA': 'sum',
                                                           'swing': 'sum', 'whiff': 'sum',
                                                           'barrel': 'sum', 'hardhit': 'sum',
                                                           'GB': 'sum', 'FB': 'sum', 'LD': 'sum', 'PU': 'sum',
                                                           'fp_swing': 'sum', 'bip_ev': 'mean',
                                                           'hit': 'sum',
                                                           'SpinAxis3dSpinEfficiency': 'mean',
                                                           'SpinAxis': 'mean',
                                                           'SpinAxis3dTransverseAngle': 'mean',
                                                          })

        if 'SpinAxis3dSpinEfficiency' not in 시즌전체평균.columns:
            null_df = pd.DataFrame(index=시즌전체평균.index,
                                   columns=['SpinAxis3dSpinEfficiency',])
            시즌전체평균 = pd.concat([시즌전체평균, null_df], axis=1)
        if 'SpinAxis' not in 시즌전체평균.columns:
            null_df = pd.DataFrame(index=시즌전체평균.index,
                                   columns=['SpinAxis', 'MovementBasedAxis'])
            시즌전체평균 = pd.concat([시즌전체평균, null_df], axis=1)
            시즌전체평균.MovementBasedAxis = 시즌전체평균.MovementBasedAxis.astype(str)
        else:
            시즌전체평균.insert(시즌전체평균.shape[1], 'MovementBasedAxis', 시즌전체평균.SpinAxis.apply(각도를시계로변환))
        if 'SpinAxis3dTransverseAngle' not in 시즌전체평균.columns:
            null_df = pd.DataFrame(index=시즌전체평균.index,
                                   columns=['SpinAxis3dTransverseAngle', 'SpinBasedAxis'])
            시즌전체평균 = pd.concat([시즌전체평균, null_df], axis=1)
            시즌전체평균.SpinBasedAxis = 시즌전체평균.SpinBasedAxis.astype(str).replace({'nan': None})
        else:
            시즌전체평균.insert(시즌전체평균.shape[1], 'SpinBasedAxis', 시즌전체평균.SpinAxis3dTransverseAngle.apply(각도를시계로변환))
        g1 = 시즌전체데이터.groupby('TaggedPitchType')
        시즌전체평균 = 시즌전체평균.assign(비율 = 시즌전체평균.PitchNo.div(시즌전체평균.PitchNo.sum()).mul(100))
        시즌전체평균 = 시즌전체평균.assign(구종 = 시즌전체평균.index)
        시즌전체평균 = 시즌전체평균.assign(구종 = 시즌전체평균.구종.apply(lambda x: 구종영문_한글로변환.get(x)))
        시즌전체평균 = 시즌전체평균.assign(구종 = 시즌전체평균.구종.astype('category'))
        시즌전체평균 = 시즌전체평균.assign(구종 = 시즌전체평균.구종.cat.set_categories(ptype_sortlist))
        시즌전체평균.insert(시즌전체평균.shape[1], '최고구속', g1.RelSpeed.max())
        시즌전체평균 = 시즌전체평균.assign(SpinAxis3dSpinEfficiency = 시즌전체평균.SpinAxis3dSpinEfficiency.mul(100))

        시즌전체평균 = 시즌전체평균.sort_values('구종')
        시즌전체평균 = 시즌전체평균.rename(columns = {
            'RelSpeed': '구속',
            'SpinRate': '회전수',
            'InducedVertBreak': '수직무브',
            'HorzBreak': '좌우무브',
            'RelHeight': '릴리즈높이',
            'Extension': '익스텐션',
            'PitchNo': '투구수',
            'hardhit': '강한타구',
            'barrel': '배럴타구',
            'strike': '스트라이크',
            'in_zone': '인존',
            'whiff': '헛스윙',
            'first_pitch': '초구',
            'fp_strike': '초구스트',
            'fp_swing': '초구스윙',
            'swing': '스윙',
            'GB': '땅볼',
            'FB': '뜬공',
            'LD': '라이너',
            'PU': '팝업',
            'bip': '인플레이',
            'hit': '피안타',
            'bip_ev': '타구속도',
            'VertRelAngle': 'VRA',
            'VertApprAngle': 'VAA',
            'SpinAxis3dSpinEfficiency': '회전효율',
            'SpinAxis': '회전축',
            'SpinAxis3dTransverseAngle': '회전축3D',
            'MovementBasedAxis': '회전방향(무브기준)',
            'SpinBasedAxis': '회전방향(실제)',
        })
        시즌전체평균.insert(시즌전체평균.shape[1], '스트%', 시즌전체평균.스트라이크.div(시즌전체평균.투구수).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '존%', 시즌전체평균.인존.div(시즌전체평균.투구수).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '스윙%', 시즌전체평균.스윙.div(시즌전체평균.투구수).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '헛스윙%', 시즌전체평균.헛스윙.div(시즌전체평균.스윙).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], 'CSW%', 시즌전체평균.csw.div(시즌전체평균.투구수).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '초구비율%', 시즌전체평균.초구.div(시즌전체평균.초구.sum()).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '초구스트%', 시즌전체평균.초구스트.div(시즌전체평균.초구).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '초구스윙%', 시즌전체평균.초구스윙.div(시즌전체평균.초구스트).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '강한타구%', 시즌전체평균.강한타구.div(시즌전체평균.bip_EVLA).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '배럴타구%', 시즌전체평균.배럴타구.div(시즌전체평균.bip_EVLA).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '땅볼%', 시즌전체평균.땅볼.div(시즌전체평균.bip_EVLA).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '라이너%', 시즌전체평균.라이너.div(시즌전체평균.bip_EVLA).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '뜬공%', 시즌전체평균.뜬공.div(시즌전체평균.bip_EVLA).mul(100))
        시즌전체평균.insert(시즌전체평균.shape[1], '팝업%', 시즌전체평균.팝업.div(시즌전체평균.bip_EVLA).mul(100))

        if _단위_미터 is False:
            시즌전체평균['구속'] = 시즌전체평균.구속.div(1.609344)
            시즌전체평균['최고구속'] = 시즌전체평균.최고구속.div(1.609344)
            시즌전체평균['수직무브'] = 시즌전체평균.수직무브.div(2.54)
            시즌전체평균['좌우무브'] = 시즌전체평균.좌우무브.div(2.54)
            시즌전체평균['릴리즈높이'] = 시즌전체평균.릴리즈높이.div(0.3048)
            시즌전체평균['익스텐션'] = 시즌전체평균.익스텐션.div(0.3048)
            시즌전체평균['타구속도'] = 시즌전체평균.타구속도.div(1.609344)

        없는컬럼 = [x for x in 테이블표시컬럼 if x not in 시즌전체평균.columns]
        if 없는컬럼 and len(없는컬럼) > 0:
            null_df = pd.DataFrame(index=시즌전체평균.index,
                                   columns=없는컬럼)
            시즌전체평균 = pd.concat([시즌전체평균, null_df], axis=1)
            for col in 없는컬럼:
                시즌전체평균[col] = 시즌전체평균[col].astype(테이블표시컬럼_타입[col])

        if 한글영문 == '한글':
            st.dataframe(시즌전체평균.set_index('구종')[테이블표시컬럼],
                         hide_index=False,
                         column_config=컬럼표시설정)
        else:
            시즌전체평균['구종'] = 시즌전체평균.구종.apply(lambda x: 구종한글_영문으로변환.get(x))
            st.dataframe(시즌전체평균.rename(columns=영문으로_컬럼바꾸기).set_index('Type')[테이블표시컬럼_영문],
                         hide_index=False,
                         column_config=컬럼표시설정_영문)

    else:
        st.markdown('**데이터 없음**')

    if 한글영문 == '한글':
        _1군구종텍스트 = ':red[1군 구종별 평균값 보기 (클릭)]'
    else:
        _1군구종텍스트 = ':red[KBO League Avg. by Pitch Type (Click)]'
    with st.expander(f'**{_1군구종텍스트}**'):
        if len(시즌전체데이터) > 0:
            투수손 = 시즌전체데이터.PitcherThrows.unique()[0]
            
            if 투수손 == 'Right':
                if 한글영문 == '한글':
                    st.markdown('**리그 평균 (우투)**')
                else:
                    st.markdown('**KBO Avg (RHH)**')
            elif 투수손 in ('Left', 'LSide'):
                투수손 = 'Left'
                if 한글영문 == '한글':
                    st.markdown('**리그 평균 (좌투)**')
                else:
                    st.markdown('**KBO Avg (LHH)**')
            elif 투수손 == 'Side':
                if 한글영문 == '한글':
                    st.markdown('**리그 평균 (사이드)**')
                else:
                    st.markdown('**KBO Avg (Side)**')
            연도별_리그_평균 = 연도별_리그_평균_가져오기(선택한연도)
            연도별_리그_평균 = 연도별_리그_평균.rename(columns=구종별컬럼명바꾸기)
            연도별_리그_평균 = 연도별_리그_평균[연도별_리그_평균.던지는손 == 투수손]
            연도별_리그_평균['비율'] = 연도별_리그_평균['비율'].mul(100)
            연도별_리그_평균['초구스윙%'] = 연도별_리그_평균['초구스윙%']
            연도별_리그_평균['구종'] = 연도별_리그_평균.구종.apply(lambda x: 구종영문_한글로변환.get(x))
            연도별_리그_평균 = 연도별_리그_평균.assign(구종 = 연도별_리그_평균.구종.astype('category'))
            연도별_리그_평균 = 연도별_리그_평균.assign(구종 = 연도별_리그_평균.구종.cat.set_categories(ptype_sortlist))
            연도별_리그_평균 = 연도별_리그_평균.sort_values('구종')

            if 한글영문 == '한글':
                표시컬럼 = [x for x in 테이블표시컬럼 if x in 연도별_리그_평균.columns]
                st.dataframe(연도별_리그_평균.set_index('구종')[표시컬럼],
                             hide_index=False,
                             column_config=컬럼표시설정)
            else:
                연도별_리그_평균['구종'] = 연도별_리그_평균.구종.apply(lambda x: 구종한글_영문으로변환.get(x))
                table = 연도별_리그_평균.rename(columns=영문으로_컬럼바꾸기).set_index('Type')
                표시컬럼 = [x for x in 테이블표시컬럼_영문 if x in table.columns]
                st.dataframe(table[표시컬럼],
                             hide_index=False,
                             column_config=컬럼표시설정_영문)

        else:
            st.markdown('**비교대상 없음**')


with st.expander('그림 한장으로 보기'):
    plt.style.use('fivethirtyeight')
    set_fonts()
    fig = plt.figure(figsize=(22, 13), dpi=144)#, layout="constrained")
    gs  = fig.add_gridspec(nrows=5, ncols=4,
                           height_ratios=[1, 5, 1, 3, 3])

    ax_topleft = fig.add_subplot(gs[0, 0]) # 투수 이름
    ax_top = fig.add_subplot(gs[0, 1:3])   # 박스스코어
    ax_logo = fig.add_subplot(gs[0, 3])    # 로고
    ax_ch1 = fig.add_subplot(gs[1, 0])     # 좌타상대 로케이션
    ax_ch2 = fig.add_subplot(gs[1, 1])     # 시즌전체 무브먼트
    ax_ch3 = fig.add_subplot(gs[1, 2])     # 그날경기 무브먼트
    ax_ch4 = fig.add_subplot(gs[1, 3])     # 우타상대로케이션

    ax_leg = fig.add_subplot(gs[2, 1:3])     # 범례/전체 폭
    ax_b1  = fig.add_subplot(gs[3, :])     # 그날경기 표
    ax_b2  = fig.add_subplot(gs[4, :])     # 시즌전체 표

    if 박스스코어 is not None and len(박스스코어) > 0:
        tbl_top = ax_top.table(cellText=박스스코어.values,
                               colLabels=박스스코어.columns,
                               cellLoc='center', loc='center')
        # 헤더 스타일(배경/볼드)
        for (r, c), cell in tbl_top.get_celld().items():
            cell.set_height(40/100)
            if r == 0:
                cell.set_facecolor("#F0F2F6")           # 헤더 배경색 (Streamlit 기본 톤 비슷)
                cell.set_text_props(weight='bold')      # 헤더 볼드
            cell.set_width(0.08)

        # 표가 그림 영역을 넘지 않게 bbox 조정
        tbl_top.auto_set_font_size(False)
        tbl_top.set_fontsize(18)

    # 여백 줄이기
    ax_top.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)


    # ---- 2) 예시: 가운데 4개 차트
    if len(그날데이터) > 0:
        if 좌타상대_로케이션 is not None:
            fA = 로케이션그리기(그날데이터, '좌', _분포표시, _구종별마커표시, ax=ax_ch1, dpi=200)
            좌타타이틀 = f"vs 좌타자 {len(그날데이터[그날데이터.BatterSide == 'Left'])}구" if 한글영문 == '한글' \
                         else f"vs LHH {len(그날데이터[그날데이터.BatterSide == 'Left'])} Pitches"
            ax_ch1.set_title(좌타타이틀, fontsize=20)
        if 우타상대_로케이션 is not None:
            fA = 로케이션그리기(그날데이터, '우', _분포표시, _구종별마커표시, ax=ax_ch4, dpi=200)
            우타타이틀 = f"vs 우타자 {len(그날데이터[그날데이터.BatterSide == 'Right'])}구" if 한글영문 == '한글' \
                         else f"vs RHH {len(그날데이터[그날데이터.BatterSide == 'Right'])} Pitches"
            ax_ch4.set_title(우타타이틀, fontsize=20)

        _ = movement_plot(그날데이터,
                          futures=퓨처스임,
                          draw_dots=_개별투구표시2,
                          sample_dots=False,
                          draw_usage=_구사율로표시,
                          draw_lg_avg=_1군평균표시,
                          lg_avg_df=리그평균,
                          freq_th=0,
                          eng=(한글영문 == '영어'),
                          ax=ax_ch3)
        if _ is not None:
            if isinstance(ax_ch3, mpl.axes.Axes):
                if 한글영문 == '한글':
                    선택경기_무브먼트플롯_타이틀 = '무브먼트: '
                else:
                    선택경기_무브먼트플롯_타이틀 = 'Movement: '
                if len(그날데이터) == len(시즌전체데이터):
                    if len(시즌전체데이터.year.unique()) > 1:
                        선택경기_무브먼트플롯_타이틀 += f'{시즌전체데이터.year.min()}-{시즌전체데이터.year.max()}'
                    else:
                        선택경기_무브먼트플롯_타이틀 += f'{시즌전체데이터.year.unique()[0]}'
                    if 한글영문 == '한글':
                        선택경기_무브먼트플롯_타이틀 += ' 시즌'
                    else:
                        선택경기_무브먼트플롯_타이틀 += ' Season'
                elif len(그날데이터.game_date.unique()) > 1:
                    선택경기_무브먼트플롯_타이틀 += f"{앞날짜텍스트} - {뒷날짜텍스트}"
                else:
                    선택경기_무브먼트플롯_타이틀 += f"{선택한경기날}"

                ax_ch3.set_title(선택경기_무브먼트플롯_타이틀)
    else:
        ax_ch1.axis('off')
        ax_ch3.axis('off')
        ax_ch4.axis('off')

    if len(시즌전체데이터) > 0:
        _ = movement_plot(시즌전체데이터,
                          futures=퓨처스임,
                          draw_dots=_개별투구표시1,
                          sample_dots=_샘플표시,
                          draw_usage=_구사율로표시,
                          draw_lg_avg=_1군평균표시,
                          lg_avg_df=리그평균,
                          freq_th=0,
                          eng=(한글영문 == '영어'),
                          ax=ax_ch2)
        if _ is not None:
            if isinstance(ax_ch2, mpl.axes.Axes):
                if 선택한연도 != '전체':
                    if 한글영문 == '한글':
                        시즌전체_무브먼트플롯_타이틀 = f'무브먼트: {선택한연도}'
                    else:
                        시즌전체_무브먼트플롯_타이틀 = f'Movement: {선택한연도}'
                else:
                    if 한글영문 == '한글':
                        시즌전체_무브먼트플롯_타이틀 = '무브먼트: '
                    else:
                        시즌전체_무브먼트플롯_타이틀 = f'Movement: '
                    if len(시즌전체데이터.year.unique()) > 1:
                        시즌전체_무브먼트플롯_타이틀 += f'{시즌전체데이터.year.min()}-{시즌전체데이터.year.max()}'
                    else:
                        시즌전체_무브먼트플롯_타이틀 += f'{시즌전체데이터.year.unique()[0]}'

                if 선택한레벨 != '전체':
                    if 한글영문 == '한글':
                        시즌전체_무브먼트플롯_타이틀 += f' {선택한레벨} 전체'
                    else:
                        if 선택한레벨 == '1군':
                            시즌전체_무브먼트플롯_타이틀 += f' KBO Majors'
                        elif 선택한레벨 == '퓨처스':
                            시즌전체_무브먼트플롯_타이틀 += f' KBO Minors'
                        elif 선택한레벨 == '시범':
                            시즌전체_무브먼트플롯_타이틀 += f' Exhibitions'
                        elif 선택한레벨 == '정규':
                            시즌전체_무브먼트플롯_타이틀 += f' Regular Season'
                        elif 선택한레벨 == '포스트시즌':
                            시즌전체_무브먼트플롯_타이틀 += f' Postseason'
                        elif 선택한레벨 == '정규+포시':
                            시즌전체_무브먼트플롯_타이틀 += f' Regular & Postseason'
                else:
                    if 한글영문 == '한글':
                        시즌전체_무브먼트플롯_타이틀 += f' 시즌'
                    else:
                        시즌전체_무브먼트플롯_타이틀 += f' Season'

                ax_ch2.set_title(시즌전체_무브먼트플롯_타이틀)

    ax_leg.axis('off')

    if len(그날데이터) > 0:
        if 한글영문 == '한글':
            ax_b1 = 차트용테이블변환(지정기간평균, ['구종']+테이블표시컬럼,
                                     row_px=16, header_px=22, ax=ax_b1, col_px=1.3, dpi=144, fontsize=12)
        else:
            ax_b1 = 차트용테이블변환(지정기간평균.rename(columns=영문으로_컬럼바꾸기), ['Type']+테이블표시컬럼_영문,
                                     row_px=16, header_px=22, ax=ax_b1, col_px=1.3, dpi=144, fontsize=12)

        y좌표위치 = 0.95 if len(지정기간평균) < 7 else 1.05
        if len(그날데이터.game_date.unique()) > 1:
            ax_b1.text(
                0.0, y좌표위치, # x=0(왼쪽), y=1.05(표 위)
                f"{앞날짜텍스트} - {뒷날짜텍스트}",
                ha='left', va='bottom',
                fontsize=16, fontweight='bold',
                transform=ax_b1.transAxes
            )
        elif 선택한경기날 == '전체':
            ax_b1.text(
                0.0, y좌표위치, # x=0(왼쪽), y=1.05(표 위)
                f"{앞날짜텍스트} - {뒷날짜텍스트}",
                ha='left', va='bottom',
                fontsize=16, fontweight='bold',
                transform=ax_b1.transAxes
            )
        else:
            ax_b1.text(
                0.0, y좌표위치, # x=0(왼쪽), y=1.05(표 위)
                f"{선택한경기날}",
                ha='left', va='bottom',
                fontsize=16, fontweight='bold',
                transform=ax_b1.transAxes
            )
    else:
        ax_b1.axis('off')

    if len(시즌전체데이터) > 0:
        if 한글영문 == '한글':
            ax_b2 = 차트용테이블변환(시즌전체평균, ['구종']+테이블표시컬럼,
                                     row_px=16, header_px=22, ax=ax_b2, col_px=1.3, dpi=144, fontsize=12)
        else:
            ax_b2 = 차트용테이블변환(시즌전체평균.rename(columns=영문으로_컬럼바꾸기), ['Type']+테이블표시컬럼_영문,
                                     row_px=16, header_px=22, ax=ax_b2, col_px=1.3, dpi=144, fontsize=12)
        y좌표위치 = 0.95 if len(시즌전체평균) < 7 else 1.05
        표타이틀 = "시즌 평균" if 한글영문 == '한글' else 'Season Summary'
        ax_b2.text(
            0.0, y좌표위치, # x=0(왼쪽), y=1.05(표 위)
            표타이틀, 
            ha='left', va='bottom',
            fontsize=16, fontweight='bold',
            transform=ax_b2.transAxes
        )

    # 선수 이름 좌상단
    ax_topleft.text(0, 0.8, 타이틀2,
                    ha='left', va='bottom',
                    fontsize=36, fontweight='bold',
                    transform=ax_topleft.transAxes)
    ax_topleft.axis('off')
    ax_topleft.set_xticks([])
    ax_topleft.set_yticks([])

    # 로고 이미지 우상단
    try:
        logo = mpimg.imread('../images/eagles_no_bg.png')  # PNG/JPG 불러오기
    except:
        logo = mpimg.imread('images/eagles_no_bg.png')  # PNG/JPG 불러오기
    imagebox = OffsetImage(logo, zoom=0.15)  # zoom으로 크기 조절
    ab = AnnotationBbox(imagebox, (0.75, 0.95), frameon=False,
                        xycoords=ax_logo.transAxes)
    ax_logo.add_artist(ab)
    ax_logo.axis('off')

    # 마지막으로 모든 플롯 하얀 배경
    fig.patch.set_facecolor('white') # figure 배경
    for ax in fig.axes: ax.set_facecolor('white') # axes 배경
    st.pyplot(fig)
