import streamlit as st
import pandas as pd

from utils.codes import *
from utils.conn import *

level_dict = {
    '1군': 'KBO',
    '퓨처스': 'KBO Minors',
}
engine = get_conn()

타자컬럼명바꾸기 = {
    'year': '연도',
    'BA': '타율',
    'OBP': '출루율',
    'SLG': '장타율',
    'OPS': 'OPS',
    'xBA': '기대타율',
    'xOBP': '기대출루율',
    'xSLG': '기대장타율',
    'xOPS': '기대OPS',
    'BABIP': 'BABIP',
    'wOBA': 'wOBA',
    'xwOBA': '기대wOBA',
    'bb_rate': 'BB%',
    'k_rate': 'K%',
    'hr_rate': 'HR%',
    'hardhit_rate': '강한타구%',
    'barrel_rate': '배럴%',
    'flareburner_rate': '단타성타구%',
    'zswing_rate': '존스윙%',
    'zcon_rate': '존컨택%',
    'chase_rate': '체이스%',
    'swing_rate': '스윙%',
    'ocon_rate': '아웃컨%',
    'con_rate': '컨택%',
    'gb_rate': '땅볼%',
    'ld_rate': '라인%',
    'fb_rate': '뜬공%',
    'pfb_rate': '약한뜬공%',
    'pu_rate': '팝업%',
    'pull_rate': '당긴%',
    'center_rate': '가운데%',
    'oppo_rate': '밀어친%',
    'max_ev': '최대 타구속도',
    'mean_ev': '평균 타구속도',
    'mean_la': '평균 발사각도',
    'pullair_rate': 'PullAir%',
}

타자필요컬럼 = [
    '타율', '출루율', '장타율', 'OPS', 'BABIP', 'wOBA',
    'BB%', 'K%', 'HR%',
    '강한타구%', '배럴%', '단타성타구%', 'PullAir%',
    '최대 타구속도', '평균 타구속도', '평균 발사각도',
    '존스윙%', '체이스%', '스윙%', '존컨택%', '아웃컨%', '컨택%',
    '땅볼%', '라인%', '뜬공%', '약한뜬공%', '팝업%',
    '당긴%', '가운데%', '밀어친%',
]

투수컬럼명바꾸기 = {
    'year': '연도',
    'whip': 'WHIP',
    'k_rate': 'K%',
    'bb_rate': 'BB%',
    'k_minus_bb_rate': 'K-BB%',
    'hr_rate': 'HR%',
    'k_per_9': 'K/9',
    'bb_per_9': 'BB/9',
    'hr_per_9': 'HR/9',
    'csw_rate': 'CSW%',
    'whiff_rate': '헛스윙%',
    'zone_rate': '존%',
    'strike_rate': '스트%',
    'BA': '피안타율',
    'OBP': '피출루율',
    'SLG': '피장타율',
    'OPS': '피OPS',
    'xBA': '기대피안타율',
    'xOBP': '기대피출루율',
    'xSLG': '기대피장타율',
    'xOPS': '기대피OPS',
    'BABIP': 'BABIP',
    'hardhit_rate': '강한타구%',
    'barrel_rate': '배럴%',
    'flareburner_rate': '단타성타구%',
    'zcon_rate': '존컨택%',
    'chase_rate': '체이스%',
    'gb_rate': '땅볼%',
    'ld_rate': '라인%',
    'fb_rate': '뜬공%',
    'pu_rate': '팝업%',
    'gb_per_fb': '땅/뜬',
    'pitches': '투구수',
}

투수필요컬럼 = [
    'WHIP', 'K%', 'BB%', 'K-BB%', 'HR%', 'K/9', 'BB/9', 'HR/9',
    'CSW%', '헛스윙%', '존%', '스트%', 
    '피안타율', '피출루율', '피장타율', '피OPS', 'BABIP',
    '강한타구%', '배럴%', '단타성타구%',
    '존컨택%', '체이스%',
    '땅볼%', '라인%', '뜬공%', '팝업%', '땅/뜬', '투구수',
]

구종별컬럼명바꾸기 = {
    'year': '연도',
    'pitch_type': '구종',
    'pthrows': '던지는손',
    'speed_mean': '구속',
    'speed_median': '구속(중간값)',
    'spin_mean': '회전수',
    'spin_median': '회전수(중간값)',
    'hb_mean': '수평무브',
    'hb_median': '수평무브(중간값)',
    'hb_std': '수평무브(표준편차)',
    'ivb_mean': '수직무브',
    'ivb_median': '수직무브(중간값)',
    'ivb_std': '수직무브(표준편차)',
    'ext_mean': '익스텐션',
    'ext_median': '익스텐션(중간값)',
    'ext_std': '익스텐션(표준편차)',
    'relh_mean': '릴리즈높이',
    'relh_median': '릴리즈높이(중간값)',
    'relh_std': '릴리즈높이(표준편차)',
    'ratio': '구사율',
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
    'ld_pct': '라인%',
    'pu_pct': '팝업%',
    'hardhit_pct': '강한타구%',
    'barrel_pct': '배럴%',
    'vra_mean': 'VRA',
    'vaa_mean': 'VAA',
    'vra_std': 'VRA(표준편차)',
    'vaa_std': 'VAA(표준편차)',
    'ba': '피안타율',
    'obp': '피출루율',
    'slg': '피장타율',
    'ops': '피OPS',
    'xba': '기대피안타율',
    'xobp': '기대피출루율',
    'xslg': '기대피장타율',
    'xops': '기대피OPS',
    'woba': 'wOBA',
    'xwoba': '기대wOBA',
}

구종별필요컬럼 = [
    #'구종', '던지는손',
    '구속', '회전수',
    '수직무브', '수평무브', '익스텐션', '릴리즈높이',
    'VRA', 'VAA',
    '스트%', '존%', '헛스윙%', 'CSW%', '초구스트%', '초구스윙%',
    '피안타율', '피출루율', '피장타율', '피OPS', 'wOBA',
    '기대피안타율', '기대피출루율', '기대피장타율', '기대피OPS', '기대wOBA',
    '땅볼%', '뜬공%', '라인%', '팝업%', '강한타구%', '배럴%',
]

def get_hitter_yearly_summary(level='KBO',
                              year: int=None):
    sql = f"""
        SELECT *
        FROM `service_mart`.season_agg_hitter_lg
        WHERE level='{level}'
    """
    if year is not None:
        sql += f' AND year={year}'
    df = get_sql_df(sql, engine, verbose=False)
    return df


def get_pitcher_yearly_summary(level='KBO',
                               year: int=None):
    sql = f"""
        SELECT *
        FROM `service_mart`.season_agg_pitcher_lg
        WHERE level='{level}'
    """
    if year is not None:
        sql += f' AND year={year}'
    df = get_sql_df(sql, engine, verbose=False)
    return df


def get_pitcher_pitch_yearly_summary(year: int=None):
    sql = f"""
        SELECT *
        FROM `service_mart`.season_pitchtype_agg_lg
    """
    if year is not None:
        sql += f' WHERE year={year}'
    else:
        sql += ' WHERE year >= 2021'
    df = get_sql_df(sql, engine, verbose=False)
    return df


st.set_page_config(
    page_title = "리그 평균 기록",
    page_icon = "📊",
    layout='wide',
)
st.markdown("##### 리그 평균 기록")

셀렉트컬럼 = st.columns(6)
with 셀렉트컬럼[0]:
    level = st.selectbox("레벨", ["1군", "퓨처스"])

tab1, tab2 = st.tabs(["타자", "투수"])

with tab1:
    st.subheader("타자 리그 평균값")

    # 연도/월 선택 (월별 테이블이 없으면 연도별만 제공)
    df = get_hitter_yearly_summary(level_dict[level])
    df = df.rename(columns=타자컬럼명변환)
    df = df.set_index(['연도'])

    if df.empty:
        st.info("해당 조건의 데이터가 없습니다.")
    else:
        # 필요하면 컬럼명 한글 변환 등 가공
        st.dataframe(df[타자필요컬럼],
                     width='content',
                     column_config={
                         **타자컬럼포맷설정
                     },
                     hide_index=False)
        # st.write(df.columns)

with tab2:
    st.subheader("투수 리그 평균값")

    # 연도/월 선택 (월별 테이블이 없으면 연도별만 제공)
    df = get_pitcher_yearly_summary(level_dict[level])
    df = df.rename(columns=투수컬럼명바꾸기)
    df = df.set_index(['연도'])

    df2 = get_pitcher_pitch_yearly_summary()
    df2 = df2.rename(columns=구종별컬럼명바꾸기)
    df2 = df2.assign(구종 = df2.구종.apply(lambda x: 구종영문_한글로변환.get(x)),
                     던지는손 = df2.던지는손.apply(lambda x: 손변환.get(x)))

    df2 = df2.assign(구종 = pd.Categorical(df2.구종, categories=구종순서, ordered=True),
                     던지는손 = pd.Categorical(df2.던지는손, categories=손순서, ordered=True),)

    df2 = df2.sort_values(by=['구종', '던지는손'])

    df2 = df2.set_index(['연도', '구종', '던지는손'])

    if df.empty:
        st.info("해당 조건의 데이터가 없습니다.")
    else:
        # 필요하면 컬럼명 한글 변환 등 가공
        st.dataframe(df[투수필요컬럼],
                     width='content',
                     column_config={
                         **투수컬럼포맷설정
                     },
                     hide_index=False)
    if df2.empty:
        st.info("해당 조건의 데이터가 없습니다.")
    else:
        st.markdown('### 1군 구종별 평균값')
        투수_레이아웃 = st.columns(7)
        with 투수_레이아웃[0]:
            던지는손 = st.selectbox("던지는손", ["전체", "우", "좌", "우사", "좌사"])
        if 던지는손 != '전체':
            df3 = df2[df2.index.get_level_values('던지는손') == 던지는손]
        else:
            df3 = df2
        
        # 필요하면 컬럼명 한글 변환 등 가공
        st.dataframe(df3[구종별필요컬럼],
                     width='content',
                     column_config={
                        **투수컬럼포맷설정
                     },
                     hide_index=False)
