import pandas as pd
import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import datetime
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from scipy.spatial import ConvexHull
from scipy.interpolate import splprep, splev

stadiumDict = {
    'Daejeon': '대전',
    'Incheon': '문학',
    'Jamsil': '잠실',
    'NCDinosMajors': '창원',
    'Suwon': '수원',
    'Sajik': '사직',
    'Gocheok': '고척',
    'DaeguPark': '대구',
    'UlsanMunsu': '울산',
}

def calcPositionAtTBase(m, c, t, GameDay=False):
    if GameDay == False:
        v = float(m.get(f'v{c}0'))
        s = float(m.get(f'{c}0'))
        a = float(m.get(f'a{c}0'))
    else:
        v = float(m.get(f'v{c}0GameDay'))
        s = float(m.get(f'{c}0GameDay'))
        a = float(m.get(f'a{c}0GameDay'))

    # x좌표 반전
    if (c == 'x'):
        return -(s + v * t + 0.5 * a * t * t)
    else:
        return (s + v * t + 0.5 * a * t * t)


def calcFlightTimeAtY(m, cy, GameDay=False):
    if GameDay == False:
        y0 = float(m.get('y0'))
        vy0 = float(m.get('vy0'))
        ay0 = float(m.get('ay0'))
    else:
        y0 = float(m.get('y0GameDay'))
        vy0 = float(m.get('vy0GameDay'))
        ay0 = float(m.get('ay0GameDay'))

    if ay0 != 0:
        return (-vy0 - ((vy0 ** 2) - 2 * ay0 * (y0 - cy))**0.5) / ay0
    else:
        return -1


def calcPositionAtT(m, t, GameDay=False):
    xp = calcPositionAtTBase(m, 'x', t, GameDay=GameDay)
    yp = calcPositionAtTBase(m, 'y', t, GameDay=GameDay)
    zp = calcPositionAtTBase(m, 'z', t, GameDay=GameDay)

    return { 'x': xp, 'y': yp, 'z': zp }

def calcPositionAtY(m, cy, GameDay=False):
    tY = calcFlightTimeAtY(m, cy, GameDay=GameDay)
    if tY > 0:
        return calcPositionAtT(m, tY, GameDay=GameDay)
    else:
        return {'x': -100, 'y': -100, 'z': -100}

'''
abs_tm_cols = [
    'game_date', 'year', 'Stadium',
    'PitcherId', 'Pitcher', 'BatterId', 'Batter',
    'PitcherTeam', 'BatterTeam',
    'PlateLocSide', 'PlateLocHeight', 'PlateLocSideGameDay', 'PlateLocHeightGameDay',
    'RelSpeed', 'Extension', 'RelSpeedGameDay',
    'x0', 'y0', 'z0', 'x0GameDay', 'y0GameDay', 'z0GameDay',
    'vx0', 'vy0', 'vz0', 'vx0GameDay', 'vy0GameDay', 'vz0GameDay',
    'ax0', 'ay0', 'az0', 'ax0GameDay', 'ay0GameDay', 'az0GameDay',
    'SzTopGameDay', 'SzBotGameDay',
    'PitchCall', 'PlayResult', 'PitchResultGameDay',
    'Outs', 'Balls', 'Strikes', 'TaggedPitchType', 'Inning', 'Top/Bottom',
]
'''

abs_tm_cols = [
    'game_date', 'Stadium',
    'PitcherId', 'BatterId',
    'PlateLocSide', 'PlateLocHeight', 'PlateLocSideGameDay', 'PlateLocHeightGameDay',
    'RelSpeed', 'Extension', 'RelSpeedGameDay',
    'x0', 'y0', 'z0', 'x0GameDay', 'y0GameDay', 'z0GameDay',
    'vx0', 'vy0', 'vz0', 'vx0GameDay', 'vy0GameDay', 'vz0GameDay',
    'ax0', 'ay0', 'az0', 'ax0GameDay', 'ay0GameDay', 'az0GameDay',
    'SzTopGameDay', 'SzBotGameDay',
    'PitchCall',
]


def show_TM_ABS_diff(df: pd.DataFrame,
                     len_games: int = 10,
                     chart_color = 'lightcoral'):
    """
    ABS-Trackman 차이 그리기 (최근 N게임 기준)
    :param len_games: 게임 N
    :param chart_color: 차트 색상
    """
    stadiums = df[~df.Stadium.isin(['Gwangju', 'Ulsan', 'UlsanMunsu', 'Pohang', 'Cheongju', 'Masan'])].Stadium.unique()

    dot_size = 50
    rightborder_x = np.ones(100)*0.2740
    leftborder_x = np.ones(100)*(-0.2740)
    rightborder_y = np.linspace(0, 1, 100)
    leftborder_y = np.linspace(0, 1, 100)

    topborder_x = np.linspace(-0.2740, 0.2740, 100)
    botborder_x = np.linspace(-0.2740, 0.2740, 100)
    topborder_y = np.ones(100)
    botborder_y = np.zeros(100)

    border_x = np.concatenate([rightborder_x, topborder_x[::-1], leftborder_x, botborder_x])
    border_y = np.concatenate([rightborder_y, topborder_y, leftborder_y[::-1], botborder_y])

    # 울산 추가로 2 row 4 col에서 3 row 4 col로 변경
    # 울산 다시 없어져서 2 row 4 col로 재변경
    f1, a1 = plt.subplots(2, 4, figsize=(16, 8), dpi=100)
    f2, a2 = plt.subplots(2, 4, figsize=(16, 8), dpi=100)
    row = 0
    col = 0

    # 만약 datetime/date 타입이면 문자열로 통일 (대시보드 출력용)
    if pd.api.types.is_datetime64_any_dtype(df['game_date']) or \
       any(isinstance(x, (datetime.date, datetime.datetime)) for x in df['game_date'].dropna().head(1)):
        df = df.assign(game_date = df.game_date.astype(str))

    for stadium in stadiums:
        games = sorted(df[df.Stadium == stadium].game_date.unique(), reverse=False)
        if len(games) > len_games:
            last_games = games[-len_games:]
        else:
            last_games = games

        ax = a1[row][col]
        ax2 = a2[row][col]

        target = df[(df.Stadium == stadium) &
                    df.game_date.isin(last_games) &
                    df.pxAtPlateMid.notnull() &
                    df.pzMid_norm.notnull() &
                    df.pxAtPlateMidGameDay.notnull() &
                    df.pzMid_norm_gameday.notnull() &
                    df.pxDiffAtMid.between(-10, 10) &
                    df.pzDiffAtTail.between(-10, 10) &
                    df.pzDiffAtMid.between(-10, 10)]

        last_games = [datetime.datetime.strptime(x, '%Y-%m-%d').date() for x in last_games]
        target = target[target.PitchCall == 'StrikeCalled']

        xoffset, yoffset = target.pxDiffAtMid.mean(), target.pzDiffAtMid.mean()
        points_TM = target[['pxAtPlateMid', 'pzMid_norm']].values.astype(np.float64)
        points_ABS = target[['pxAtPlateMidGameDay', 'pzMid_norm_gameday']].values.astype(np.float64)

        if len(points_TM) > 0:
            hull_TM = ConvexHull(points_TM)
            hull_ABS = ConvexHull(points_ABS)

            # convex hull 경계 오프셋 설정
            # ABS 기준이면 ABS 좌표를 사각형에 맞추고 트랙맨 오프셋을 추가
            # 트랙맨 좌표가 실세계 좌표라고 가정
            # ABS 스트로 나오는 공이 실제 세계에서 어느 위치에 나오는지 표시
            trackman_border_x = border_x + xoffset
            trackman_border_y = border_y + yoffset
            absborder_x = border_x
            absborder_y = border_y

            # ABS Convex Hull을 따라 순서대로 좌표를 배열
            # ABS 좌표를 사각형에 맞추고 대응되는 트랙맨 점으로 convex hull을 그림
            # ABS 스트로 나오는 공이 실제 세계에서 어느 위치에 나오는지 표시
            hull_points_TM = points_TM[hull_TM.vertices]
            hull_points_ABS = points_ABS[hull_TM.vertices] #트랙맨 외곽선에 대응되는 ABS 선들

            # B-spline 보간을 위해 hull_points에서 처음 점을 추가하여 닫힌 곡선으로 만듦
            hull_points_TM = np.concatenate([hull_points_TM, [hull_points_TM[0]]])
            hull_points_ABS = np.concatenate([hull_points_ABS, [hull_points_ABS[0]]])

            # 외곽선을 따라서 점과 선을 그림
            simplices = hull_TM.simplices
            for simplex in simplices:
                ax2.scatter(points_TM[simplex, 0], points_TM[simplex, 1], s=dot_size,
                           marker='o', c=chart_color, zorder=2)  # 원래 점들
                ax2.plot(points_TM[simplex, 0], points_TM[simplex, 1],
                        '-', c=chart_color, linewidth=1, zorder=2)  # Convex Hull을 이은 선들
            abs_zorder = 2
            tm_zorder = 1

            # 내부 색칠
            ax2.fill(hull_points_TM[:, 0], hull_points_TM[:, 1],
                     chart_color, alpha=0.6, zorder=tm_zorder)  # Convex Hull 내부 색칠
            
        ax.plot( [-0.2359, -0.2359], [0, 1], color='k', linestyle='solid', lw=1 )
        ax.plot( [0.2359, 0.2359], [0, 1], color='k', linestyle='solid', lw=1 )
        ax.plot( [-0.2740, -0.2740], [0, 1], color='grey', linestyle='dashed', lw=1 )
        ax.plot( [0.2740, 0.2740], [0, 1], color='grey', linestyle='dashed', lw=1 )
        ax.plot( [-0.2359+(0.2359+0.2359)/3, -0.2359+(0.2359+0.2359)/3], [0, 1], color='k', linestyle= '--', lw=.5 )
        ax.plot( [-0.2359+(0.2359+0.2359)*2/3, -0.2359+(0.2359+0.2359)*2/3], [0, 1], color='k', linestyle= '--', lw=.5 )

        ax.plot( [-0.2359, 0.2359], [0, 0], color='k', linestyle='solid', lw=1 )
        ax.plot( [-0.2359, 0.2359], [1, 1], color='k', linestyle='solid', lw=1 )
        ax.plot( [-0.2359, 0.2359], [1/3, 1/3], color='k', linestyle= '--', lw=.5 )
        ax.plot( [-0.2359, 0.2359], [2/3, 2/3], color='k', linestyle= '--', lw=.5 )

        ax2.plot( [-0.2359, -0.2359], [0, 1], color='k', linestyle='solid', lw=1 )
        ax2.plot( [0.2359, 0.2359], [0, 1], color='k', linestyle='solid', lw=1 )
        ax2.plot( [-0.2740, -0.2740], [0, 1], color='grey', linestyle='dashed', lw=1 )
        ax2.plot( [0.2740, 0.2740], [0, 1], color='grey', linestyle='dashed', lw=1 )
        ax2.plot( [-0.2359+(0.2359+0.2359)/3, -0.2359+(0.2359+0.2359)/3], [0, 1], color='k', linestyle= '--', lw=.5 )
        ax2.plot( [-0.2359+(0.2359+0.2359)*2/3, -0.2359+(0.2359+0.2359)*2/3], [0, 1], color='k', linestyle= '--', lw=.5 )

        ax2.plot( [-0.2359, 0.2359], [0, 0], color='k', linestyle='solid', lw=1 )
        ax2.plot( [-0.2359, 0.2359], [1, 1], color='k', linestyle='solid', lw=1 )
        ax2.plot( [-0.2359, 0.2359], [1/3, 1/3], color='k', linestyle= '--', lw=.5 )
        ax2.plot( [-0.2359, 0.2359], [2/3, 2/3], color='k', linestyle= '--', lw=.5 )

        ax.fill(trackman_border_x, trackman_border_y, chart_color, alpha=0.6, label='트랙맨', zorder=tm_zorder)
        
        hp_img = mpimg.imread('images/hp_reverse_transparent.png')
        hp_imagebox1 = OffsetImage(hp_img, zoom=.225, alpha=1)
        hp_ab1 = AnnotationBbox(hp_imagebox1, (0, -0.45), frameon=False)
        hp_artist1 = ax.add_artist(hp_ab1)
        hp_artist1.set_zorder(-3)

        hp_img = mpimg.imread('images/hp_reverse_transparent.png')
        hp_imagebox1 = OffsetImage(hp_img, zoom=.225, alpha=1)
        hp_ab1 = AnnotationBbox(hp_imagebox1, (0, -0.45), frameon=False)
        hp_artist1 = ax2.add_artist(hp_ab1)
        hp_artist1.set_zorder(-3)

        ax.set_xbound(-0.45, 0.45); ax.set_ybound(-0.45, 1.45)
        ax.axis('off')
        if len(target) > len_games:
            ax.set_title(f"{stadiumDict[stadium]} 최근 {len_games}경기", fontsize=20)
        else:
            ax.set_title(f"{stadiumDict[stadium]}", fontsize=20)
        ax.text(0, 1.25,
                ha='center', fontsize=20,
                s=f"({last_games[0].strftime('%-m/%-d')} - {last_games[-1].strftime('%-m/%-d')})")

        ax2.set_xbound(-0.45, 0.45); ax2.set_ybound(-0.45, 1.45)
        ax2.axis('off')
        if len(target) > len_games:
            ax2.set_title(f"{stadiumDict[stadium]} 최근 {len_games}경기", fontsize=20)
        else:
            ax2.set_title(f"{stadiumDict[stadium]}", fontsize=20)
        ax2.text(0, 1.25,
                 ha='center', fontsize=20,
                 s=f"({last_games[0].strftime('%-m/%-d')} - {last_games[-1].strftime('%-m/%-d')})")

        if col+1 == 4:
            row = row + 1
        col = (col+1)%4

    return f1, f2

def show_TM_ABS_diff2(df: pd.DataFrame,
                      시작일: None,
                      종료일: None,
                      chart_color = 'lightcoral'):
    """
    ABS-Trackman 차이 그리기 (최근 N게임 기준)
    :param 시작일: 시작일
    :param 종료일: 종료일
    :param chart_color: 차트 색상
    """
    stadiums = df[~df.Stadium.isin(['Gwangju', 'Ulsan', 'UlsanMunsu', 'Pohang', 'Cheongju', 'Masan'])].Stadium.unique()

    dot_size = 50
    rightborder_x = np.ones(100)*0.2740
    leftborder_x = np.ones(100)*(-0.2740)
    rightborder_y = np.linspace(0, 1, 100)
    leftborder_y = np.linspace(0, 1, 100)

    topborder_x = np.linspace(-0.2740, 0.2740, 100)
    botborder_x = np.linspace(-0.2740, 0.2740, 100)
    topborder_y = np.ones(100)
    botborder_y = np.zeros(100)

    border_x = np.concatenate([rightborder_x, topborder_x[::-1], leftborder_x, botborder_x])
    border_y = np.concatenate([rightborder_y, topborder_y, leftborder_y[::-1], botborder_y])

    # 울산 추가로 2 row 4 col에서 3 row 4 col로 변경
    # 울산 다시 없어져서 2 row 4 col로 재변경
    f1, a1 = plt.subplots(2, 4, figsize=(16, 8), dpi=100)
    f2, a2 = plt.subplots(2, 4, figsize=(16, 8), dpi=100)
    row = 0
    col = 0
    
    df['game_date'] = pd.to_datetime(df.game_date).dt.date

    for stadium in stadiums:
        ax = a1[row][col]
        ax2 = a2[row][col]

        ax.plot( [-0.2359, -0.2359], [0, 1], color='k', linestyle='solid', lw=1 )
        ax.plot( [0.2359, 0.2359], [0, 1], color='k', linestyle='solid', lw=1 )
        ax.plot( [-0.2740, -0.2740], [0, 1], color='grey', linestyle='dashed', lw=1 )
        ax.plot( [0.2740, 0.2740], [0, 1], color='grey', linestyle='dashed', lw=1 )
        ax.plot( [-0.2359+(0.2359+0.2359)/3, -0.2359+(0.2359+0.2359)/3], [0, 1], color='k', linestyle= '--', lw=.5 )
        ax.plot( [-0.2359+(0.2359+0.2359)*2/3, -0.2359+(0.2359+0.2359)*2/3], [0, 1], color='k', linestyle= '--', lw=.5 )

        ax.plot( [-0.2359, 0.2359], [0, 0], color='k', linestyle='solid', lw=1 )
        ax.plot( [-0.2359, 0.2359], [1, 1], color='k', linestyle='solid', lw=1 )
        ax.plot( [-0.2359, 0.2359], [1/3, 1/3], color='k', linestyle= '--', lw=.5 )
        ax.plot( [-0.2359, 0.2359], [2/3, 2/3], color='k', linestyle= '--', lw=.5 )

        ax2.plot( [-0.2359, -0.2359], [0, 1], color='k', linestyle='solid', lw=1 )
        ax2.plot( [0.2359, 0.2359], [0, 1], color='k', linestyle='solid', lw=1 )
        ax2.plot( [-0.2740, -0.2740], [0, 1], color='grey', linestyle='dashed', lw=1 )
        ax2.plot( [0.2740, 0.2740], [0, 1], color='grey', linestyle='dashed', lw=1 )
        ax2.plot( [-0.2359+(0.2359+0.2359)/3, -0.2359+(0.2359+0.2359)/3], [0, 1], color='k', linestyle= '--', lw=.5 )
        ax2.plot( [-0.2359+(0.2359+0.2359)*2/3, -0.2359+(0.2359+0.2359)*2/3], [0, 1], color='k', linestyle= '--', lw=.5 )

        ax2.plot( [-0.2359, 0.2359], [0, 0], color='k', linestyle='solid', lw=1 )
        ax2.plot( [-0.2359, 0.2359], [1, 1], color='k', linestyle='solid', lw=1 )
        ax2.plot( [-0.2359, 0.2359], [1/3, 1/3], color='k', linestyle= '--', lw=.5 )
        ax2.plot( [-0.2359, 0.2359], [2/3, 2/3], color='k', linestyle= '--', lw=.5 )
        
        hp_img = mpimg.imread('images/hp_reverse_transparent.png')
        hp_imagebox1 = OffsetImage(hp_img, zoom=.225, alpha=1)
        hp_ab1 = AnnotationBbox(hp_imagebox1, (0, -0.45), frameon=False)
        hp_artist1 = ax.add_artist(hp_ab1)
        hp_artist1.set_zorder(-3)

        hp_img = mpimg.imread('images/hp_reverse_transparent.png')
        hp_imagebox1 = OffsetImage(hp_img, zoom=.225, alpha=1)
        hp_ab1 = AnnotationBbox(hp_imagebox1, (0, -0.45), frameon=False)
        hp_artist1 = ax2.add_artist(hp_ab1)
        hp_artist1.set_zorder(-3)

        len_games = 0

        if len(df) > 0:
            target = df[(df.Stadium == stadium) &
                        (df.game_date >= 시작일) &
                        (df.game_date <= 종료일) &
                        df.pxAtPlateMid.notnull() &
                        df.pzMid_norm.notnull() &
                        df.pxAtPlateMidGameDay.notnull() &
                        df.pzMid_norm_gameday.notnull() &
                        df.pxDiffAtMid.between(-10, 10) &
                        df.pzDiffAtTail.between(-10, 10) &
                        df.pzDiffAtMid.between(-10, 10)]
            games = sorted(target.game_date.unique(), reverse=False)
            target = target[target.PitchCall == 'StrikeCalled']

            xoffset, yoffset = target.pxDiffAtMid.mean(), target.pzDiffAtMid.mean()
            points_TM = target[['pxAtPlateMid', 'pzMid_norm']].values.astype(np.float64)
            points_ABS = target[['pxAtPlateMidGameDay', 'pzMid_norm_gameday']].values.astype(np.float64)

            if (len(points_TM) == 0) & (len(points_ABS) == 0):
                ax.set_title(f"{stadiumDict[stadium]} - 경기 없음", fontsize=20)
                ax2.set_title(f"{stadiumDict[stadium]} - 경기 없음", fontsize=20)

                pass
            else:
                len_games = len(games)
                hull_TM = ConvexHull(points_TM)
                hull_ABS = ConvexHull(points_ABS)

                # convex hull 경계 오프셋 설정
                # ABS 기준이면 ABS 좌표를 사각형에 맞추고 트랙맨 오프셋을 추가
                # 트랙맨 좌표가 실세계 좌표라고 가정
                # ABS 스트로 나오는 공이 실제 세계에서 어느 위치에 나오는지 표시
                trackman_border_x = border_x + xoffset
                trackman_border_y = border_y + yoffset

                ax.fill(trackman_border_x, trackman_border_y, chart_color, alpha=0.6, label='트랙맨', zorder=1)

                # ABS Convex Hull을 따라 순서대로 좌표를 배열
                # ABS 좌표를 사각형에 맞추고 대응되는 트랙맨 점으로 convex hull을 그림
                # ABS 스트로 나오는 공이 실제 세계에서 어느 위치에 나오는지 표시
                hull_points_TM = points_TM[hull_TM.vertices]

                # B-spline 보간을 위해 hull_points에서 처음 점을 추가하여 닫힌 곡선으로 만듦
                hull_points_TM = np.concatenate([hull_points_TM, [hull_points_TM[0]]])

                # 외곽선을 따라서 점과 선을 그림
                simplices = hull_TM.simplices
                for simplex in simplices:
                    ax2.scatter(points_TM[simplex, 0], points_TM[simplex, 1], s=dot_size,
                               marker='o', c=chart_color, zorder=2)  # 원래 점들
                    ax2.plot(points_TM[simplex, 0], points_TM[simplex, 1],
                            '-', c=chart_color, linewidth=1, zorder=2)  # Convex Hull을 이은 선들

                # 내부 색칠
                ax2.fill(hull_points_TM[:, 0], hull_points_TM[:, 1],
                         chart_color, alpha=0.6, zorder=1)  # Convex Hull 내부 색칠

                ax.set_title(f"{stadiumDict[stadium]} {시작일.strftime('%-m/%-d')} - {종료일.strftime('%-m/%-d')} ({len(games)}경기)", fontsize=20)
                ax2.set_title(f"{stadiumDict[stadium]} {시작일.strftime('%-m/%-d')} - {종료일.strftime('%-m/%-d')} ({len(games)}경기)", fontsize=20)

        ax.set_xbound(-0.45, 0.45); ax.set_ybound(-0.45, 1.45)
        ax.axis('off')

        ax2.set_xbound(-0.45, 0.45); ax2.set_ybound(-0.45, 1.45)
        ax2.axis('off')
        if col+1 == 4:
            row = row + 1
        col = (col+1)%4

    return f1, f2
