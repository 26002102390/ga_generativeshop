import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from deap import base, creator, tools, algorithms
from scipy.spatial import distance_matrix
import json

jp_font = fm.FontProperties(fname='/Users/cdl/Downloads/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf')  # フォントパス

# 店舗の種類を設定
store_types = ["飲食店", "洋服店", "本屋", "電化製品店", "おもちゃ屋", "映画館", "ゲームセンター"]

# 個体遺伝子の作成
def create_shop():
    """
    ショップの個体を作成
    [x座標, y座標, 幅, 高さ, 店舗の種類]
    幅と高さが50x50の範囲内に収まるように設計
    """
    width = random.randint(5, 10)
    height = random.randint(5, 10)
    
    # x座標とy座標は、幅と高さがエリア外に出ないように制限
    x = random.randint(0, 50 - width)
    y = random.randint(0, 50 - height)

    store_type = random.choice(store_types)
    
    return [x, y, width, height, store_type]


# 店舗間の回遊性を評価する関数
def eval_circulation(shop):
    # 店舗間の回遊性を評価する関数
    threshold_distance = 30  # 店舗間がつながると見なす距離のしきい値
    penalty_per_deadend = 100  # デッドエンド1つにつき課されるペナルティ

    # 各店舗の座標を抽出
    coords = np.array([(store[0], store[1]) for store in shop])

    # 店舗間の距離行列を計算
    dist_matrix = distance_matrix(coords, coords)

    # 隣接行列を作成（しきい値以下の距離の店舗はつながっているとみなす）
    adjacency_matrix = (dist_matrix < threshold_distance).astype(int)

    # 店舗ごとの接続数を計算（各店舗が何店舗とつながっているか）
    connections_per_store = adjacency_matrix.sum(axis=1)

    # デッドエンドの数をカウント（接続数が1以下の店舗をデッドエンドとみなす）
    num_deadends = np.sum(connections_per_store <= 1)

    # デッドエンドの数に基づいてペナルティを計算
    deadend_penalty = num_deadends * penalty_per_deadend

    return deadend_penalty

# 仕組みの詳細
# 距離行列 (distance_matrix) の作成: 店舗の座標間の距離を計算し、2店舗が一定の距離内にある場合、隣接しているとみなします。
# 隣接行列 (adjacency_matrix) の作成: 各店舗が他の店舗とつながっているかを2次元の行列で表現し、つながっている店舗同士に1を、つながっていない場合に0を割り当てます。
# 接続数のカウント: 各店舗の接続数を数え、接続数が1以下の店舗をデッドエンド（行き止まり）と定義します。
# ペナルティの加算: デッドエンドの数に応じてペナルティを加算し、回遊性が悪い（デッドエンドが多い）レイアウトには低評価を与えます。
# 改良の余地
# 距離のしきい値 (threshold_distance) は調整が可能です。回遊性を強く評価する場合は、しきい値を小さく、店舗間のつながりを強調する場合は大きく設定します。
# デッドエンドのペナルティ を調整し、デッドエンドの数が少ないほど評価が高くなるように変更できます。
# より詳細に、複雑な経路や「最適な動線」を評価する場合には、グラフ理論を用いて最短経路や巡回パスを計算するアプローチも考えられます。

# 店舗の評価関数
def eval_category(shop):
    category_bonus = 0
    for store in shop:
        x, y, width, height, store_type = store
        # 飲食店が中心にあればボーナス
        if store_type == "飲食店" and 20 < x < 30 and 20 < y < 30:
            category_bonus += 100
        # 飲食店と洋服店に関しては同じ種類の店舗が近くにあるとボーナス
        if store_type == "飲食店":
            for other_store in shop:
                x, y, width, height, store_type = store
                if store_type == "飲食店":
                    distance = np.sqrt((x - other_store[0])**2 + (y - other_store[1])**2)
                    if distance < 10:
                        category_bonus += 10
        if store_type == "洋服店":
            for other_store in shop:
                x, y, width, height, store_type = store
                if store_type == "洋服店":
                    distance = np.sqrt((x - other_store[0])**2 + (y - other_store[1])**2)
                    if distance < 10:
                        category_bonus += 10
        # その他の店に関しては同じ種類の店舗が存在するだけでペナルティ
        if store_type == "本屋":
            num = 0
            for other_store in shop:
                x, y, width, height, store_type = store
                if store_type == "本屋":
                    num += 1
            if num > 1:
                category_bonus -= 100
        if store_type == "電化製品店":
            num = 0
            for other_store in shop:
                x, y, width, height, store_type = store
                if store_type == "電化製品店":
                    num += 1
            if num > 1:
                category_bonus -= 100
        if store_type == "おもちゃ屋":
            num = 0
            for other_store in shop:
                x, y, width, height, store_type = store
                if store_type == "おもちゃ屋":
                    num += 1
            if num > 1:
                category_bonus -= 100
        if store_type == "映画館":
            num = 0
            for other_store in shop:
                x, y, width, height, store_type = store
                if store_type == "映画館":
                    num += 1
            if num > 1:
                category_bonus -= 100
        if store_type == "ゲームセンター":
            num = 0
            for other_store in shop:
                x, y, width, height, store_type = store
                if store_type == "ゲームセンター":
                    num += 1
            if num > 1:
                category_bonus -= 100
                    
    return category_bonus

# 評価関数の作成
def eval_shop(shop):
    """
    ショップの評価関数
    ショップごとの距離ができるだけ離れているほど評価が高い
    ショップの面積ができるだけ大きいほど評価が高い
    ショップが重なっている場合ペナルティーを与える
    """
    total_distance = 0
    total_area = 0
    overlap_penalty = 0
    for i in range((len(shop))):
        shop1 = shop[i]
        total_area += shop1[2] * shop1[3]
        for j in range(i+1, len(shop)):
            shop2 = shop[j]
            distance = np.sqrt((shop1[0] - shop2[0])**2 + (shop1[1] - shop2[1])**2)
            total_distance += distance
            if shop1[0] < shop2[0] + shop2[2] and shop1[0] + shop1[2] > shop2[0] and shop1[1] < shop2[1] + shop2[3] and shop1[1] + shop1[3] > shop2[1]:
                overlap_penalty += 100

    deadend_penalty = eval_circulation(shop)
    category_bonus = eval_category(shop)
    return total_distance + total_area + category_bonus - overlap_penalty*2 - deadend_penalty,
    # return total_distance - overlap_penalty,

# 交叉関数の作成
def cx_shop(shop1, shop2):
    """
    ショップの交叉関数
    交叉点をランダムに選択し、それ以降の遺伝子を入れ替える
    """
    cxpoint = random.randint(1, len(shop1)-1)
    shop1[cxpoint:], shop2[cxpoint:] = shop2[cxpoint:], shop1[cxpoint:]
    return shop1, shop2

# 突然変異関数の作成
def mut_shop(shop, mu, sigma, indpb):
    """
    ショップの突然変異関数
    ガウス分布に基づいて座標と大きさをランダムに変動させる
    """
    for i in range(len(shop)):
        if random.random() < indpb:
            # 0: x座標, 1: y座標, 2: 幅, 3: 高さに対してガウス変異を適用
            shop[i][0] += random.gauss(mu, sigma)
            shop[i][1] += random.gauss(mu, sigma)
            shop[i][2] += random.gauss(mu, sigma)
            shop[i][3] += random.gauss(mu, sigma)

            # 幅と高さが5以上10以下になるように制限
            shop[i][2] = max(5, min(shop[i][2], 10))  # 幅の制約
            shop[i][3] = max(5, min(shop[i][3], 10))  # 高さの制約

            # 座標がエリア外に出ないように制限
            shop[i][0] = max(0, min(shop[i][0], 50 - shop[i][2]))
            shop[i][1] = max(0, min(shop[i][1], 50 - shop[i][3]))

    return shop,

# 遺伝的アルゴリズムの設定
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# ベースクラスのセットアップ
toolbox = base.Toolbox()

# 個体を生成（属性がn個のリスト）
toolbox.register("individual", tools.initRepeat, creator.Individual, create_shop, n=10)

# 集団を生成（個体を複数集めたもの）
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# 交叉、突然変異、選択関数の登録
toolbox.register("evaluate", eval_shop)
toolbox.register("mate", cx_shop)
toolbox.register("mutate", mut_shop, mu=0, sigma=1, indpb=0.2)

# 選択関数の定義　（tournsize: 何個体で勝負するか）
toolbox.register("select", tools.selTournament, tournsize=3)

# 遺伝的アルゴリズムの実行
if __name__ == "__main__":
    # 初期集団の生成
    population = toolbox.population(n=300)

    # 進化の実行(交叉確率0.5, 突然変異確率0.2, 進化計算の世代数40, verboseは進捗状況をコンソールに出力するか)
    algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=60, verbose=True)

    # 最も優れている個体を選択
    best_ind = tools.selBest(population, 1)[0]
    print('Best individual is ', best_ind)

    # 最も優れている個体の評価値を表示
    print('Best individual evaluation is ', eval_shop(best_ind))

    # 個体データをわかりやすく整形
    best_individual_data = {
        "shops": [
            {
                "x_coordinate": shop[0],
                "y_coordinate": shop[1],
                "width": shop[2],
                "height": shop[3],
                "store_type": shop[4]
            }
            for shop in best_ind
        ]
    }

    # JSONファイルに保存
    with open('best_individual.json', 'w') as json_file:
        json.dump(best_individual_data, json_file, ensure_ascii=False, indent=4)

    print("Best individual data has been saved to best_individual.json")

    # 最も優れている個体のショップの配置を表示
    fig, ax = plt.subplots()
    for i in range(len(best_ind)):
        shop = best_ind[i]
        ax.add_patch(plt.Rectangle((shop[0], shop[1]), shop[2], shop[3], edgecolor='black', facecolor='none'))
        # 店舗の中心位置を計算 (x + width / 2, y + height / 2)
        center_x = shop[0] + shop[2] / 2
        center_y = shop[1] + shop[3] / 2
        
        # 店舗の種類をラベルとして表示
        ax.text(center_x, center_y, shop[4], ha='center', va='center', fontsize=8, color='blue', fontproperties=jp_font)

    plt.xlim(0, 50)
    plt.ylim(0, 50)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()