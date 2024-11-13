import cv2
import numpy as np
from scipy.spatial import Voronoi
from PIL import Image, ImageDraw, ImageFont

# フロア1の店舗とキャパシティの設定
floor_1_shops = ['雑貨', '雑貨', '雑貨', '雑貨', '雑貨', '書店', '雑貨', '食事', '雑貨']
shop_types = {
    "映画館": 15,
    "服屋": 2,
    "食事": 5,
    "雑貨": 3,
    "書店": 4,
    "スポーツ用品店": 6,
    "家電店": 10,
    "美容・化粧品店": 4,
    "子供向けエリア": 8,
    "カー用品店": 7
}

# 画像の読み込み
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

# フロア1の店舗の仮想的な重心をキャパシティに基づき拡張して生成
expanded_centroids = []
for shop in floor_1_shops:
    centroid = boundary_points[np.random.choice(len(boundary_points))]  # 任意のポイントを取得
    capacity_factor = shop_types[shop] / max(shop_types.values())  # キャパシティに基づく重み
    expansion_offset = np.random.normal(scale=50 * capacity_factor, size=centroid.shape)  # 偏移
    expanded_centroids.append(centroid + expansion_offset)

expanded_centroids = np.array(expanded_centroids)

# Voronoi領域の計算
vor = Voronoi(expanded_centroids)

# 描画用に各クラスタに対して色をランダムに割り当て
colors = np.random.randint(0, 255, size=(len(floor_1_shops), 3))

# # 各店舗の入口を決定し、重心から最も近い点を赤い点で描画
# store_entries = []
# for i, centroid in enumerate(expanded_centroids):
#     cluster_points = boundary_points[np.linalg.norm(boundary_points - centroid, axis=1) < 100]  # 近隣の点を取得
#     if len(cluster_points) > 0:
#         closest_point = cluster_points[np.argmin(np.linalg.norm(cluster_points - centroid, axis=1))]
#         store_entries.append(closest_point)
#         cv2.circle(image, (closest_point[1], closest_point[0]), 5, (0, 0, 255), -1)  # 赤で入口描画

# Voronoi領域に基づき、boundary_pointsを色分けして描画
for i, point in enumerate(boundary_points):
    distances = np.linalg.norm(expanded_centroids - point, axis=1)
    closest_cluster = np.argmin(distances)
    cv2.circle(image, (point[1], point[0]), 1, colors[closest_cluster].tolist(), -1)

# OpenCVの画像をPillowに変換
image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
draw = ImageDraw.Draw(image_pil)

# 日本語フォントの読み込み（必要に応じてパスを変更してください）
font_path = "/Users/cdl/Downloads/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf"  # Mac用の例
font = ImageFont.truetype(font_path, 20)

# 各店舗の種類のラベルを描画
for i, (centroid, shop) in enumerate(zip(expanded_centroids, floor_1_shops)):
    position = (int(centroid[1]), int(centroid[0]))  # ラベル位置（y, x）
    draw.text(position, shop, font=font, fill=(0, 0, 0))

# Pillow画像をOpenCV形式に戻す
image_with_labels = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

# 結果を表示
cv2.imshow("Floor 1 Store Layout with Entrances and Labels", image_with_labels)
cv2.waitKey(0)
cv2.destroyAllWindows()
