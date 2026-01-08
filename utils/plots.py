import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.image as mpimg
import matplotlib as mpl
import matplotlib.colors as mcolors
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Ellipse
from sklearn.decomposition import PCA

from .codes import *

def set_fonts():
    fe = fm.FontEntry(fname=r'./Fonts/NanumGothic.ttf', # ttf 파일이 저장되어 있는 경로
                      name='NanumGothic')                        # 이 폰트의 원하는 이름 설정
    fm.fontManager.ttflist.insert(0, fe)              # Matplotlib에 폰트 추가
    plt.rcParams.update({
        'font.size': 18,
        'font.family': 'NanumGothic',
        'axes.unicode_minus': False
    }) # 폰트 설정


def movement_plot(df,
                  player=None,
                  pid=None,
                  futures=False,
                  ax=None,
                  freq_th=0.05,
                  instant=False,
                  eng=False,
                  show_batter_img=False,
                  draw_dots=False, sample_dots=False,
                  draw_usage=False,
                  draw_lg_avg=False,
                  lg_avg_df=None,
                  show_PTS=False):
    """
    무브먼트 플롯을 그린다.

    Parameters:
        df: 트랙맨 데이터가 포함된 pandas dataframe.

        player: 투수 이름; 데이터프레임에서 Pitcher 값이 해당 이름과 같은 것만 골라내어 그림.
                기본값 None.

        pid: 투수 ID; 데이터프레임에서 PitcherId 값이 해당 ID와 같은 것만 골라내어 그림.
             기본값 None

        futures: 퓨처스 포함 여부; True면 포함, False면 비포함.
                 데이터프레임의 Level 값이 'KBO'면 1군, 'KBO Minors'면 퓨처스, 'Exhibition'이면 시범.
                 기본값 False(1군+시범)

        ax: matplotlib.axes.Axes 객체. 있으면 해당 ax에 그리고, 아니면 새로운 figure 생성 후 리턴.
            기본값 None

        freq_th: 최소 구사율. 데이터프레임에서 TaggedPitchType의 비중이 해당 값 이상인 구종만 그림.
                 기본값 0.05(5%)

        # HITS 구현 X
        instant: True면 미리 지정된 전역변수 instant_year('올해' 값을 지정함. ex: 2025) 기준으로,
                 '올해'에 해당하는 데이터만 그림.
                 기본값 False

        eng: True면 영어로, False면 한글로 그림. cm/inch 변환도 함.
             기본값 False

        # HITS 구현 X
        show_batter_img: True면 타자 이미지 그림을 그리고 False면 안 그림.
                         기본값 False

        draw_dots: True면 개별 투구를 scatter chart로 뿌리고, False면 범위를 그림.
                   기본값 False

        sample_dots: True면 100구만 선별, False면 전체 투구를 그림.
                     기본값 False

        draw_usage: True면 범위를 그릴 때, 구사율에 비례해서 크기를 조정.
                    False면 실제 무브먼트 범위를 토대로 범위를 그림.
                    draw_dots가 True인 경우 작동하지 않음.
                    기본값 False

        draw_lg_avg: True면 리그 평균을 그리고, False면 그리지 않음.
                     avg_values가 없으면 df에 리그 전체 범위가 있다고 가정하고 그림.
                     기본값 False

        lg_avg_df: 리그 평균값을 정리한 avg.
                   없으면 df에 리그 전체 범위가 있다고 가정하고 계산.
                   year, pitch_type, pthrows, speed_mean, spin_mean,
                   hb_median, hb_std, ivb_median, ivb_std,
                   ext_median, ext_std, relh_mean, relh_std
                   기본값 None

        show_PTS: True면 PTS 무브먼트를 보여줌 (트랙맨이 없을 때만)

    Returns:
        a: 플롯이 그려진 matplotlib.axes.Axes 객체
    """
    # matplotlib.axes.Axes 객체 주어졌는지 확인
    if ax is None:
        f, a = plt.subplots(figsize=(5, 5), dpi=100)
    else:
        a = ax

    # 폰트 설정; HITS 구현 X
    set_fonts()
    dpi = 100

    # 선수명, player
    if player is not None:
        target = df[df.Pitcher == player]
    else:
        target = df

    # 선수ID, pid
    if pid is not None:
        target = target[target.PitcherId == pid]

    # 퓨처스 포함 여부
    if futures == False:
        target = target.loc[target.Level.isin(['KBO', 'Exhibition'])]

    # '올해'만 그릴지
    if instant == True:
        target = target[target.year == instant_year]

    # 필터링한 데이터 0 -> Return
    if target.shape[0] == 0:
        return

    # 무브먼트를 그릴 것이기 때문에
    # 필요한 Feature (구속, 무브먼트, 구종) 없는 데이터는 걸러낸다.
    if show_PTS is True:
        if 'InducedVertBreakGameDay' in target.columns:
            # 코드 작성 편의성을 위해 GameDay 컬럼 -> 전부 떼고 수정
            target = target.assign(RelSpeed = np.where(target.RelSpeed.notnull(),
                                                       target.RelSpeed,
                                                       target.RelSpeedGameDay),
                                   HorzBreak = np.where(target.HorzBreak.notnull(),
                                                        target.HorzBreak,
                                                        target.HorzBreakGameDay),
                                   InducedVertBreak = np.where(target.InducedVertBreak.notnull(),
                                                               target.InducedVertBreak,
                                                               target.InducedVertBreakGameDay),
                                   PlateLocSide = np.where(target.PlateLocSide.notnull(),
                                                           target.PlateLocSide,
                                                           target.PlateLocSideGameDay),
                                   PlateLocHeight = np.where(target.PlateLocHeight.notnull(),
                                                             target.PlateLocHeight,
                                                             target.PlateLocHeightGameDay),)
    target = target[target.RelSpeed != 0]
    target = target[target.RelSpeed.notnull() & target.HorzBreak.notnull() & target.TaggedPitchType.notnull()]

    # 구종 별 구사율 구하기
    index_order = [x for x in sort_order if x in target.TaggedPitchType.unique()]
    total = target.groupby('TaggedPitchType').size()[index_order] / len(target)

    # 구사율이 정해진 기준 이하인 경우 그리지 않는다.
    index_order = [x for x in index_order if total[x] >= freq_th]

    ##### 100구 샘플 추출
    ratio = target.groupby('TaggedPitchType').size() / len(target)
    fs = filter_and_sample(target, 100, ratio)

    # KBO 평균 구하기
    # 같은 손방향 투수들의 구종별 평균 무브먼트를 구한다.
    # 현재 선택된 투수의 손방향을 추출/저장
    psidecol = 'PitcherThrows' if 'PitcherThrows' in df.columns else 'PitcherThrows'
    if 'PitcherThrows' in df.columns:
        pitcher_side = target.PitcherThrows.unique()[0]
    else:
        pitcher_side = target.PitcherThrows.unique()[0]

    
    if lg_avg_df is None:
        # 리그 평균 데이터 DF가 주어지지 않은 경우.
        pitch_kbo = df[(df[psidecol] == pitcher_side)]
        if futures == False:
            pitch_kbo = pitch_kbo[pitch_kbo.Level.isin(['KBO', 'Exhibition'])]
    else:
        # 리그 평균 데이터 DF가 주어진 경우.
        # 데이터프레임 column (괄호안: 설명):
        # year(연도), pitch_type(구종), pthrows(던지는손),
        # speed_mean, speed_median, (구속 평균/중간값. 단위 cm)
        # spin_mean, spin_median, (회전수 평균/중간값. 단위 cm)
        # hb_mean, hb_median, hb_std, (좌우무브 평균/중간값/표준편차. 단위 cm)
        # ivb_mean, ivb_median, ivb_std, (수직무브 평균/중간값/표준편차. 단위 cm)
        # ext_mean, ext_median, ext_std, (익스텐션 평균/중간값/표준편차. 단위 m)
        # relh_mean, relh_median, relh_std, (릴리즈높이 평균/중간값/표준편차. 단위 m)
        # ratio (구종의 구사율; 연도, 던지는손 같은 그룹 안에서. 값 범위는 0-1)
        years = df.year.unique()
        year = max(years)
        pitch_kbo = lg_avg_df[(lg_avg_df.pthrows == pitcher_side) & (lg_avg_df.year == year)]

    # maxfreq: 대상 투수 구종 구사율 중 최대치
    maxfreq = target.groupby('TaggedPitchType').size().max() / len(target)
    dots_by_type = []
    labels = []

    # 구종 별로 차트를 그림
    for p in index_order:
        t = target[target.TaggedPitchType == p]
        freq = len(t) / len(target)
        # 위에서도 한번 걸렀지만, 여기서 구사율 최소값 체크를 한번 더 함
        if freq < freq_th:
            continue

        alpha2 = min(1, freq*2+.25)
        s = len(t)
        if len(t) == 0:
            continue

        color = ball_colors[p]
        width = t.HorzBreak.std()*2 + 10
        height = t.HorzBreak.std()*2 + 10
        c1, c2 = t.HorzBreak.median(), t.InducedVertBreak.median()

        if draw_dots == False:
            # 타원 그리기; 구종 무브먼트 범위로 타원을 그림
            if eng == True:
                # 영어 버전인 경우, inch 단위로 환산
                width /= 2.54
                height /= 2.54
                c1 /= 2.54
                c2 /= 2.54
            if draw_usage == False:
                # 무브먼트 범위에 따라서 타원 크기를 결정
                # ellipse1은 원 내부, ellipse2는 바깥의 선
                ellipse1 = Ellipse((c1, c2), width, height,
                                   ec=color, fc=color, lw=2,
                                   alpha=.45, zorder=2)
                ellipse2 = Ellipse((c1, c2), width, height,
                                   ec=darken_color(color), fc='none', lw=2,
                                   alpha=.15, zorder=1)
            else:
                # 구사율에 비례해서 타원 크기를 결정
                # ellipse1은 원 내부, ellipse2는 바깥의 선
                ellipse1 = Ellipse((c1, c2), dpi*freq/4+15, dpi*freq/4+15,
                                   ec=color, fc=color, lw=2,
                                   alpha=.45, zorder=2)
                ellipse2 = Ellipse((c1, c2), dpi*freq/4+15, dpi*freq/4+15,
                                   ec=darken_color(color), fc='none', lw=2,
                                   alpha=.15, zorder=1)
            a.add_patch(ellipse1)
            a.add_patch(ellipse2)

            # 타원 가운데는 점 찍기
            a.scatter(c1, c2, alpha=alpha2, s=dpi*.5, zorder=2, c=color)
        else:
            # Scatter Chart로 그리기; 공 개별로 표시
            if sample_dots is True:
                # 100구 샘플만 그리기 선택한 경우
                t = fs[fs.TaggedPitchType == p]
                if eng == False:
                    a.scatter(t.HorzBreak, t.InducedVertBreak, s=dpi, zorder=2, c=color, alpha=.45)
                    a.scatter(t.HorzBreak, t.InducedVertBreak, s=dpi, zorder=0,
                              c='none', alpha=.65, ec=darken_color(color), linewidths=1)
                else:
                    # 영어 버전인 경우, inch 단위로 환산
                    a.scatter(t.HorzBreak / 2.54, t.InducedVertBreak / 2.54, s=dpi*.75, zorder=1, c=color, alpha=.45)
                    a.scatter(t.HorzBreak / 2.54, t.InducedVertBreak / 2.54, s=dpi*.75, zorder=0,
                              c='none', alpha=.65, ec=color, linewidths=1)
            else:
                # 모든 공을 그리기
                if eng == False:
                    a.scatter(t.HorzBreak, t.InducedVertBreak, s=dpi, zorder=2, c=color, alpha=.45)
                    a.scatter(t.HorzBreak, t.InducedVertBreak, s=dpi, zorder=0,
                              c='none', alpha=.65, ec=darken_color(color), linewidths=1)
                else:
                    # 영어 버전인 경우, inch 단위로 환산
                    a.scatter(t.HorzBreak / 2.54, t.InducedVertBreak / 2.54, s=dpi*.75, zorder=1, c=color, alpha=.45)
                    a.scatter(t.HorzBreak / 2.54, t.InducedVertBreak / 2.54, s=dpi*.75, zorder=0,
                              c='none', alpha=.65, ec=color, linewidths=1)

        # 범례 표시 위해서 구종 별로 점 하나를 차트 범위 밖의 외곽에 하나 찍어놓음
        # 점을 찍고 범례 array에 붙여넣기
        dots_by_type.append(a.scatter(-1000, -1000,
                                       s=dpi, zorder=0, c=color))

        if draw_lg_avg is True:
            # 구종 KBO 평균 무브먼트 그리기
            # 리그 평균값 가져오기
            # 평균 무브먼트는 타원으로 그린다
            if lg_avg_df is None:
                pitch_kbo_p = pitch_kbo[(pitch_kbo.TaggedPitchType == p)]
                freq_kbo = len(pitch_kbo_p)/len(pitch_kbo)
                xbreak_kbo = pitch_kbo_p.HorzBreak.mean()
                zbreak_kbo = pitch_kbo_p.InducedVertBreak.mean()

                # 타원 폭/높이: 수평/수직 무브먼트의 표준편차를 활용해서 그림
                kbo_avg_width = pitch_kbo_p.HorzBreak.std()*2 + 5
                kbo_avg_height = pitch_kbo_p.InducedVertBreak.std()*2 + 5
                if eng is True:
                    # 영어 버전인 경우, inch 단위로 환산
                    xbreak_kbo, zbreak_kbo = xbreak_kbo / 2.54, zbreak_kbo / 2.54
                    kbo_avg_width = pitch_kbo_p.HorzBreak.div(2.54).std()*2 + 2
                    kbo_avg_height = pitch_kbo_p.InducedVertBreak.div(2.54).std()*2 + 2
            else:
                pitch_kbo_p = pitch_kbo[(pitch_kbo.pitch_type == p)]
                freq_kbo = pitch_kbo_p.ratio.values[0]
                xbreak_kbo = pitch_kbo_p.hb_mean.values[0]
                zbreak_kbo = pitch_kbo_p.ivb_mean.values[0]

                # 타원 폭/높이: 수평/수직 무브먼트의 표준편차를 활용해서 그림
                kbo_avg_width = pitch_kbo_p.hb_std.values[0]*2 + 5
                kbo_avg_height = pitch_kbo_p.ivb_std.values[0]*2 + 5
                if eng is True:
                    # 영어 버전인 경우, inch 단위로 환산
                    xbreak_kbo, zbreak_kbo = xbreak_kbo / 2.54, zbreak_kbo / 2.54
                    kbo_avg_width = pitch_kbo_p.hb_std.values[0] / 2.54 * 2 + 2
                    kbo_avg_height = pitch_kbo_p.ivb_std.values[0] / 2.54 * 2 + 2

            with mpl.rc_context({'hatch.linewidth': 2.0}):
                # 타원 안쪽은 hatch (빗금)으로 색칠함
                if draw_usage:
                    # 구사율 비례해서 그리는 경우
                    # 평균 무브먼트도 구사율 비례해서 그림
                    ellipse3 = Ellipse((xbreak_kbo, zbreak_kbo),
                                       dpi*freq_kbo/4+15, dpi*freq_kbo/4+15,
                                       ec=color, fc='none', lw=0, hatch='/////',
                                       alpha=0.85, zorder=0)
                else:
                    ellipse3 = Ellipse((xbreak_kbo, zbreak_kbo),
                                       kbo_avg_width, kbo_avg_height,
                                       ec=color, fc='none', lw=0, hatch='/////',
                                       alpha=0.85, zorder=0)
                # 타원 patch 추가
                a.add_patch(ellipse3)
        if eng == True:
            labels.append(p)
        else:
            labels.append(p_kor_dict[p])

    # 구종별 KBO 평균 라벨
    if draw_lg_avg == True:
        dots_by_type.append(a.scatter(-1000, -1000, ec='k', fc='none', lw=0, hatch='///',
                                       s=dpi*2, zorder=0, marker='s'))
        if eng == True:
            labels.append('KBO AVG.')
        else:
            labels.append('리그평균')

    # Tick 자막 표시 / 영점 및 0 line 표시
    if eng == True:
        a.text(-27, -60 / 2.54, '◀Drop', rotation=90, weight='bold', zorder=1)
        a.text(-27, 54 / 2.54, 'Rise▶', rotation=90, weight='bold', zorder=1)
        a.text(-26, -26, '◀LHH', weight='bold', zorder=4)
        a.text(21, -26, 'RHH▶', weight='bold', zorder=4)
        a.set_xlim(-70 / 2.54, 70 / 2.54)
        a.set_ylim(-70 / 2.54, 70 / 2.54)
        a.hlines(0, -100 / 2.54, 100 / 2.54, color='k', ls='--', lw=1.5, zorder=0)
        a.vlines(0, -100 / 2.54, 100 / 2.54, color='k', ls='--', lw=1.5, zorder=0)
    else:
        a.text(-68, -60, '◀가라앉음', rotation=90, weight='bold', zorder=1)
        a.text(-68, 44, '떠오름▶', rotation=90, weight='bold', zorder=1)
        a.text(-67, -68, '◀좌타석', weight='bold', zorder=4)
        a.text(40, -68, '우타석▶', weight='bold', zorder=4)
        a.set_xlim(-70, 70)
        a.set_ylim(-70, 70)
        a.set_xticks(list(range(-80, 80, 20))[1:])
        a.set_yticks(list(range(-80, 80, 20))[1:])
        a.hlines(0, -100, 100, color='k', ls='--', lw=1.5, zorder=0)
        a.vlines(0, -100, 100, color='k', ls='--', lw=1.5, zorder=0)

    if show_batter_img:
        # 타자 이미지 그리기
        try:
            RHB_img = mpimg.imread('../images/RHB_image_colordot.png')
            LHB_img = mpimg.imread('../images/LHB_image_colordot.png')
        except:
            RHB_img = mpimg.imread('images/RHB_image_colordot.png')
            LHB_img = mpimg.imread('images/LHB_image_colordot.png')
        RHB_imagebox = OffsetImage(RHB_img, zoom=.25, alpha=.55)

        if eng == True:
            RHB_ab = AnnotationBbox(RHB_imagebox, (54 / 2.54, 0), frameon=False)
        else:
            RHB_ab = AnnotationBbox(RHB_imagebox, (54, 0), frameon=False)
        RHB_artist = a.add_artist(RHB_ab)
        RHB_artist.set_zorder(3)

        LHB_imagebox = OffsetImage(LHB_img, zoom=.25, alpha=.55)
        if eng == True:
            LHB_ab = AnnotationBbox(LHB_imagebox, (-54 / 2.54, 0), frameon=False)
        else:
            LHB_ab = AnnotationBbox(LHB_imagebox, (-54, 0), frameon=False)
        LHB_artist = a.add_artist(LHB_ab)
        LHB_artist.set_zorder(3)

    # Legend 표시 - 오프셋 설정
    bbox_anchor_y = -0.35
    if len(labels) <= 5:
        bbox_anchor_y = -0.29 if eng == True else -0.28
    else:
        bbox_anchor_y = -0.33 if eng == True else -0.32

    # Legend 표시
    a.legend(tuple(dots_by_type), tuple(labels), ncol=3,
             loc='lower center', fontsize='medium',
             bbox_to_anchor =(0.5, bbox_anchor_y))
    return a



def darken_color(hex_color, factor=0.7):
    """
    주어진 색상을 더 진하게 변환.

    Parameters:
        hex_color (str): 색상 코드 (예: '#00aa00').
        factor (float): 진하게 만들 강도 (0~1, 작을수록 더 진해짐).

    Returns:
        str: 진하게 변환된 색상의 HEX 코드.
    """
    # HEX 색상을 RGB로 변환 (0~1 범위)
    rgb = mcolors.hex2color(hex_color)

    # RGB 값을 factor에 따라 줄이기
    darkened_rgb = tuple(max(0, c * factor) for c in rgb)

    # RGB 값을 HEX로 변환
    return mcolors.to_hex(darkened_rgb)


def filter_and_sample(data, total_samples, ratio):
    """
    주어진 데이터에서 조건에 맞는 샘플을 추출.

    Parameters:
        data (DataFrame): 데이터셋
        total_samples (int): 총 샘플 개수
        ratio (list): A, B, C, D 비율

    Returns:
        DataFrame: 샘플링된 데이터
    """
    sampled_data = []
    type_counts = {t: int(total_samples * r / sum(ratio)) for t, r in zip(sorted(data['TaggedPitchType'].unique()), ratio)}

    for t, count in type_counts.items():
        # 특정 타입의 데이터 필터링
        type_data = data[data['TaggedPitchType'] == t]

        # 아웃라이어 제거 (3-sigma 기준)
        x_mean, x_std = type_data['HorzBreak'].mean(), type_data['HorzBreak'].std()
        y_mean, y_std = type_data['InducedVertBreak'].mean(), type_data['InducedVertBreak'].std()
        filtered_data = type_data[
            (type_data['HorzBreak'] >= x_mean - 2 * x_std) &
            (type_data['HorzBreak'] <= x_mean + 2 * x_std) &
            (type_data['InducedVertBreak'] >= y_mean - 2 * y_std) &
            (type_data['InducedVertBreak'] <= y_mean + 2 * y_std)
        ]
        count = len(filtered_data) if count > len(filtered_data) else count

        # 샘플링 (비율 유지)
        sampled_data.append(filtered_data.sample(count, random_state=42))

    # 결과 합치기
    return pd.concat(sampled_data).reset_index(drop=True)


def draw_zone_line(ax, color='black', double=False):
    if double == True:
        ax.plot( [ll, ll], [bl, tl], color=color, linestyle='solid', lw=1 )
        ax.plot( [rl, rl], [bl, tl], color=color, linestyle='solid', lw=1 )
        ax.plot( [ll+(rl-ll)/3, ll+(rl-ll)/3], [bl, tl], color=color, linestyle= '--', lw=.5 )
        ax.plot( [ll+(rl-ll)*2/3, ll+(rl-ll)*2/3], [bl, tl], color=color, linestyle= '--', lw=.5 )

        ax.plot( [ll, rl], [bl, bl], color=color, linestyle='solid', lw=1 )
        ax.plot( [ll, rl], [tl, tl], color=color, linestyle='solid', lw=1 )
        ax.plot( [ll, rl], [bl+(tl-bl)/3, bl+(tl-bl)/3], color=color, linestyle= '--', lw=.5 )
        ax.plot( [ll, rl], [bl+(tl-bl)*2/3, bl+(tl-bl)*2/3], color=color, linestyle= '--', lw=.5 )

        ax.plot( [oll, oll], [obl, otl], color=color, linestyle='solid', lw=1 )
        ax.plot( [orl, orl], [obl, otl], color=color, linestyle='solid', lw=1 )

        ax.plot( [oll, orl], [obl, obl], color=color, linestyle='solid', lw=1 )
        ax.plot( [oll, orl], [otl, otl], color=color, linestyle='solid', lw=1 )
    else:
        ax.plot( [oll, oll], [obl, otl], color=color, linestyle='solid', lw=1 )
        ax.plot( [orl, orl], [obl, otl], color=color, linestyle='solid', lw=1 )
        ax.plot( [oll+(orl-oll)/3, oll+(orl-oll)/3], [obl, otl], color=color, linestyle= '--', lw=.5 )
        ax.plot( [oll+(orl-oll)*2/3, oll+(orl-oll)*2/3], [obl, otl], color=color, linestyle= '--', lw=.5 )

        ax.plot( [oll, orl], [obl, obl], color=color, linestyle='solid', lw=1 )
        ax.plot( [oll, orl], [otl, otl], color=color, linestyle='solid', lw=1 )
        ax.plot( [oll, orl], [obl+(otl-obl)/3, obl+(otl-obl)/3], color=color, linestyle= '--', lw=.5 )
        ax.plot( [oll, orl], [obl+(otl-obl)*2/3, obl+(otl-obl)*2/3], color=color, linestyle= '--', lw=.5 )


def vaa_plot(df,
             player=None,
             pid=None,
             futures=False,
             ax=None,
             freq_th=0.05,
             eng=False,
             draw_dots=False,
             draw_lg_avg=False,
             lg_avg_df=None,
             loc=None):
    """
    VAA 플롯을 그린다.

    Parameters:
        df: 트랙맨 데이터가 포함된 pandas dataframe.

        player: 투수 이름; 데이터프레임에서 Pitcher 값이 해당 이름과 같은 것만 골라내어 그림.
                기본값 None.

        pid: 투수 ID; 데이터프레임에서 PitcherId 값이 해당 ID와 같은 것만 골라내어 그림.
             기본값 None

        futures: 퓨처스 포함 여부; True면 포함, False면 비포함.
                 데이터프레임의 Level 값이 'KBO'면 1군, 'KBO Minors'면 퓨처스, 'Exhibition'이면 시범.
                 기본값 False(1군+시범)

        ax: matplotlib.axes.Axes 객체. 있으면 해당 ax에 그리고, 아니면 새로운 figure 생성 후 리턴.
            기본값 None

        freq_th: 최소 구사율. 데이터프레임에서 TaggedPitchType의 비중이 해당 값 이상인 구종만 그림.
                 기본값 0.05(5%)

        # HITS 구현 X
        draw_dots: True면 개별 투구를 scatter chart로 뿌리고, False면 범위를 그림.
                   기본값 False

        draw_lg_avg: True면 리그 평균을 그리고, False면 그리지 않음.
                     avg_values가 없으면 df에 리그 전체 범위가 있다고 가정하고 그림.
                     기본값 False

        lg_avg_df: 리그 평균값을 정리한 avg.
                   없으면 df에 리그 전체 범위가 있다고 가정하고 계산.
                   year, pitch_type, pthrows, speed_mean, spin_mean,
                   hb_median, hb_std, vaa_mean, vaa_std,
                   ext_median, ext_std, relh_mean, relh_std,
                   vaa_top_mean, vaa_top_std, vaa_mid_mean, vaa_mid_std,
                   vaa_bot_mean, vaa_bot_std
                   기본값 None

        loc: 로케이션 옵션, 기본 None
             None: 전체
             'top': 상단
             'mid': 중단
             'bot': 하단

    Returns:
        a: 플롯이 그려진 matplotlib.axes.Axes 객체
    """

    # matplotlib.axes.Axes 객체 주어졌는지 확인
    if ax is None:
        f, a = plt.subplots(figsize=(5, 5), dpi=100)
    else:
        a = ax

    # 폰트 설정; HITS 구현 X
    set_fonts()
    dpi = 100

    # 선수명, player
    if player is not None:
        target = df[df.Pitcher == player]
    else:
        target = df

    # 선수ID, pid
    if pid is not None:
        target = target[target.PitcherId == pid]

    # 퓨처스 포함 여부
    if futures == False:
        target = target.loc[target.Level.isin(['KBO', 'Exhibition'])]

    # 필터링한 데이터 0 -> Return
    if target.shape[0] == 0:
        return

    # 무브먼트를 그릴 것이기 때문에
    # 필요한 Feature (구속, 무브먼트, 구종) 없는 데이터는 걸러낸다.
    target = target[target.RelSpeed != 0]
    target = target[target.RelSpeed.notnull() & target.VertApprAngle.notnull() & target.TaggedPitchType.notnull()]

    # 구종 별 구사율 구하기
    index_order = [x for x in sort_order if x in target.TaggedPitchType.unique()]
    total = target.groupby('TaggedPitchType').size()[index_order] / len(target)

    # 구사율이 정해진 기준 이하인 경우 그리지 않는다.
    index_order = [x for x in index_order if total[x] >= freq_th]

    ##### 100구 샘플 추출
    ratio = target.groupby('TaggedPitchType').size() / len(target)
    fs = filter_and_sample(target, 100, ratio)

    # KBO 평균 구하기
    # 같은 손방향 투수들의 구종별 평균 무브먼트를 구한다.
    # 현재 선택된 투수의 손방향을 추출/저장
    psidecol = 'PitcherThrows' if 'PitcherThrows' in df.columns else 'PitcherThrows'
    if 'PitcherThrows' in df.columns:
        pitcher_side = target.PitcherThrows.unique()[0]
    else:
        pitcher_side = target.PitcherThrows.unique()[0]

    
    if lg_avg_df is None:
        # 리그 평균 데이터 DF가 주어지지 않은 경우.
        pitch_kbo = df[(df[psidecol] == pitcher_side)]
        if futures == False:
            pitch_kbo = pitch_kbo[pitch_kbo.Level.isin(['KBO', 'Exhibition'])]
    else:
        # 리그 평균 데이터 DF가 주어진 경우.
        # 데이터프레임 column (괄호안: 설명):
        # year(연도), pitch_type(구종), pthrows(던지는손),
        # speed_mean, speed_median, (구속 평균/중간값. 단위 cm)
        # spin_mean, spin_median, (회전수 평균/중간값. 단위 cm)
        # hb_mean, hb_median, hb_std, (좌우무브 평균/중간값/표준편차. 단위 cm)
        # ivb_mean, ivb_median, ivb_std, (수직무브 평균/중간값/표준편차. 단위 cm)
        # ext_mean, ext_median, ext_std, (익스텐션 평균/중간값/표준편차. 단위 m)
        # relh_mean, relh_median, relh_std, (릴리즈높이 평균/중간값/표준편차. 단위 m)
        # ratio (구종의 구사율; 연도, 던지는손 같은 그룹 안에서. 값 범위는 0-1)
        years = df.year.unique()
        year = max(years)
        pitch_kbo = lg_avg_df[(lg_avg_df.pthrows == pitcher_side) & (lg_avg_df.year == year)]

    # maxfreq: 대상 투수 구종 구사율 중 최대치
    maxfreq = target.groupby('TaggedPitchType').size().max() / len(target)
    dots_by_type = []
    labels = []

    # 구종 별로 차트를 그림
    for p in index_order:
        t = target[target.TaggedPitchType == p]
        freq = len(t) / len(target)
        # 위에서도 한번 걸렀지만, 여기서 구사율 최소값 체크를 한번 더 함
        if freq < freq_th:
            continue

        alpha2 = min(1, freq*2+.25)
        s = len(t)
        if len(t) == 0:
            continue

        color = ball_colors[p]
        width = t.HorzApprAngle.std()*2 + 0.5
        height = t.HorzApprAngle.std()*2 + 0.5
        c1, c2 = t.HorzApprAngle.median(), t.VertApprAngle.median()

        if draw_dots == False:
            # 타원 그리기; 구종 무브먼트 범위로 타원을 그림
            # VAA 범위에 따라서 타원 크기를 결정
            # ellipse1은 원 내부, ellipse2는 바깥의 선
            ellipse1 = Ellipse((c1, c2), width, height,
                               ec=color, fc=color, lw=2,
                               alpha=.45, zorder=2)
            ellipse2 = Ellipse((c1, c2), width, height,
                               ec=darken_color(color), fc='none', lw=2,
                               alpha=.15, zorder=1)
            a.add_patch(ellipse1)
            a.add_patch(ellipse2)

            # 타원 가운데는 점 찍기
            a.scatter(c1, c2, alpha=alpha2, s=dpi*.5, zorder=2, c=color)
        else:
            # Scatter Chart로 그리기; 공 개별로 표시
            # 모든 공을 그리기
            a.scatter(t.HorzApprAngle, t.VertApprAngle, s=dpi, zorder=2, c=color, alpha=.45)
            a.scatter(t.HorzApprAngle, t.VertApprAngle, s=dpi, zorder=0,
                      c='none', alpha=.65, ec=darken_color(color), linewidths=1)

        # 범례 표시 위해서 구종 별로 점 하나를 차트 범위 밖의 외곽에 하나 찍어놓음
        # 점을 찍고 범례 array에 붙여넣기
        dots_by_type.append(a.scatter(-1000, -1000,
                                       s=dpi, zorder=0, c=color))

        if draw_lg_avg is True:
            # 구종 KBO 평균 무브먼트 그리기
            # 리그 평균값 가져오기
            # 평균 무브먼트는 타원으로 그린다
            if lg_avg_df is None:
                pitch_kbo_p = pitch_kbo[(pitch_kbo.TaggedPitchType == p)]
                freq_kbo = len(pitch_kbo_p)/len(pitch_kbo)
                x_kbo = pitch_kbo_p.HorzApprAngle.mean()
                z_kbo = pitch_kbo_p.VertApprAngle.mean()

                # 타원 폭/높이: 수평/수직 무브먼트의 표준편차를 활용해서 그림
                kbo_avg_width = pitch_kbo_p.HorzApprAngle.std()*2 + 0.5
                kbo_avg_height = pitch_kbo_p.VertApprAngle.std()*2 + 0.5
            else:
                pitch_kbo_p = pitch_kbo[(pitch_kbo.pitch_type == p)]
                freq_kbo = pitch_kbo_p.ratio.values[0]

                x_kbo = pitch_kbo_p.haa_mean.values[0]
                if loc is None:
                    z_kbo = pitch_kbo_p.vaa_mean.values[0]
                elif loc == 'top':
                    z_kbo = pitch_kbo_p.vaa_mean.values[0]
                elif loc == 'mid':
                    z_kbo = pitch_kbo_p.vaa_mid_mean.values[0]
                elif loc == 'bot':
                    z_kbo = pitch_kbo_p.vaa_bot_mean.values[0]

                # 타원 폭/높이: 수평/수직 무브먼트의 표준편차를 활용해서 그림
                kbo_avg_width = pitch_kbo_p.haa_std.values[0]*2 + 0.5
                kbo_avg_height = pitch_kbo_p.vaa_std.values[0]*2 + 0.5

            with mpl.rc_context({'hatch.linewidth': 2.0}):
                # 타원 안쪽은 hatch (빗금)으로 색칠함
                ellipse3 = Ellipse((x_kbo, z_kbo),
                                   kbo_avg_width, kbo_avg_height,
                                   ec=color, fc='none', lw=0, hatch='/////',
                                   alpha=0.85, zorder=0)
                # 타원 patch 추가
                a.add_patch(ellipse3)
        labels.append(p_kor_dict[p])

    # 구종별 KBO 평균 라벨
    if draw_lg_avg == True:
        dots_by_type.append(a.scatter(-1000, -1000, ec='k', fc='none', lw=0, hatch='///',
                                       s=dpi*2, zorder=0, marker='s'))
        labels.append('리그평균')

    # Tick 자막 표시 / 영점 및 0 line 표시

    a.text(-5, -12, '◀Steep', rotation=90, weight='bold', zorder=1)
    a.text(-5, -3.5, 'Flat▶', rotation=90, weight='bold', zorder=1)
    a.text(-4.5, -12.5, '◀좌타자', weight='bold', zorder=4)
    a.text(3.5, -12.5, '우타자▶', weight='bold', zorder=4)
    a.set_xlim(-5, 5)
    a.set_ylim(-12.5, -2.5)
    a.set_xticks(list(np.arange(-7.5, 7.5, 2.5))[1:])
    a.set_yticks(list(np.arange(-12.5, 0, 2.5))[1:])
    a.hlines(0, -100, 100, color='k', ls='--', lw=1.5, zorder=0)
    a.vlines(0, -100, 100, color='k', ls='--', lw=1.5, zorder=0)

    # Legend 표시 - 오프셋 설정
    bbox_anchor_y = -0.35
    if len(labels) <= 5:
        bbox_anchor_y = -0.29 if eng == True else -0.28
    else:
        bbox_anchor_y = -0.33 if eng == True else -0.32

    # Legend 표시
    a.legend(tuple(dots_by_type), tuple(labels), ncol=3,
             loc='lower center', fontsize='medium',
             bbox_to_anchor =(0.5, bbox_anchor_y))
    return a


def 로케이션그리기(df,
                   좌우: str='우',
                   분포표시: bool=False,
                   마커쓰기: bool=False,
                   ax=None,
                   dpi=100,
                   PTS로_그림=False):
    if ax is None:
        fig, ax = plt.subplots(figsize=(3, 3), dpi=dpi)
    else:
        fig = ax.get_figure()

    마커사이즈 = 125/100*dpi
    마커_가로줄사이즈 = 300/100*dpi
    마커_세로줄사이즈 = 50/100*dpi
    세로줄_중심부오프셋 = 0.05 / dpi * 100
    홈플레이트_사이즈_비율 = 0.195/100*dpi
    
    ax.plot( [-0.2359, -0.2359], [0.45, 1.05], color='k', linestyle='solid', lw=1 )
    ax.plot( [0.2359, 0.2359], [0.45, 1.05], color='k', linestyle='solid', lw=1 )
    ax.plot( [-0.2359+(0.2359+0.2359)/3, -0.2359+(0.2359+0.2359)/3], [0.45, 1.05], color='k', linestyle= '--', lw=.5 )
    ax.plot( [-0.2359+(0.2359+0.2359)*2/3, -0.2359+(0.2359+0.2359)*2/3], [0.45, 1.05], color='k', linestyle= '--', lw=.5 )

    ax.plot( [-0.2359, 0.2359], [0.45, 0.45], color='k', linestyle='solid', lw=1 )
    ax.plot( [-0.2359, 0.2359], [1.05, 1.05], color='k', linestyle='solid', lw=1 )
    ax.plot( [-0.2359, 0.2359], [0.65, 0.65], color='k', linestyle= '--', lw=.5 )
    ax.plot( [-0.2359, 0.2359], [0.85, 0.85], color='k', linestyle= '--', lw=.5 )

    hp_img = mpimg.imread('images/hp_reverse_transparent.png')
    hp_imagebox1 = OffsetImage(hp_img, zoom=홈플레이트_사이즈_비율, alpha=1)
    hp_ab1 = AnnotationBbox(hp_imagebox1, (0, 0.225), frameon=False)
    hp_artist1 = ax.add_artist(hp_ab1)
    hp_artist1.set_zorder(-3)

    투수좌우 = df.PitcherThrows.unique()[0]
    if 좌우 and 좌우 == '우':
        대상 = df[df.BatterSide == 'Right']
    elif 좌우 and 좌우 == '좌':
        대상 = df[df.BatterSide == 'Left']
    else:
        대상 = df

    대상구종들 = 대상.TaggedPitchType.unique()
    구종별_라벨 = []
    라벨 = []

    유형 = '타원' if 분포표시 is True else '점'
    for 구종 in pitchtype_sortlist:
        if 구종 in ('Other', 'Undefined', 'Knuckleball'):
            continue
        색상 = ball_colors[구종]
        if 마커쓰기 is False:
            마커 = 'o'
        elif 구종 in ('Slider', 'Cutter'):
            마커_좌우 = 'R' if 투수좌우 in ('Right', 'Side') else 'L'
            마커 = 구종별_마커[f'{구종}-{마커_좌우}']
        else:
            마커 = 구종별_마커[구종]

        if 구종 in 대상구종들:
            타겟 = 대상[대상.TaggedPitchType == 구종]
            if PTS로_그림 is False:
                유효타겟 = 타겟[타겟.PlateLocSide.notnull() & 타겟.PlateLocHeight.notnull()]
            else:
                유효타겟 = 타겟.assign(PlateLocSide = np.where(타겟.PlateLocSide.notnull(),
                                                               타겟.PlateLocSide,
                                                               타겟.PlateLocSideGameDay),
                                       PlateLocHeight = np.where(타겟.PlateLocHeight.notnull(),
                                                                 타겟.PlateLocHeight,
                                                                 타겟.PlateLocHeightGameDay))
            구종별_라벨.append(ax.scatter(-1000, -1000,
                                          s=100, zorder=0, c=색상))
            라벨.append(구종영문_한글로변환[구종])

            if 유형 == '타원' and len(타겟) > 3:
                try:
                    # 표준편차 배수
                    표준편차배수 = 1
                    width = 유효타겟.PlateLocSide.std() * 표준편차배수
                    height = 유효타겟.PlateLocHeight.std() * 표준편차배수
                    c1, c2 = 유효타겟.PlateLocSide.mean(), 유효타겟.PlateLocHeight.mean()

                    def chatgpt_타원():
                        ### chatgpt
                        # PlateLocSide, PlateLocHeight 값 배열화
                        X = np.column_stack((유효타겟.PlateLocSide.values, 유효타겟.PlateLocHeight.values))

                        # PCA로 주성분 분석
                        pca = PCA(n_components=2)
                        pca.fit(X)
                        c1, c2 = X[:,0].mean(), X[:,1].mean()
                        # 회전각도 계산 (라디안을 도(degree)로 변환)
                        angle = np.degrees(np.arctan2(pca.components_[0, 1], pca.components_[0, 0]))

                        표준편차배수 = 1  # 표준편차와 비슷한 크기
                        width = 표준편차배수 * np.sqrt(pca.explained_variance_[0]) * 2  # 긴 축
                        height = 표준편차배수 * np.sqrt(pca.explained_variance_[1]) * 2  # 짧은 축

                        # 타원1 (내부 채움)
                        타원1 = Ellipse((c1, c2), width, height,
                                       angle=angle,
                                       ec=색상, fc=색상, lw=2,
                                       alpha=.25, zorder=-2)

                        # 타원2 (외곽선)
                        타원2 = Ellipse((c1, c2), width, height,
                                       angle=angle,
                                       ec=darken_color(색상), fc='none', lw=2,
                                       alpha=.15, zorder=-2)
                        return 타원1, 타원2

                    타원1, 타원2 = chatgpt_타원()
                    ax.add_patch(타원1)
                    ax.add_patch(타원2)
                    
                    ax.scatter(c1, c2,
                               label=구종,
                               color=색상,
                               edgecolors='black',
                               s=마커사이즈, alpha=0.75, marker='o', zorder=2)

                except Exception as e:
                    print(e)
                    ax.scatter(유효타겟.PlateLocSide,
                               유효타겟.PlateLocHeight,
                               label=구종,
                               color=색상,
                               edgecolors='black',
                               s=마커사이즈, alpha=0.5, marker=마커, zorder=2)
                    if 구종 == 'Cutter':
                        ax.scatter(유효타겟.PlateLocSide,
                                   유효타겟.PlateLocHeight,
                                   label=구종,
                                   color=색상,
                                   edgecolors='black',
                                   s=마커_가로줄사이즈, alpha=0.5, marker='_', zorder=2)
                    elif 구종 == 'Sweeper':
                        ax.scatter(유효타겟.PlateLocSide,
                                   유효타겟.PlateLocHeight-세로줄_중심부오프셋,
                                   label=구종,
                                   color='black', linewidths=1,
                                   s=마커_세로줄사이즈, alpha=0.5, marker='|', zorder=2)
            else:
                ax.scatter(유효타겟.PlateLocSide,
                           유효타겟.PlateLocHeight,
                           label=구종,
                           color=색상,
                           edgecolors='black',
                           s=마커사이즈, alpha=0.5, marker=마커, zorder=2)
                if 구종 == 'Cutter':
                    ax.scatter(유효타겟.PlateLocSide,
                               유효타겟.PlateLocHeight,
                               label=구종,
                               color='black', linewidths=1,
                               s=마커_가로줄사이즈, alpha=0.5, marker='_', zorder=2)
                elif 구종 == 'Sweeper':
                    ax.scatter(유효타겟.PlateLocSide,
                               유효타겟.PlateLocHeight-세로줄_중심부오프셋,
                               label=구종,
                               color='black', linewidths=1,
                               s=마커_세로줄사이즈, alpha=0.5, marker='|', zorder=2)

    ax.set_xbound(-0.45, 0.45); ax.set_ybound(0.1, 1.2)
    ax.axis('off')

    return fig
