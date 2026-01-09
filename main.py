import streamlit as st

pages = {
    "리더보드": [
        st.Page("pages/01_리더보드.py", title="KBO 스탯 리더보드"),
        st.Page("pages/14_구종별_리더보드.py", title="구종별 리더보드"),
    ],
    "투수 데이터": [
        st.Page("pages/02_투수_무브먼트_차트.py", title="무브먼트 차트"),
        st.Page("pages/03_투수_경기별_데이터_요약.py", title="경기별 데이터 요약"),
        st.Page("pages/04_투수_경기별_트래킹_데이터_그래프.py", title="Daily 트래킹 데이터 그래프"),
        st.Page("pages/06_투수_스터프_점수-요약.py", title="스터프 점수 - 요약"),
        st.Page("pages/07_투수_스터프_점수-경기별.py", title="스터프 점수 - 경기별"),
        st.Page("pages/05_투수_VAA_차트.py", title="VAA 차트"),
    ],
    "ABS": [
        st.Page("pages/08_구장별_ABS_존_비교.py", title="구장별 ABS 존 비교"),
    ],
    "기타": [
        st.Page("pages/11_고교야구_무브먼트_차트.py", title="고교야구 무브먼트 차트"),
        st.Page("pages/12_퓨처스_팀별_포지션_정리.py", title="퓨처스 팀별 야수 출장 포지션 정리"),
        st.Page("pages/13_리그_평균기록.py", title="리그 평균기록"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()
