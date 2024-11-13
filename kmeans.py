import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image, ImageDraw, ImageFont

# フロア1の店舗とキャパシティの設定
floor_1_shops = ['雑貨', '雑貨', '雑貨', '雑貨', '雑貨', '書店', '雑貨', '食事', '雑貨']
NUM_SHOPS = len(floor_1_shops)  # 店舗数

# 画像を読み込む
image_path = "./high_res_screenshot.jpg"  # アップロードした画像のパス
image = cv2.imread(image_path)

# BGR色空間で指定された色範囲を定義
target_color_bgr = np.array([183, 66, 67])  # BGR形式で指定
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

# KMeansクラスタリングを使ってboundary_pointsをNUM_SHOPS個に分割
kmeans = KMeans(n_clusters=NUM_SHOPS, random_state=42)
kmeans.fit(boundary_points)
labels = kmeans.labels_

# 各クラスタに対して色をランダムに割り当て
colors = np.random.randint(0, 255, size=(NUM_SHOPS, 3))

# 各クラスタの重心を計算
cluster_centers = kmeans.cluster_centers_

# 店の入口を決定（重心に最も近い点を選択）
store_entries = []
for shop_id in range(NUM_SHOPS):
    # 各クラスタに属する点を取得
    cluster_points = boundary_points[labels == shop_id]

    # 重心に最も近い点を選択
    distances = np.sqrt(np.sum((cluster_points - cluster_centers[shop_id])**2, axis=1))
    closest_point_idx = np.argmin(distances)
    store_entries.append(cluster_points[closest_point_idx])

# 結果をOpenCVで描画（赤い点や色付き点を描画）
for shop_id, shop_entry in enumerate(store_entries):
    cluster_points = boundary_points[labels == shop_id]
    # クラスタのポイントをその店に対応する色で描画
    for point in cluster_points:
        cv2.circle(image, (point[1], point[0]), 1, colors[shop_id].tolist(), -1)

    # 店の入口（重心に最も近い点）を赤で描画
    cv2.circle(image, (shop_entry[1], shop_entry[0]), 5, (0, 0, 255), -1)

# PIL画像に変換（文字を描画するため）
pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))  # OpenCV形式からPIL形式に変換
draw = ImageDraw.Draw(pil_image)

# 日本語フォントの読み込み（必要に応じてパスを変更してください）
font_path = "/Users/cdl/Downloads/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf"  # Mac用の例
font = ImageFont.truetype(font_path, 20)

# 店舗名を描画（PILで日本語を描画）
for shop_id, shop_entry in enumerate(store_entries):
    shop_name = floor_1_shops[shop_id]  # 店舗名（ここでは仮に順番で指定）

    # テキストのバウンディングボックスを取得
    text_bbox = draw.textbbox((0, 0), shop_name, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # テキストの背景用の白い四角形を描画
    background_position = (int(shop_entry[1] + 10), int(shop_entry[0] - 10))
    background_rectangle = [
        background_position,
        (background_position[0] + text_width + 4, background_position[1] + text_height + 4)
    ]
    draw.rectangle(background_rectangle, fill=(255, 255, 255))

    # テキストを白背景の上に描画
    draw.text((background_position[0] + 2, background_position[1] + -5), shop_name, font=font, fill=(0, 0, 0))  # 黒色

# PIL画像をOpenCV形式に戻す
final_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

# 結果を表示
cv2.imshow("Optimized Store Layout", final_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
