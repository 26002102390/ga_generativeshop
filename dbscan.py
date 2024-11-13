import cv2
import numpy as np
from sklearn.cluster import DBSCAN

# 画像を読み込む
image_path = "./high_res_screenshot.jpg"  # アップロードした画像のパス
image = cv2.imread(image_path)

# BGR色空間で指定された色範囲を定義
target_color_bgr = np.array([183,66,67])  # BGR形式で指定
threshold = 10  # 色の範囲の許容誤差

# 指定色の周辺の範囲を定義
lower_bound = target_color_bgr - threshold
upper_bound = target_color_bgr + threshold

# マスクを作成
mask = cv2.inRange(image, lower_bound, upper_bound)

# マスクから輪郭を検出
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 黒色の背景に輪郭を描画（デバッグ用）
boundary_image = np.zeros_like(image)
cv2.drawContours(boundary_image, contours, -1, (255, 255, 255), 2)

# 境界線のピクセル座標を取得
boundary_points = np.column_stack(np.where(boundary_image > 0))

# DBSCANクラスタリングを使ってboundary_pointsをクラスタリング
eps = 10  # クラスタリングの半径
min_samples = 10  # クラスタに必要な最小サンプル数
dbscan = DBSCAN(eps=eps, min_samples=min_samples)
labels = dbscan.fit_predict(boundary_points)

# クラスタごとに色を割り当てる
unique_labels = np.unique(labels)
colors = np.random.randint(0, 255, size=(len(unique_labels), 3))

# 店の入口を決定（重心に最も近い点を選択）
store_entries = []
for shop_id in unique_labels:
    if shop_id == -1:
        continue  # ノイズとされる点（-1）の場合はスキップ

    # 各クラスタに属する点を取得
    cluster_points = boundary_points[labels == shop_id]

    # 重心を計算
    cluster_center = np.mean(cluster_points, axis=0)

    # 重心に最も近い点を選択
    distances = np.sqrt(np.sum((cluster_points - cluster_center)**2, axis=1))
    closest_point_idx = np.argmin(distances)
    store_entries.append(cluster_points[closest_point_idx])

# 結果を画像に描画
for shop_id, shop_entry in enumerate(store_entries):
    # 各クラスタに対してその店に対応する色で描画
    cluster_points = boundary_points[labels == unique_labels[shop_id]]
    for point in cluster_points:
        cv2.circle(image, (point[1], point[0]), 1, colors[shop_id].tolist(), -1)

    # 店の入口（重心に最も近い点）を赤で描画
    cv2.circle(image, (shop_entry[1], shop_entry[0]), 5, (0, 0, 255), -1)

# 結果を表示
cv2.imshow("Optimized Store Layout", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
