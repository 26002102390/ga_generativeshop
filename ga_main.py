import random
import numpy as np
import matplotlib.pyplot as plt
from deap import base, creator, tools, algorithms

# 個体遺伝子の作成
def create_shop():
    """
    ショップの個体を作成
    (x座標, y座標, 幅, 高さ)
    幅と高さが50x50の範囲内に収まるように設計
    """
    width = random.randint(5, 10)
    height = random.randint(5, 10)
    
    # x座標とy座標は、幅と高さがエリア外に出ないように制限
    x = random.randint(0, 50 - width)
    y = random.randint(0, 50 - height)
    
    return [x, y, width, height]

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
                overlap_penalty += 1000
    
    return total_distance + total_area - overlap_penalty,
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

    # 最も優れている個体のショップの配置を表示
    fig, ax = plt.subplots()
    for i in range(len(best_ind)):
        shop = best_ind[i]
        ax.add_patch(plt.Rectangle((shop[0], shop[1]), shop[2], shop[3], edgecolor='black', facecolor='none'))
    plt.xlim(0, 50)
    plt.ylim(0, 50)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()