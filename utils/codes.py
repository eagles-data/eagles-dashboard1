from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from enum import IntEnum
import numpy as np
import streamlit as st

# 2026 season
season_start_month = 3
season_start_day = 28
preseason_start_month = 3
preseason_start_day = 12
futures_season_start_month = 3
futures_season_start_day = 20


class SACode(IntEnum):
    Barrel = 0
    SolidContact = 1
    FlareBurner = 2
    PoorlyUnder = 3
    PoorlyTopped = 4
    PoorlyWeak = 5
    Unclassified = 6


class EVLABBClass(IntEnum):
    BR = 0
    LD = 1
    FB = 2
    GB = 3
    PU = 4
    UC = 5


pitchtype_sortlist = ['Fastball', 'Sinker', 'Slider', 'Cutter', 'Curveball', 'Sweeper',
                      'ChangeUp', 'Splitter', 'Knuckleball', 'Other', 'Undefined']

ptype_sortlist = ['직구(포심)', '직구', '직구(투심)', '직구(싱커)', '직구(원심)', '싱커', '투심',
                  '슬라이더', '커터', '스위퍼', '커브', '너클커브', '슬로커브', '슬러브',
                  '체인지업', '스플리터', '포크볼', '스크류볼', '너클볼', '이퓨스', '미분류']

구종영문_한글로변환 = {
                      'Fastball': '직구',
                      'Sinker': '투심',
                      'Slider': '슬라이더',
                      'Cutter': '커터',
                      'Sweeper': '스위퍼',
                      'Curveball': '커브',
                      'Slurve': '슬러브',
                      'Changeup': '체인지업',
                      'ChangeUp': '체인지업',
                      'Splitter': '포크볼',
                      'Forkball': '포크볼',
                      'Screwball': '스크류볼',
                      'Knuckleball': '너클볼',
                      'Eephus': '이퓨스',
                      'Other': '기타',
                      'Undefined': '미분류'
                  }
구종한글_영문으로변환 = {
    '직구': 'Fastball',
    '투심': 'Sinker',
    '슬라이더': 'Slider',
    '슬라': 'Slider',
    '커터': 'Cutter',
    '스위퍼': 'Sweeper',
    '스위': 'Sweeper',
    '커브': 'Curveball',
    '슬러브': 'Slurve',
    '체인지업': 'ChangeUp',
    '체인': 'ChangeUp',
    '포크': 'Splitter',
    '포크볼': 'Splitter',
    '스플리터': 'Splitter',
    '스플': 'Splitter',
    '너클볼': 'Knuckleball',
    '너클': 'Knuckleball',
    '기타': 'Other',
    '미분류': 'Undefined'
}

구종별_마커 = {
    'Fastball': 'o',
    'Sinker': 'v',
    'Cutter': '<',
    'Cutter-R': '<',
    'Cutter-L': '>',
    'Slider': '<',
    'Slider-R': '<',
    'Slider-L': '>',
    'Curveball': '^',
    'Slurve': '^',
    'Sweeper': '^',
    'ChangeUp': 's',
    'Splitter': 'D',
    'Forkball': 'D',
    'Knuckleball': 'x',
    'Eephus': 'x',
    'Other': 'x',
    'Undefined': 'x'
}


ball_colors = {
    'Fastball': '#ff0000',
    'Sinker': '#ff7800',
    'Cutter': '#00ff00',
    'Slider': '#00aa00',
    'Sweeper': '#4f8f00',
    'Curveball': '#000000',
    'ChangeUp': '#0000ff',
    'Splitter': '#a01ff0',
    'Forkball': '#a01ff0',
    '직구': '#ff0000',
    '포심': '#ff0000',
    '투심': '#ff7800',
    '싱커': '#ff7800',
    '커터': '#00ff00',
    '슬라': '#00aa00',
    '슬라이더': '#00aa00',
    '스위퍼': '#4f8f00',
    '스위': '#4f8f00',
    '커브': '#000000',
    '체인': '#0000ff',
    '체인지업': '#0000ff',
    '스플': '#a01ff0',
    '스플리터': '#a01ff0',
    '포크': '#a01ff0',
    '포크볼': '#a01ff0',
    '스크류볼': '#a01ff0',
    '너클볼': '#a01ff0',
    '이퓨스': '#a01ff0',
    '미분류': '#888888',
    'Eephus': '#a01ff0',
    'Undefined': '#888888',
}

손변환 = {
    'Right': '우',
    'Left': '좌',
    'Side': '우사',
    'LSide': '좌사',
    'Switch': '스위치',
}

구종순서 = ['직구', '투심',
            '슬라', '슬라이더', '커터', '커브', '스위퍼',
            '체인', '체인지업', '포크', '포크볼', '스플', '스플리터',
            '너클', '너클볼', '기타', '미분류', 'Undefined']

손순서 = ['우', '좌', '우사', '좌사', '스위치']


고교야구팀들 = {
    "EPBC(U-18)": ["EUN_U19"],
    "GD챌린저스BC(U18)": ["CHA_CHA15"],
    "HGBC(U-18)": ["HGB_HGB"],
    "TKBC(U19)": ["TKB_TKB"],
    "TNPBA(U-18)": ["TNP_BAS"],
    "강릉고": ["GAN_HIG"],
    "강원고": ["KAN_HIG"],
    "개성고": ["GAE_GAE"],
    "거제BC(U18)": ["GEO_U-1"],
    "경기고": ["GYE_GYE"],
    "경기상업고": ["GYE_TEC"],
    "경기항공고": ["GYE_AVI"],
    "경남고": ["KYU_KYU"],
    "경동고": ["KYU_KYU2"],
    "경민IT고": ["KYU_KYU1"],
    "경북고": ["KYU_HIG"],
    "경주고": ["GYE_HIG"],
    "공주고": ["GON_HIS"],
    "광남고BC(U18)": ["GWA_GWA"],
    "광주동성고": ["GWA_DON"],
    "광주제일고": ["GWA_JAE"],
    "광주진흥고": ["GWA_JIN"],
    "광주BC(U-18)": ["GWA_BC("],
    "군산상업고": ["GUN_COM"],
    "군산상일고": ["GUN_SAN"],
    "글로벌선진학교": ["GSJHS"],
    "금남고": ["GEU_HIG"],
    "김해고": ["GIM_HIS"],
    "나주광남고": ["NAN_GWA"],
    "남양주금곡BC(U-19)": ["NAM_GEU"],
    "남양주GK(U18)": ["NAM_GEU"],
    "달서구BC야구단(U-18)": ["DAL_BC("],
    "대구고": ["DAE_HIG"],
    "대구북구SC(U-18)": ["DAE_BUK"],
    "대구상원고": ["DAE_SAN"],
    "대전고": ["DAE_DAE"],
    "대전제일고": ["DAE_JEI"],
    "덕수고": ["DEO_DEO"],
    "덕적고": ["DEO_DEO1"],
    "도개고": ["DOG_HIG"],
    "동산고": ["DON_DON"],
    "라온고": ["RAO_HIS"],
    "마산고": ["MAS_MAS"],
    "마산용마고": ["MAS_YON"],
    "물금고": ["MUL_HIG"],
    "배명고": ["BAE_HIG"],
    "배재고": ["BAE_HIG1"],
    "백송고": ["BAC_HIG"],
    "부경고": ["BUG_HIG"],
    "부산고": ["BUS_HIG"],
    "부산공업고": ["BUS_TEC"],
    "부산정보고SBC": ["BUS_INF"],
    "부천고": ["BUC_HIG"],
    "북일고": ["BUG_HIG1"],
    "분당BC(U18)": ["BUN_BUN"],
    "비봉고": ["BIB_HIG"],
    "상동고": ["SAN_HIG"],
    "상우고": ["SAN_WOO"],
    "서울고": ["KHS_SEO"],
    "서울동산고": ["SEO_DON"],
    "서울디자인고": ["SEO_DES"],
    "서울자동차고": ["SEO_CAR"],
    "서울컨벤션고": ["KHSSC"],
    "서울HK야구단(U-18)": ["SEO_SEO"],
    "선린인터넷고": ["KHSSR"],
    "설악고": ["KHS_SRK"],
    "성남고": ["SEO_N"],
    "성지고": ["SEO_J"],
    "세광고": ["KHS_SEK"],
    "세원고": ["SEW_HIG"],
    "소래고": ["SOR_H"],
    "순천효천고": ["HYO_HYO"],
    "신일고": ["KHS_SHI"],
    "신흥고": ["SHI_H"],
    "안산공업고": ["ANS_TEC"],
    "야로고BC": ["YAR_B"],
    "야탑고": ["KHS_YAT"],
    "여주IDBC": ["YEO_IDB"],
    "예일메디텍고": ["YEI_MEY"],
    "온양BC(U18)": ["ONY_ONY"],
    "용인시야구단(U-18)": ["YON_BC("],
    "우성베이스볼AC": ["WOO_WOO"],
    "우신고": ["WSHS"],
    "울산공고BC": ["KHS_ULS"],
    "원주고": ["KHS_WON"],
    "유신고": ["YSHS"],
    "율곡고": ["YG_HS"],
    "의성고": ["UIS_UIS"],
    "의왕BC(U18)": ["UIW_BC("],
    "인상고": ["INS_INS"],
    "인창고": ["INC_HIG"],
    "인천고": ["KHSIN"],
    "장안고": ["JAN_JAN"],
    "장충고": ["JAN_JAN1"],
    "전주고": ["JEO_HIG"],
    "제물포고": ["JEM_HIG"],
    "제주고": ["JEJ_JEJ"],
    "중앙고": ["JOO_HIG"],
    "진영고": ["JIN_HIG"],
    "창원공고야구단": ["CHA_TEC"],
    "천안CS": ["CHE_CHE1"],
    "천안CSBC(U-18)": ["CHE_CHE1"],
    "청담고": ["CHU_CHU"],
    "청원고": ["CHE_CHE2"],
    "청주고": ["CHU_HIG"],
    "충암고": ["CHU_CHU1"],
    "충훈고": ["CHO_HIG"],
    "포항제철고": ["POH_JAE"],
    "한광BC(U-18)": ["HAN_BC("],
    "한국마사BC(U18)": ["KOR_MAS"],
    "한국K-POP고": ["KOR_K-P"],
    "화성동탄B(U-18)": ["DON_BC("],
    "화순고": ["HWA_HIG"],
    "휘문고": ["KHSWM"]
};


투수컬럼명변환 = {
    'year': '연도',
    'level': '레벨',
    'IP': '이닝',
    'PA': '타자',
    'hit': '피안타',
    'strikeout': '탈삼진',
    'walk': '볼넷',
    'homerun': '홈런',
    'k_rate': 'K%',
    'bb_rate': 'BB%',
    'k_minus_bb_rate': 'K-BB%',
    'hr_rate': 'HR%',
    'k_per_9': 'K/9',
    'bb_per_9': 'BB/9',
    'hr_per_9': 'HR/9',
    'BA': '피안타율',
    'OBP': '피출루율',
    'SLG': '피장타율',
    'OPS': '피OPS',
    'BABIP': 'BABIP',
    'xBA': '기대피안타율',
    'xOBP': '기대피출루율',
    'xSLG': '기대피장타율',
    'xOPS': '기대피OPS',
    'zone_rate': '존%',
    'strike_rate': '스트%',
    'csw_rate': 'CSW%',
    'whiff_rate': '헛스윙%',
    'zcon_rate': '존컨택%',
    'chase_rate': '체이스%',
    'gb_rate': '땅볼%',
    'ld_rate': '라인%',
    'fb_rate': '뜬공%',
    'pu_rate': '팝업%',
    'gb_per_fb': '땅/뜬',
    'hardhit_rate': '강한타구%',
    'barrel_rate': '배럴%',
    'flareburner_rate': '안타성타구%',
    'pitches': '투구수',
}

타자컬럼명변환 = {
    'year': '연도',
    'level': '레벨',
    'PA': '타석',
    'AB': '타수',
    'homerun': '홈런',
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
    'flareburner_rate': '안타성타구%',
    'zswing_rate': '존스윙%',
    'zcon_rate': '존컨택%',
    'chase_rate': '체이스%',
    'swing_rate': '스윙%',
    'ocon_rate': '아웃컨%',
    'con_rate': '컨택%',
    'gb_rate': '땅볼%',
    'ld_rate': '라인%',
    'fb_rate': '뜬공%',
    'pu_rate': '팝업%',
    'pull_rate': '당긴%',
    'center_rate': '가운데%',
    'oppo_rate': '밀어친%',
    'max_ev': '최대 타구속도',
    'mean_ev': '평균 타구속도',
    'mean_la': '평균 발사각도',
    'BIPs': '인플레이 타구수',
    'pullair_rate': 'PullAir%',
    'hardhits': '강한 타구수',
    't10_ev': 'T-10',
    'pd_plus_ev': 'PD+EV',
}



투수컬럼포맷설정 = {
     "이닝": st.column_config.NumberColumn(format='%.1f'),
     "WHIP": st.column_config.NumberColumn(format='%.2f'),
     "K%": st.column_config.NumberColumn(format='%.1f'),
     "BB%": st.column_config.NumberColumn(format='%.1f'),
     "HR%": st.column_config.NumberColumn(format='%.1f'),
     "K-BB%": st.column_config.NumberColumn(format='%.1f'),
     "K/9": st.column_config.NumberColumn(format='%.1f'),
     "BB/9": st.column_config.NumberColumn(format='%.1f'),
     "HR/9": st.column_config.NumberColumn(format='%.1f'),
     "피안타율": st.column_config.NumberColumn(format='%.3f'),
     "피출루율": st.column_config.NumberColumn(format='%.3f'),
     "피장타율": st.column_config.NumberColumn(format='%.3f'),
     "피OPS": st.column_config.NumberColumn(format='%.3f'),
     "BABIP": st.column_config.NumberColumn(format='%.3f', help="인플레이 타구의 타율; (안타-홈런)/(타수+희플-삼진-홈런)"),
     "기대피안타율": st.column_config.NumberColumn(format='%.3f', help='인플레이 타구의 타구속도&발사각에 근거해 예상된 타율'),
     "기대피출루율": st.column_config.NumberColumn(format='%.3f', help='인플레이 타구의 타구속도&발사각에 근거해 예상된 출루율'),
     "기대피장타율": st.column_config.NumberColumn(format='%.3f', help='인플레이 타구의 타구속도&발사각에 근거해 예상된 장타율'),
     "기대피OPS": st.column_config.NumberColumn(format='%.3f', help='인플레이 타구의 타구속도&발사각에 근거해 예상된 OPS'),
     "존%": st.column_config.NumberColumn(format='%.1f'),
     "스트%": st.column_config.NumberColumn(format='%.1f'),
     "땅볼%": st.column_config.NumberColumn(format='%.1f'),
     "라인%": st.column_config.NumberColumn(format='%.1f'),
     "뜬공%": st.column_config.NumberColumn(format='%.1f'),
     "팝업%": st.column_config.NumberColumn(format='%.1f'),
     "땅/뜬": st.column_config.NumberColumn(format='%.2f'),
     "강한타구%": st.column_config.NumberColumn(format='%.1f', help='인플레이 타구 중 타구속도 153km/h 이상인 강한 타구의 비율'),
     "배럴%": st.column_config.NumberColumn(format='%.1f', help='배럴타구 비율; 배럴타구는 타구속도&발사각 기준 기대타율 5할 이상, 기대장타율 1.500 이상인 타구'),
     "안타성타구%": st.column_config.NumberColumn(format='%.1f', help='배럴은 아니지만 기대타율 5할 이상인 타구; 외야 앞에 떨어지는 라인드라이브/텍사스 안타, 강하지만 각도가 낮은 땅볼/라이너 타구 등이 해당함'),
     "CSW%": st.column_config.NumberColumn(format='%.1f', help='전체 투구 중 헛스윙과 루킹스트라이크 비율'),
     "헛스윙%": st.column_config.NumberColumn(format='%.1f', help='스윙이 나왔을 때 헛스윙이 된 비율'),
     "존컨택%": st.column_config.NumberColumn(format='%.1f', help='S존 안에 투구했을 때 컨택된 비율'),
     "체이스%": st.column_config.NumberColumn(format='%.1f', help='존 밖에 투구했을 때 스윙이 끌려나온 비율'),
}
타자컬럼포맷설정 = {
     "K%": st.column_config.NumberColumn(format='%.1f'),
     "BB%": st.column_config.NumberColumn(format='%.1f'),
     "HR%": st.column_config.NumberColumn(format='%.1f'),
     "타율": st.column_config.NumberColumn(format='%.3f'),
     "출루율": st.column_config.NumberColumn(format='%.3f'),
     "장타율": st.column_config.NumberColumn(format='%.3f'),
     "OPS": st.column_config.NumberColumn(format='%.3f'),
     "BABIP": st.column_config.NumberColumn(format='%.3f', help="인플레이 타구의 타율; (안타-홈런)/(타수+희플-삼진-홈런)"),
     "기대타율": st.column_config.NumberColumn(format='%.3f', help='인플레이 타구의 타구속도&발사각에 근거해 예상된 타율'),
     "기대출루율": st.column_config.NumberColumn(format='%.3f', help='인플레이 타구의 타구속도&발사각에 근거해 예상된 출루율'),
     "기대장타율": st.column_config.NumberColumn(format='%.3f', help='인플레이 타구의 타구속도&발사각에 근거해 예상된 장타율'),
     "기대OPS": st.column_config.NumberColumn(format='%.3f', help='인플레이 타구의 타구속도&발사각에 근거해 예상된 OPS'),
     "wOBA": st.column_config.NumberColumn(format='%.3f', help='안타/볼넷/사구 등 각 결과에 가중치를 부여, 계산한 종합 타격 생산성지표'),
     "기대wOBA": st.column_config.NumberColumn(format='%.3f', help='인플레이 타구의 타구속도&발사각에 근거해 예상된 wOBA'),
     "땅볼%": st.column_config.NumberColumn(format='%.1f'),
     "라인%": st.column_config.NumberColumn(format='%.1f'),
     "뜬공%": st.column_config.NumberColumn(format='%.1f'),
     "팝업%": st.column_config.NumberColumn(format='%.1f'),
     "강한타구%": st.column_config.NumberColumn(format='%.1f', help='인플레이 타구 중 타구속도 153km/h 이상인 강한 타구의 비율'),
     "배럴%": st.column_config.NumberColumn(format='%.1f', help='배럴타구 비율; 배럴타구는 타구속도&발사각 기준 기대타율 5할 이상, 기대장타율 1.500 이상인 타구'),
     "안타성타구%": st.column_config.NumberColumn(format='%.1f', help='배럴은 아니지만 기대타율 5할 이상인 타구; 외야 앞에 떨어지는 라인드라이브/텍사스 안타, 강하지만 각도가 낮은 땅볼/라이너 타구 등이 해당함'),
     "존스윙%": st.column_config.NumberColumn(format='%.1f', help='S존 안에 들어온 공에 스윙한 비율'),
     "존컨택%": st.column_config.NumberColumn(format='%.1f', help='S존 안 공에 스윙했을 때 컨택트에 성공한 비율'),
     "체이스%": st.column_config.NumberColumn(format='%.1f', help='S존 바깥의 공에 스윙이 나간 비율'),
     "스윙%": st.column_config.NumberColumn(format='%.1f', help='전체 투구 중 스윙이 나간 비율'),
     "컨택%": st.column_config.NumberColumn(format='%.1f', help='스윙했을 때 컨택트에 성공한 비율'),
     "아웃컨%": st.column_config.NumberColumn(format='%.1f', help='S존 바깥의 공에 스윙했을 때 컨택트에 성공한 비율'),
     "PullAir%": st.column_config.NumberColumn(format='%.1f', help='인플레이 타구 중, 당겨서 라이너/뜬공이 된 타구의 비율; PullAir는 방향+상하각도 분류 중 기대생산성이 가장 높은 유형의 타구임'),
     "당긴%": st.column_config.NumberColumn(format='%.1f', help='인플레이 타구 중, 당겨친 타구의 비율'),
     "가운데%": st.column_config.NumberColumn(format='%.1f', help='인플레이 타구 중, 가운데 방향으로 보낸 타구의 비율'),
     "밀어친%": st.column_config.NumberColumn(format='%.1f', help='인플레이 타구 중, 밀어친 타구의 비율'),
     "PD+EV": st.column_config.NumberColumn(format='%.1f', help='(T-10)x2 + (존컨택-체이스x2)'),
     "T-10": st.column_config.NumberColumn(format='%.1f', help='선수 개인의 인플레이 타구속도 중 기준 상위 10%에 해당하는 값'),
     "최대 타구속도": st.column_config.NumberColumn(format='%.1f', help='선수 개인의 인플레이 타구속도 최대값'),
     "평균 타구속도": st.column_config.NumberColumn(format='%.1f', help='선수 개인의 인플레이 타구속도 평균값'),
     "평균 발사각도": st.column_config.NumberColumn(format='%.1f', help='선수 개인의 인플레이 타구 발사각도 평균값'),
 }

타자리더보드_표시컬럼 = [
    '나이',
    '타석', '홈런', '타율', '출루율', '장타율', 'OPS',
    'BB%', 'K%', 'HR%', 'BABIP',
    '기대타율', '기대출루율', '기대장타율', '기대OPS',
    'wOBA', '기대wOBA', '체이스%', '존컨택%', '존스윙%', '스윙%', '컨택%',
    'PD+EV', 'T-10',
    '강한타구%', '배럴%','PullAir%', '안타성타구%',
    '당긴%', '가운데%', '밀어친%',
    '땅볼%', '라인%', '뜬공%', '팝업%',
    '최대 타구속도', '평균 타구속도', '평균 발사각도',
    '인플레이 타구수', '강한 타구수',
    # 타수, 아웃컨%
]

투수리더보드_표시컬럼 = [
    '나이',
    '이닝', 'WHIP', '타자', '피안타', '탈삼진', '볼넷', '홈런',
    'K%', 'BB%', 'K-BB%', 'HR%', 'K/9', 'BB/9', 'HR/9',
    'CSW%' ,'헛스윙%', '존컨택%', '체이스%',
    '스트%', '존%', 
    '피안타율', '피출루율', '피장타율', '피OPS', 'BABIP',
    '기대피안타율', '기대피출루율', '기대피장타율', '기대피OPS',
    '땅볼%', '라인%', '뜬공%', '팝업%', '땅/뜬',
    '강한타구%', '배럴%', '안타성타구%', '투구수',
]

p_kor_dict = {
    'Fastball': '직구',
    'Sinker': '투심',
    'Cutter': '커터',
    'Slider': '슬라이더',
    'Sweeper': '스위퍼',
    'Curveball': '커브',
    'ChangeUp': '체인지업',
    'Splitter': '포크볼',
    'Knuckleball': '너클볼',
    'Forkball': '포크볼',
}

stadiumDict = {
    'Daejeon': '대전',
    'Incheon': '문학',
    'Jamsil': '잠실',
    'NCDinosMajors': '창원',
    'Suwon': '수원',
    'Sajik': '사직',
    'Gocheok': '고척',
    'DaeguPark': '대구'
}

sort_order = list(ball_colors.keys())
coolwarm_trim = ListedColormap(np.vstack((np.zeros((10,4)), cm.coolwarm(np.linspace(0, 1, 256))[10:])))
orange_grey = ListedColormap(np.vstack((np.zeros((10,4)),
                                        cm.Greys(np.linspace(0, 1, 256))[128:10:-1],
                                        cm.Oranges(np.linspace(0, 1, 128)))))
red_layer_color = (0.98, 0.29, 0.32, 1)
yellow_layer_color = (0.98, 0.99, 0.16, 1)
blue_layer_color = (65/255, 105/255, 225/255, 1)

rwb_front = np.linspace(red_layer_color, yellow_layer_color, 85).reshape(85, 4)
rwb_back = np.linspace(np.ones((1, 4)), np.asarray(blue_layer_color), 85).reshape(85, 4)
rwb = ListedColormap(np.vstack((rwb_front, np.ones((86, 4)), rwb_back)))

레벨영어변환 = {
    '1군': 'kbo',
    '퓨처스': 'kbo minors',
    '정규': 'regular',
    '포스트시즌': 'postseason',
    '정규+포시': 'regular and postseason',
    '시범': 'exhibition',
    '전체': None
}
