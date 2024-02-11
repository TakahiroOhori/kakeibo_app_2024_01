# ライブラリのインポート
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import seaborn as sns
import datetime

#####   準備
# データフレームの準備
#   データフレームのカラム
column_list = ["年&月", "発生日", "収入or支出", "分類", "金額", "登録日"]
#   家計簿データ(csvファイル)の読み込み
df_kakeibo = pd.read_csv("kakeibo_data.csv")
#   データ入力数の指定
all_row_num = 20


####################################################################
#####   画面タイトル
st.title("家計簿アプリ")


####################################################################
#####   データ入力画面の表示と入力データのでエータフレームへの取り込み
with st.container(border=True):
    st.markdown("### 家計簿の入力(一度に20項目まで入力可)")
    #   家計簿データ(csvファイルの読み込み/新規作成)
    new_btn = st.button("家計簿データの新規作成(既存データの消去)")
    #   新規作成がクリックされたらデータフレームを新規に作成し、家計簿データファイルを上書きする
    if new_btn:
        # データフレームの新規作成
        df_kakeibo = pd.DataFrame(columns=column_list)
        # 家計簿データ(csvファイル)の上書き(カラム名だけのファイルにする)
        df_kakeibo.to_csv("kakeibo_data.csv", index=False)

    # データの入力(データ入力ウィジェットは1行につき4カラム、all_ros_numで指定した行数作る)
    #    widget変数や入力値を格納するリストの作成
    input_widget_list = []
    for i in range(all_row_num):
        input_widget_list.append(st.columns(4))
    #   入力widgetの作成
    with st.container():
        for i in range(all_row_num):
            with input_widget_list[i][0]:
                input_widget_list[i][0] = st.date_input(f"発生日{i+1}")
            with input_widget_list[i][1]:
                input_widget_list[i][1] = st.selectbox(f"収入or支出{i+1}", ["収入", "支出"])
            with input_widget_list[i][2]:
                input_widget_list[i][2] = st.selectbox(f"分類{i+1}", 
                    ["給料", "臨時収入", "住居費", "食費", "光熱費", "通信費", "交通費", "交際費", "娯楽","雑費"])
            with input_widget_list[i][3]:
                input_widget_list[i][3] = st.number_input(f"金額{i+1}", step=100)

    #   家計簿に追加ボタン
    add_btn = st.button("家計簿に追加")
    if add_btn:
        input_list = []   # データフレーム格納用のリスト
        for i in range(len(input_widget_list)):
            # 金額が0(デフォルト値)の場合は、その行はデータフレームには格納しない
            if input_widget_list[i][3]==0:
                continue
            else:
                temp_list = [f"{input_widget_list[i][0].year:4d}年{input_widget_list[i][0].month:02d}月",
                            input_widget_list[i][0],
                            input_widget_list[i][1],
                            input_widget_list[i][2],
                            input_widget_list[i][3],
                            datetime.date.today()]
                input_list.append(temp_list)
        df_kakeibo = pd.concat([df_kakeibo, pd.DataFrame(input_list, columns=column_list)], axis=0, ignore_index=True)
        df_kakeibo.to_csv("kakeibo_data.csv", index=False)
        st.text(df_kakeibo)


####################################################################
#####   指定した年&月の支出の分類別割合円グラフ表示

# with st.container(border=True):

# matplotlibの日本語表示の設定
#  補足：conda環境ではjapanize_matplotlibがインストールできないので代替手段として
#        matplotlib.pyplotのフォントパラメータの変更を行う
# plt.rcParams['font.family'] = "MS Gothic"

# データフレームの分類カラムの要素をリスト化
column_list = ["年&月", "発生日", "収入or支出", "分類", "金額", "登録日"]
list_bunrui_all = ["給料", "臨時収入", "住居費", "食費", "光熱費", "通信費", "交通費", "交際費", "娯楽","雑費"]
list_bunrui_income = list_bunrui_all[:2]
list_bunrui_outgo = list_bunrui_all[2:]

# csvファイルを読み込みデータフレームを作成
df_kakeibo = pd.read_csv("kakeibo_data.csv")

# データフレームの中にある"年&月"をリスト化する(昇順にソート)
list_y_m = list(df_kakeibo["年&月"].unique())
list_y_m.sort()

# グルーピングした時に分類で項目の抜けがあるとグラフ表示で不都合があるので
#  全豪目を存在させる。
# 　　そのために、全ての"年&月"に全ての"分類"を存在させるために、金額0の行を追加
for ym in list_y_m:
    for name in list_bunrui_all:
        if name not in df_kakeibo[df_kakeibo["年&月"]==ym]["分類"]:
            inout = "収入" if (name in list_bunrui_income) else "支出"
            df_kakeibo = pd.concat([df_kakeibo, 
                    pd.DataFrame([[ym, "", inout, name, 0, ""]], columns=column_list)], 
                    axis=0, ignore_index=True)

# データフレームを収入用と支出用に分ける
df_kakeibo_income = df_kakeibo[df_kakeibo["収入or支出"]=="収入"]
df_kakeibo_outgo = df_kakeibo[df_kakeibo["収入or支出"]=="支出"]

# データフレームのカラムをグラフ作成に必要なもののみにする
#   年&月, 分類, 金額
df_kakeibo_income = df_kakeibo_income[["年&月", "分類", "金額"]]
df_kakeibo_outgo = df_kakeibo_outgo[["年&月", "分類", "金額"]]

# "年&月"と"分類"でグループ化して"金額"の合計を算出
df_kakeibo_group_income = df_kakeibo_income.groupby(["年&月", "分類"])["金額"].sum()
df_kakeibo_group_outgo = df_kakeibo_outgo.groupby(["年&月", "分類"])["金額"].sum()

# groupbyオブジェクトから年&月ごとのデータフレームを作成、リストに格納
list_of_df_y_m_income = []
list_of_df_y_m_outgo = []

for y_m in list_y_m:
    # 作成したデータフレームをリストに追加
    list_of_df_y_m_income.append(df_kakeibo_group_income[y_m])
    list_of_df_y_m_outgo.append(df_kakeibo_group_outgo[y_m])

### 指定した年&月の支出内訳を円グラフで表示
# 円グラフの作成
with st.container(border=True):
    st.markdown("### 月毎の支出の分類別割合")

    select_box1, select_box2 = st.columns(2)
    len_ym = len(list_y_m)
    with select_box1:
        select_box1 = st.selectbox("円グラフ1_表示月", list_y_m,
                                    index= (len_ym-1 if len_ym==1 else len_ym-2))
    with select_box2:
        select_box2 = st.selectbox("円グラフ2_表示月", list_y_m,
                                    index=(len_ym-1))

    # 指定した月の支出の合計金額を算出
    total1 = df_kakeibo_group_outgo[select_box1].sum()
    total2 = df_kakeibo_group_outgo[select_box2].sum()

    fig = plt.figure(figsize=(18, 8))
    ax1 = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 2, 1)

    df_kakeibo_group_outgo[select_box1].plot.pie( ax=ax2,
        startangle=90, counterclock=False, autopct="%.f%%", 
        title=f"{select_box1}の支出割合\n支出合計={total1:,}円",
        fontsize=8)
    df_kakeibo_group_outgo[select_box2].plot.pie( ax=ax1,
        startangle=90, counterclock=False, autopct="%.f%%", 
        title=f"{select_box2}の支出割合\n支出合計={total2:,}円",
        fontsize=8)
    # streamlitにグラフを表示
    st.pyplot(fig)


####################################################################
#####   支出額(分類ごと)と収入額の推移グラフの作成
#   支出分類リスト
list_of_outgo_index = list(df_kakeibo_group_outgo[list_y_m[0]].index)

### グラフ作成
with st.container(border=True):
    st.markdown("### 支出額(分類別)&収入額の推移グラフ")
    # ある分類の金額の全ての年月のnumpyリストを作成
    bottom = np.zeros(len(list_y_m))

    fig = plt.figure(figsize=(10,5))
    ax = fig.add_subplot(1,1,1)
    plt.title("金額推移")

    # 全ての支出分類に対して、分類ごとに縦積み棒グラフを作成
    for bunrui_index in range(len(list_of_outgo_index)):
        # 分類ごとに年月の金額のリストを作成
        out_total = np.empty(len(list_y_m))
        for ym_index, ym in enumerate(list_y_m):
            out_total[ym_index]=df_kakeibo_group_outgo[ym][list_of_outgo_index[bunrui_index]].sum()
        # 縦積み棒グラフの作成
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        ax.bar(list_y_m, out_total, label=list_of_outgo_index[bunrui_index],
                bottom = bottom)
        bottom += out_total
        ax.set(ylabel = "金額")

    # 収入合計額の年月推移の折れ線グラフを追加
    #   収入合計額の年月リストを作成
    list_of_income_index = ["給料", "臨時収入"]
    in_total = np.empty(len(list_y_m))
    for ym_index, ym in enumerate(list_y_m):
        for bunrui_index in range(len(list_of_income_index)):
            in_total[ym_index] += \
                    df_kakeibo_group_income[ym][list_of_income_index[bunrui_index]].sum()
    #   グラフ作成
    plt.plot(list_y_m, in_total, label="収入合計")
    plt.legend(loc="best")
    plt.grid(True)

    # streamlitにグラフを表示
    st.pyplot(fig)

###########################  プログラム終わり  ###########################
#########################################################################


