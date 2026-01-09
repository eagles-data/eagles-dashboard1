import streamlit as st
import pandas as pd
import gcsfs

from utils.codes import *
from utils.conn import *

engine = get_conn()
storage_options = get_storage_options()
bucket_name = "baseball_app_data_cache"
summary_uri = f"gs://{bucket_name}/stuffplus/summary"
pattern = f"{summary_uri}/*.csv.gz"

@st.cache_data(ttl=86400)
def load_pids():
    쿼리 = """
WITH res AS
(SELECT
DISTINCT pitcherid, pitcher
FROM `raw_tracking`.tm
WHERE tm.`level` = 'KBO'
),
res2 AS
(SELECT
pinfo.team_code, pinfo.name, res.pitcherid, res.pitcher
FROM `master_meta`.player_info pinfo, res
WHERE res.pitcherid = pinfo.tm_id
)
SELECT
tn.team,
res2.name,
res2.pitcherid
FROM `master_meta`.team_info tn, res2
WHERE tn.`year` = 2025
AND tn.team <> '고양'
AND res2.team_code = tn.team_code
    """
    쿼리 = """
SELECT
    tn.team 팀, 
    pinfo.name,
    pinfo.tm_id,
    CONCAT(pinfo.name, '(', pinfo.tm_id, ')') AS ID
FROM 
    `master_meta`.player_info pinfo
LEFT JOIN
    `master_meta`.team_info tn ON pinfo.team_code = tn.team_code
WHERE
    (tn.`year` = 2025 OR tn.team_code IS NULL)
AND
    (tn.team <> '고양' OR tn.team IS NULL);
"""
    df = get_sql_df(쿼리, engine)

    return df


@st.cache_data(ttl=43200)
def load_stuff_by_game():
    fs = gcsfs.GCSFileSystem(**storage_options)
    
    # glob으로 파일 목록 가져오기 (gs:// 접두사 유지를 위해 리스트 컴프리헨션 활용)
    서머리_게임파일목록 = sorted([f"gs://{p}" for p in fs.glob(f"{summary_uri}/*summary_game.csv.gz")])
    서머리_퓨처스_게임파일목록 = sorted([f"gs://{p}" for p in fs.glob(f"{summary_uri}/*summary_game_futures.csv.gz")])

    # 가장 최신 파일 선택
    서머리_파일 = 서머리_게임파일목록[-1]
    서머리_퓨처스_파일 = 서머리_퓨처스_게임파일목록[-1]

    # Pandas가 인증, 경로, 압축을 모두 처리합니다.
    summary = pd.read_csv(서머리_파일, storage_options=storage_options)
    summary_futures = pd.read_csv(서머리_퓨처스_파일, storage_options=storage_options)

    update_1 = fs.info(서머리_파일)['updated']
    update_2 = fs.info(서머리_퓨처스_파일)['updated']

    # 2. pd.to_datetime으로 감싸서 무조건 시간 객체로 변환
    # max() 연산을 수행한 결과가 문자열일지라도 여기서 객체로 바뀝니다.
    upload_time = pd.to_datetime(max(update_1, update_2))
    upload_time_kst = upload_time + pd.Timedelta(hours=9)
    formatted_time = upload_time_kst.strftime("%Y/%m/%d %H:%M")

    return [summary, summary_futures, formatted_time]


####################
#### Main
####################
st.set_page_config(
    page_title = "스터프 점수 대시보드",
    page_icon = "⚾️🔥",
    layout='wide',
)
st.markdown("##### 스터프 점수 (경기별)")

#### Summary 파일 읽기
서머리게임테이블, 서머리게임테이블_퓨처스, lastUpdate = load_stuff_by_game()
#st.markdown(f'##### ♻️업데이트 시간: {lastUpdate}')

서머리게임테이블 = 서머리게임테이블.rename(columns = {
                                               'year': '연도',
                                               'game_date': '날짜',
                                               'TaggedPitchType': '구종',
                                               'n': '투구수',
                                               'Stuff_avg': '스터프+',
                                               'Stuff_poly': '스터프+(모델1)',
                                               'Stuff_GAM': '스터프+(모델2)',
                                               'Stuff_xgboost': '스터프+(모델3)',
                                               'RelSpeed': '구속',
                                               'SpinRate': '회전수',
                                               'InducedVertBreak': '수직무브',
                                               'HorzBreak': '좌우무브',
                                               'RelHeight': '릴리즈높이',
                                               'Extension': '익스텐션',
                                               'Extension_mod': '익스텐션(보정)',
                                           })
서머리게임테이블_퓨처스 = 서머리게임테이블_퓨처스.rename(columns = {
                                                             'year': '연도',
                                                             'game_date': '날짜',
                                                             'TaggedPitchType': '구종',
                                                             'n': '투구수',
                                                             'Stuff_avg': '스터프+',
                                                             'Stuff_poly': '스터프+(모델1)',
                                                             'Stuff_GAM': '스터프+(모델2)',
                                                             'Stuff_xgboost': '스터프+(모델3)',
                                                             'RelSpeed': '구속',
                                                             'SpinRate': '회전수',
                                                             'InducedVertBreak': '수직무브',
                                                             'HorzBreak': '좌우무브',
                                                             'RelHeight': '릴리즈높이',
                                                             'Extension': '익스텐션',
                                                             'Extension_mod': '익스텐션(보정)',
                                                         })

@st.cache_data(ttl=86400)
def load_season_teams():
    query = f"""
    SELECT 
        `year`, 
        `level_eng`, 
        tmid, 
        IF(team='고양', '키움', team) AS 시즌소속팀
    FROM `stats_logs`.stats_pitcher
    WHERE `year` BETWEEN 2021 AND 2025
    """
    return get_sql_df(query, engine)

# pitcher id 읽기
pids = load_pids()
season_teams = load_season_teams()

셀렉터영역 = st.columns(8)
with 셀렉터영역[0]:
    연도목록 = 서머리게임테이블.연도.unique().tolist()
    선택한연도 = st.selectbox("연도",
                              ["전체"] + 연도목록,
                              index=len(연도목록))
with 셀렉터영역[1]:
    현시즌구분 = st.radio("팀 분류", ["현재", "시즌"], index=1, horizontal=True)
    선택한팀 = st.selectbox("팀",
                            ["전체", "한화", "KIA", "KT", "LG", "NC", "SSG",
                             "두산", "롯데", "삼성", "키움", "상무"],
                            index=0)

with 셀렉터영역[2]:
    선택한레벨 = st.selectbox("레벨",
                              ["1군", "퓨처스"],
                              index=0)

with 셀렉터영역[-1]:
    if st.button("Clear Cache"):
        load_pids.clear()
        load_stuff_by_game.clear()
        load_season_teams.clear()

if 선택한레벨 == '1군':
    선택한_서머리테이블 = 서머리게임테이블
else:
    선택한_서머리테이블 = 서머리게임테이블_퓨처스

테이블내_투수ID목록 = 선택한_서머리테이블.PitcherId.unique()
pitchers = pids[pids.tm_id.isin(테이블내_투수ID목록)]
pinfo = pitchers.set_index('tm_id').to_dict(orient='index')

# 현소속팀 vs 시즌소속팀 매핑
level_map = {"1군": "KBO", "퓨처스": "KBO Minors"}
current_level_eng = level_map.get(선택한레벨)

if 현시즌구분 == "현재":
    선택한_서머리테이블 = 선택한_서머리테이블.assign(팀 = 선택한_서머리테이블.PitcherId.apply(lambda x: pinfo.get(x)['팀']))
else:
    # 시즌 소속팀 매핑 (연도, 레벨, tmid 기준)
    st_mapping = season_teams[season_teams.level_eng == current_level_eng].set_index(['year', 'tmid'])['시즌소속팀'].to_dict()
    
    def match_season_team(row):
        pid = row['PitcherId']
        yr = row['연도']
        s_team = st_mapping.get((yr, pid))
        if s_team:
            return s_team
        return pinfo.get(pid, {}).get('팀', '없음') # 정보 없으면 현소속팀으로 보완

    선택한_서머리테이블 = 선택한_서머리테이블.assign(팀 = 선택한_서머리테이블.apply(match_season_team, axis=1))

if 선택한팀 != '전체':
    선택한_서머리테이블 = 선택한_서머리테이블[선택한_서머리테이블.팀 == 선택한팀]

# 드롭다운 투수 명단 필터링 (선택된 팀에 속한 투수들만 표시)
드롭다운_투수명단 = pitchers[pitchers.tm_id.isin(선택한_서머리테이블.PitcherId.unique())]
드롭다운_투수명단 = 드롭다운_투수명단.sort_values('name')

with 셀렉터영역[3]:
    선택한투수 = st.selectbox('투수',
                              ['전체'] + list(드롭다운_투수명단.ID.unique()),
                              index=0)
if 선택한투수 == '전체':
    선택한투수ID = 드롭다운_투수명단.tm_id.unique()
    t1 = 선택한_서머리테이블[선택한_서머리테이블.PitcherId.isin(선택한투수ID)]
else:
    선택한투수ID = 선택한투수.split('(')[1].split(')')[0]
    t1 = 선택한_서머리테이블.query(f'PitcherId == {선택한투수ID}')

t1 = t1.assign(이름 = t1.PitcherId.apply(lambda x: str(pids[pids.tm_id == x].name.values[0])))
t1 = t1.assign(구종 = t1.구종.apply(lambda x: 구종영문_한글로변환.get(x)))
t1 = t1.assign(구종 = t1.구종.astype('category'))
t1 = t1.assign(구종 = t1.구종.cat.set_categories(ptype_sortlist))
t1 = t1.sort_values(['연도', 'PitcherId', '날짜', '구종'])

if 선택한연도 != '전체':
    t1 = t1[t1.연도 == 선택한연도]


with 셀렉터영역[4]:
    선택한구종 = st.selectbox('구종',
                              ['전체', '직구', '투심',
                               '슬라이더', '커터', '스위퍼', '커브',
                               '체인지업', '포크볼'],
                              index=0)

if 선택한구종 != '전체':
    t1 = t1[t1.구종 == 선택한구종]

t1 = t1.rename(columns={
    'RelSpeed': '구속',
    'SpinRate': '회전수',
    'InducedVertBreak': '수직무브',
    'HorzBreak': '좌우무브',
    'RelHeight': '릴리즈높이',
    'Extension': '익스텐션'
})


cols = ['이름', '날짜',
        '구종', '스터프+', '스터프+(모델1)', '스터프+(모델2)', '스터프+(모델3)',
        '투구수', '구속', '회전수', '수직무브', '좌우무브', '릴리즈높이',
        '익스텐션',]

if st.button('Load'):
    t1['팀'] = t1['팀'].apply(get_base64_emblem)
    
    df_to_show = t1[cols+['PitcherId', '팀']]
    df_to_show = df_to_show.sort_values(['이름', 'PitcherId', '날짜', '구종'])

    if 선택한구종 != '전체':
        df_to_show = df_to_show[df_to_show.구종 == 선택한구종]

    FINAL_COLS = ['팀'] + cols
    st.dataframe(df_to_show[FINAL_COLS]\
                 .set_index(['이름', '팀'])\
                 .sort_values(by='스터프+', ascending=False), 
                 hide_index=False,
                 width='content',
                 column_config = {
                     "팀": st.column_config.ImageColumn(label="팀", width="small"),
                     "스터프+": st.column_config.NumberColumn(
                         format="%.0f"
                     ),
                     "스터프+(모델1)": st.column_config.NumberColumn(
                         format="%.0f"
                     ),
                     "스터프+(모델2)": st.column_config.NumberColumn(
                         format="%.0f"
                     ),
                     "스터프+(모델3)": st.column_config.NumberColumn(
                         format="%.0f"
                     ),
                     "구속": st.column_config.NumberColumn(
                         format="%.1f"
                     ),
                     "회전수": st.column_config.NumberColumn(
                         format="%.0f"
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
                 },
                )


glossaryCol = st.columns(6)

with glossaryCol[-1]:
    with st.expander(':gray[모델 설명]'):
        st.caption('모델1: Polynomial Linear Regression')
        st.caption('모델2: GAM')
        st.caption('모델3: XGBoost')
        st.caption('전체는 모델1, 2, 3의 산술평균')

