import streamlit as st
import pandas as pd

from utils.codes import *
from utils.conn import *

engine = get_conn()
최대연도 = get_max_year(engine)

@st.cache_data(ttl=86400)
def load_data():
    쿼리1 = f"""
WITH bsr AS
(
SELECT
  `year`,
  IF(team='고양', '키움', team) AS 시즌_소속팀,
  `level_eng`,
  tmid
FROM
  `stats_logs`.stats_hitter kbsr
WHERE
  kbsr.`year` BETWEEN {최대연도-4} AND {최대연도}
),
pi2 AS
(
SELECT
  pi2.name AS 이름,
  pi2.team AS 현재_원소속팀,
  pi2.team_code,
  pi2.birth,
  IF(pi2.local=1, '국내', '외국인') AS 국적,
  IF(substr(pi2.bat_throw, 1, 1)='우', '우투',
    IF(substr(pi2.bat_throw, 1, 1)='언', '우투', '좌투')) AS 투,
  IF(substr(pi2.bat_throw, 3, 1)='우', '우타',
    IF(substr(pi2.bat_throw, 3, 1)='좌', '좌타', '양타')) AS 타,
  pi2.tm_id
FROM
  `master_meta`.player_info pi2
),
teams AS
(
SELECT
  tn.team AS 현재_등록소속팀,
  tn.`year`,
  tn.team_code
FROM
  `master_meta`.team_info tn
where
  tn.team <> '고양'
),
hsys AS (
SELECT
  *
FROM
  `service_mart`.season_agg_hitter hsys
WHERE
  hsys.`year` BETWEEN {최대연도-4} AND {최대연도}
)
SELECT
  pi2.이름,
  pi2.현재_원소속팀 AS 원소속팀,
  teams.현재_등록소속팀 AS 현소속팀,
  bsr.시즌_소속팀 AS 시즌소속팀,
  hsys.`year` - year(pi2.birth) as 나이,
  pi2.국적,
  pi2.투,
  pi2.타,
  hsys.*
FROM
  hsys
JOIN pi2
  ON pi2.tm_id = hsys.BatterId
LEFT JOIN teams
  ON pi2.team_code = teams.team_code
     AND hsys.`year` = teams.`year`
LEFT JOIN bsr
  ON bsr.tmid = hsys.BatterId
     AND bsr.level_eng = hsys.`level`
     AND bsr.`year` = hsys.`year`;
"""

    쿼리2 = f"""
WITH psr AS
(
SELECT
  `year`,
  IF(team='고양', '키움', team) AS 시즌_소속팀,
  `level_eng`,
  tmid
FROM
  `stats_logs`.stats_pitcher kpsr
WHERE
  kpsr.`year` BETWEEN {최대연도-4} AND {최대연도}
),
pi2 AS
(
SELECT
  pi2.name AS 이름,
  pi2.team AS 현재_원소속팀,
  pi2.team_code,
  pi2.birth,
  IF(pi2.local=1, '국내', '외국인') AS 국적,
  IF(substr(pi2.bat_throw, 1, 1)='우', '우투',
    IF(substr(pi2.bat_throw, 1, 1)='언', '우투', '좌투')) AS 투,
  IF(substr(pi2.bat_throw, 3, 1)='우', '우타',
    IF(substr(pi2.bat_throw, 3, 1)='좌', '좌타', '양타')) AS 타,
  pi2.tm_id
FROM
  `master_meta`.player_info pi2
),
teams AS
(
SELECT
  tn.team AS 현재_등록소속팀,
  tn.`year`,
  tn.team_code
FROM
  `master_meta`.team_info tn
where
  tn.team <> '고양'
),
psys AS (
SELECT
  *
FROM
  `service_mart`.season_agg_pitcher psys
WHERE
  psys.`year` BETWEEN {최대연도-4} AND {최대연도}
)
SELECT
  pi2.이름,
  pi2.현재_원소속팀 AS 원소속팀,
  teams.현재_등록소속팀 AS 현소속팀,
  psr.시즌_소속팀 AS 시즌소속팀,
  psys.`year` - year(pi2.birth) as 나이,
  pi2.국적,
  pi2.투,
  pi2.타,
  psys.*
FROM
  psys
JOIN pi2
  ON pi2.tm_id = psys.PitcherId
LEFT JOIN teams
  ON pi2.team_code = teams.team_code
     AND psys.`year` = teams.`year`
LEFT JOIN psr
  ON psr.tmid = psys.PitcherId
     AND psr.level_eng = psys.`level`
     AND psr.`year` = psys.`year`;
"""
    with st.spinner('load data...'):
        타자성적 = get_sql_df(쿼리1, engine).rename(columns=타자컬럼명변환)
        투수성적 = get_sql_df(쿼리2, engine).rename(columns=투수컬럼명변환)
        타자성적 = 타자성적.assign(현소속팀 = np.where(타자성적.현소속팀.isnull(), '없음', 타자성적.현소속팀),
                                   원소속팀 = np.where(타자성적.원소속팀.isnull(), '없음', 타자성적.원소속팀),
                                   시즌소속팀 = np.where(타자성적.시즌소속팀.isnull(), '없음', 타자성적.시즌소속팀),)
        투수성적 = 투수성적.assign(현소속팀 = np.where(투수성적.현소속팀.isnull(), '없음', 투수성적.현소속팀),
                                   원소속팀 = np.where(투수성적.원소속팀.isnull(), '없음', 투수성적.원소속팀),
                                   시즌소속팀 = np.where(투수성적.시즌소속팀.isnull(), '없음', 투수성적.시즌소속팀),)

        타자_1군 = 타자성적[타자성적.레벨 == 'KBO']
        타자_퓨처스 = 타자성적[타자성적.레벨 == 'KBO Minors']
        투수_1군 = 투수성적[투수성적.레벨 == 'KBO']
        투수_퓨처스 = 투수성적[투수성적.레벨 == 'KBO Minors']
        
    return [타자_1군, 타자_퓨처스, 투수_1군, 투수_퓨처스] 

####################
#### Main
####################
st.set_page_config(
    page_title = "KBO 리더보드 - 메인",
    page_icon = "📊",
    layout='wide',
)
st.title('리더보드')
st.subheader("KBO 스탯 리더보드")

st.markdown('##### KBO 1군/퓨처스 기록을 표시합니다.')

#### 트랙맨 파일 읽기
#### 연도: DataFrame 형식
타자_1군, 타자_퓨처스, 투수_1군, 투수_퓨처스 = load_data()

시즌옵션 = list(range(2021, 최대연도+1))[::-1]

셀렉터영역 = st.columns(8)
with 셀렉터영역[-1]:
    if st.button("Clear Cache"):
        load_data.clear()

with 셀렉터영역[0]:
    시즌선택 = st.selectbox(label = "연도 선택",
                            options = 시즌옵션,
                            index=0,
                            placeholder = '...연도 선택')
with 셀렉터영역[1]:
    레벨선택 = st.radio("레벨 선택", ["1군", "퓨처스"], index=0, horizontal=True)

    현소속or원소속 = st.radio('현소속팀/원소속팀', ['현재', '원소속', '시즌당시소속'], index=0, horizontal=True)

with 셀렉터영역[2]:
    팀옵션 = ["한화", "KIA", "KT", "LG", "NC", "SSG",
              "두산", "롯데", "삼성", "키움", "상무", "없음"]
    # 세션 상태 초기화
    if 'selected_pills' not in st.session_state:
        st.session_state.selected_pills = 팀옵션
    # '전체 선택' 버튼을 눌렀을 때 실행될 콜백 함수
    def select_all_pills():
        st.session_state.selected_pills = 팀옵션
    def unselect_all_pills():
        st.session_state.selected_pills = []
    st.button("전체 선택", on_click=select_all_pills)
    st.button("전체 해제", on_click=unselect_all_pills)

with 셀렉터영역[3]:
    팀선택 = st.pills("팀선택",
                      팀옵션, 
                      default=st.session_state.selected_pills,
                      selection_mode="multi")
with 셀렉터영역[4]:
    국적 = st.radio("국적",
                    ['전체', '국내', '외국인'], 
                    index=0, horizontal=True)


타자탭, 투수탭 = st.tabs(['타자 스탯', '투수 스탯'])


with 타자탭:
    필터영역1 = st.columns(6)
    with 필터영역1[0]:
        타자타석최소 = st.slider('타석 ≥', 0, 600, 0, step=10)
    with 필터영역1[1]:
        타자나이범위 = st.slider('타자 나이 범위', 17, 45, (17, 45), step=1)
    with 필터영역1[2]:
        if st.toggle('OPS ≥'):
            타자ops최소 = st.slider('', 0.000, 1.500, 0.000, step=0.100,
                                    format='%.3f', label_visibility='collapsed')
        else:
            타자ops최소 = 0
    with 필터영역1[3]:
        타자_투타 = st.radio("치는손",
                             ['전체', '우타', '좌타', '양타'], 
                             index=0, horizontal=True)

    필터영역2 = st.columns(6)
    with 필터영역2[0]:
        if st.toggle('체이스% ≤'):
            타자체이스최대 = st.slider('', 0.0, 100.0, 100.0, step=5.0,
                                       format='%.1f', label_visibility='collapsed')
        else:
            타자체이스최대 = None
    with 필터영역2[1]:
        if st.toggle('존컨택% ≥'):
            타자존컨택최소 = st.slider(' ', 0.0, 100.0, 0.0, step=5.0,
                                       format='%.1f', label_visibility='collapsed')
        else:
            타자존컨택최소 = None
    with 필터영역2[2]:
        if st.toggle('존스윙% ≥'):
            타자존스윙최소 = st.slider('', 0.0, 100.0, 0.0, step=5.0,
                                       format='%.1f', label_visibility='collapsed')
        else:
            타자존스윙최소 = None
    with 필터영역2[3]:
        if st.toggle('배럴% ≥'):
            타자배럴최소 = st.slider('', 0.0, 100.0, 0.0, step=2.0,
                                     format='%.1f', label_visibility='collapsed')
        else:
            타자배럴최소 = None
    with 필터영역2[4]:
        if st.toggle('강한타구% ≥'):
            타자하드힛최소 = st.slider(' ', 0.0, 100.0, 0.0, step=2.0,
                                       format='%.1f', label_visibility='collapsed')
        else:
            타자하드힛최소 = None

    if 레벨선택 == '1군':
        df = 타자_1군
    else:
        df = 타자_퓨처스

    if 시즌선택 != '전체':
        df = df[(df.연도 == 시즌선택) &
                (df.나이.between(타자나이범위[0], 타자나이범위[1]))]

    if len(df) > 0:
        df = df[(df.타석 >= 타자타석최소)]

        if (타자ops최소 is not None):
            df = df[(df.OPS >= 타자ops최소)]
        if (타자체이스최대 is not None):
            df = df[df.get('체이스%') <= 타자체이스최대]
        if (타자존컨택최소 is not None):
            df = df[df.get('존컨택%') >= 타자존컨택최소]
        if (타자존스윙최소 is not None):
            df = df[df.get('존스윙%') >= 타자존스윙최소]
        if (타자배럴최소 is not None):
            df = df[df.get('배럴%') >= 타자배럴최소]
        if (타자하드힛최소 is not None):
            df = df[df.get('강한타구%') >= 타자하드힛최소]
        if 타자_투타 != '전체':
            df = df[df.타 == 타자_투타]
        if 국적 != '전체':
            df = df[df.국적 == 국적]

        try:
            if 현소속or원소속 == '현재':
                df = df[df.현소속팀.isin(팀선택)]
                df = df.rename(columns={'현소속팀':'팀'}).set_index(['이름', '팀'])
            elif 현소속or원소속 == '원소속':
                df = df[df.원소속팀.isin(팀선택)]
                df = df.rename(columns={'원소속팀':'팀'}).set_index(['이름', '팀'])
            else:
                df = df[df.시즌소속팀.isin(팀선택)]
                df = df.rename(columns={'시즌소속팀':'팀'}).set_index(['이름', '팀'])
            st.dataframe(df[타자리더보드_표시컬럼].sort_values('타석', ascending=False),
                         column_config = 타자컬럼포맷설정)

        except KeyError as e:
            st.markdown('데이터 없음')
            st.write(e)
    else:
        st.markdown('데이터 없음')


with 투수탭:
    필터영역1 = st.columns(6)
    with 필터영역1[0]:
        투수이닝최소 = st.slider('이닝 ≥', 0, 200, 0, step=5, format='%d')
    with 필터영역1[1]:
        투수나이범위 = st.slider('나이 범위', 17, 45, (17, 45), step=1)
    with 필터영역1[2]:
        if st.toggle('WHIP ≥'):
            투수WHIP최대 = st.slider('WHIP ≤', 0.00, 2.00, 2.00, step=0.10, format='%.2f')
        else:
            투수WHIP최대 = None
    with 필터영역1[3]:
        투수_투타 = st.radio("던지는손",
                             ['전체', '우투', '좌투'], 
                             index=0, horizontal=True)

    필터영역2 = st.columns(6)
    with 필터영역2[0]:
        if st.toggle('K/9 ≥'):
            투수K9최소 = st.slider('', 0.0, 20.0, 0.0, step=1.0,
                                   format='%.1f', label_visibility='collapsed')
        else:
            투수K9최소 = None
    with 필터영역2[1]:
        if st.toggle('BB/9 ≤'):
            투수BB9최소 = st.slider('', 0.0, 10.0, 10.0, step=1.0,
                                    format='%.1f', label_visibility='collapsed')
        else:
            투수BB9최소 = None
    with 필터영역2[2]:
        if st.toggle('HR/9 ≤'):
            투수HR9최소 = st.slider('', 0.0, 5.0, 5.0, step=0.5,
                                         format='%.1f', label_visibility='collapsed')
        else:
            투수HR9최소 = None
    with 필터영역2[3]:
        if st.toggle('K% ≥'):
            투수K퍼최소 = st.slider('', 0.0, 40.0, 0.0, step=5.0,
                                    format='%.1f', label_visibility='collapsed')
        else:
            투수K퍼최소 = None
    with 필터영역2[4]:
        if st.toggle('BB% ≤'):
            투수BB퍼최소 = st.slider('', 0.0, 30.0, 30.0, step=5.0,
                                     format='%.1f', label_visibility='collapsed')
        else:
            투수BB퍼최소 = None
    with 필터영역2[5]:
        if st.toggle('HR% ≤'):
            투수HR퍼최소 = st.slider('', 0.0, 10.0, 10.0, step=5.0,
                                     format='%.1f', label_visibility='collapsed')
        else:
            투수HR퍼최소 = None

    if 레벨선택 == '1군':
        df = 투수_1군
    else:
        df = 투수_퓨처스

    if 시즌선택 != '전체':
        df = df[(df.연도 == 시즌선택) &
                (df.나이.between(투수나이범위[0], 투수나이범위[1]))]

    if len(df) > 0:
        df = df[(df.이닝 >= 투수이닝최소)]

        if (투수WHIP최대 is not None):
            df = df[(df.WHIP <= 투수WHIP최대)]
        if (투수K9최소 is not None):
            df = df[df.get('K/9') >= 투수K9최소]
        if (투수BB9최소 is not None):
            df = df[df.get('BB/9') <= 투수BB9최소]
        if (투수HR9최소 is not None):
            df = df[df.get('HR/9') <= 투수HR9최소]
        if (투수K퍼최소 is not None):
            df = df[df.get('K%') >= 투수K퍼최소]
        if (투수BB퍼최소 is not None):
            df = df[df.get('BB%') <= 투수BB퍼최소]
        if (투수HR퍼최소 is not None):
            df = df[df.get('HR%') <= 투수HR퍼최소]
        if 투수_투타 != '전체':
            df = df[df.투 == 투수_투타]
        if 국적 != '전체':
            df = df[df.국적 == 국적]

        try:
            if 현소속or원소속 == '현재':
                df = df[df.현소속팀.isin(팀선택)]
                df = df.rename(columns={'현소속팀':'팀'}).set_index(['이름', '팀'])
            elif 현소속or원소속 == '원소속':
                df = df[df.원소속팀.isin(팀선택)]
                df = df.rename(columns={'원소속팀':'팀'}).set_index(['이름', '팀'])
            else:
                df = df[df.시즌소속팀.isin(팀선택)]
                df = df.rename(columns={'시즌소속팀':'팀'}).set_index(['이름', '팀'])
            st.dataframe(df[투수리더보드_표시컬럼].sort_values('이닝', ascending=False),
                         column_config = 투수컬럼포맷설정)

        except KeyError:
            st.markdown('데이터 없음')
            st.write(e)
    else:
        st.markdown('데이터 없음')
