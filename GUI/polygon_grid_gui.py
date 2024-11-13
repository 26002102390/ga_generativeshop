import sys
sys.path.append('/Users/cdl/Desktop/VScode_workspace/ga_generativeshop')

import tkinter as tk
from tkinter import Canvas, messagebox
from GUI.polygon_saver import Saver  # saver.pyのSaverクラスをインポート
from GUI.database_loader import LoadDatabaseDialog  # LoadDatabaseDialogクラスをインポート
from PIL import ImageGrab,Image

outer_polygon = [
    (75, 46), (210, 46), (357, 48), (357, 121),
    (330, 121), (330, 188), (294, 188), (294, 165),
    (139, 165), (139, 123), (75, 123), (75, 46)
]

class PolygonGridApp:
    def __init__(self, root, outer_polygon):
        self.root = root
        self.canvas = Canvas(root, width=400, height=400)
        self.canvas.pack()
        self.checker = False

        self.saver = Saver(self)  # PolygonGridAppのインスタンスを渡す

        self.outer_polygon = outer_polygon
        self.grid_size = 20
        self.cell_colors = {}

        # 塗りつぶしに使う色と初期色
        self.fill_colors = ["white", "white", "blue", "green", "yellow", "gray"]
        self.current_color_index = 1  # 初期は白

        # ボタンの作成
        self.color_button_road = tk.Button(root, text="道を塗る", command=self.change_color_blue)
        self.color_button_escalator = tk.Button(root, text="エスカレータを塗る", command=self.change_color_green)
        self.color_button_shop_area = tk.Button(root, text="店舗エリアを塗る", command=self.change_color_yellow)
        self.color_button_cutout_area = tk.Button(root, text="切り欠きエリアを塗る", command=self.change_color_gray)
        self.save_button = tk.Button(root, text="保存", command=lambda: self.saver.save_with_name(outer_polygon))
        self.load_button = tk.Button(root, text="読み込み", command=self.open_load_dialog)

        # ボタンの背景色設定
        self.color_button_road.config(highlightbackground="gray")
        self.color_button_escalator.config(highlightbackground="gray")
        self.color_button_shop_area.config(highlightbackground="gray")
        self.color_button_cutout_area.config(highlightbackground="gray")
        self.save_button.config(highlightbackground="gray")
        self.load_button.config(highlightbackground="gray")

        # ボタンのリスト
        self.color_buttons = [
            self.color_button_road,
            self.color_button_escalator,
            self.color_button_shop_area,
            self.color_button_cutout_area
        ]

        # ボタンを画面に配置
        for button in self.color_buttons:
            button.pack()
        self.save_button.pack()
        self.load_button.pack()


        # self.draw_polygon()
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_click)

    def open_load_dialog(self):
        # LoadDatabaseDialogを開いてロード処理を行う
        load_dialog = LoadDatabaseDialog(self.root, self.saver)
        load_dialog.show()

    def draw_polygon(self):
        self.canvas.create_polygon(self.outer_polygon, fill="", outline="grey", width=2)

    def draw_grid(self):
        for x in range(0, 400, self.grid_size):
            for y in range(0, 400, self.grid_size):
                if self.point_in_polygon(x + self.grid_size // 2, y + self.grid_size // 2, self.outer_polygon):
                    cell = self.canvas.create_rectangle(
                        x, y, x + self.grid_size, y + self.grid_size,
                        fill="white", outline="gray"
                    )
                    self.cell_colors[cell] = "white"

    def point_in_polygon(self, x, y, polygon):
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def on_click(self, event):
        clicked_items = self.canvas.find_withtag("current")
        for item in clicked_items:
            if item in self.cell_colors:
                # 現在選択されている色で塗りつぶす
                new_color = self.fill_colors[self.current_color_index]
                self.canvas.itemconfig(item, fill=new_color)
                self.cell_colors[item] = new_color

    def update_button_state(self, active_button):
        # 全ボタンをデフォルトの色に戻し、選択中のボタンだけハイライト
        for button in self.color_buttons:
            button.config(highlightbackground="gray")  # デフォルト色に戻す
        active_button.config(highlightbackground=self.fill_colors[self.current_color_index])  # 選択中のボタンをハイライト

    def change_color_blue(self):
        self.current_color_index = 2
        self.update_button_state(self.color_button_road)
        print("Blue selected")  # デバッグ用出力

    def change_color_green(self):
        self.current_color_index = 3
        self.update_button_state(self.color_button_escalator)
        print("Green selected")  # デバッグ用出力

    def change_color_yellow(self):
        self.current_color_index = 4
        self.update_button_state(self.color_button_shop_area)
        print("Yellow selected")  # デバッグ用出力

    def change_color_gray(self):
        self.current_color_index = 5
        self.update_button_state(self.color_button_cutout_area)
        print("Gray selected")  # デバッグ用出力

class PolygonGridApp_ga:
    def __init__(self, root, outer_polygon):
        self.root = root
        self.canvas = Canvas(root, width=400, height=400)
        self.canvas.pack()
        self.checker = False

        self.saver = Saver(self)  # PolygonGridAppのインスタンスを渡す

        self.outer_polygon = outer_polygon
        self.grid_size = 20
        self.cell_colors = {}

        # ボタンの作成
        self.ga_button = tk.Button(root, text="遺伝的アルゴリズム実行", command=self.ga_button)

        # ボタンの背景色設定
        self.ga_button.config(highlightbackground="gray")

        self.ga_button.pack()

        self.draw_grid()

    def open_load_dialog(self):
        # LoadDatabaseDialogを開いてロード処理を行う
        load_dialog = LoadDatabaseDialog(self.root, self.saver)
        load_dialog.show()

    def draw_grid(self):
        for x in range(0, 400, self.grid_size):
            for y in range(0, 400, self.grid_size):
                if self.point_in_polygon(x + self.grid_size // 2, y + self.grid_size // 2, self.outer_polygon):
                    cell = self.canvas.create_rectangle(
                        x, y, x + self.grid_size + 2, y + self.grid_size + 2,
                        fill="white", outline=None
                    )
                    self.cell_colors[cell] = "white"

    def draw_polygon_outline(self,x,y, color):
        if self.point_in_polygon(x + self.grid_size // 2, y + self.grid_size // 2, self.outer_polygon):
            cell = self.canvas.create_rectangle(
                x, y, x + self.grid_size + 1, y + self.grid_size + 1,
                fill=color, outline=color
            )
            self.cell_colors[cell] = color

    def point_in_polygon(self, x, y, polygon):
        n = len(polygon)
        inside = False
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def ga_button(self):
        print("GA button clicked")
        self.capture_window(self.canvas)

    def capture_window(self, canvas):
        # canvasウィジェットの位置とサイズを取得してキャプチャ
        x = canvas.winfo_rootx()
        y = canvas.winfo_rooty()
        width = x + canvas.winfo_width()
        height = y + canvas.winfo_height()

        # キャプチャをJPEGとして保存
        # img = ImageGrab.grab(bbox=(x, y, width, height))
        # img = img.convert("RGB")  # RGBAをRGBに変換
        # # 解像度を100%にして保存
        # img.save("screenshot.jpg", "JPEG", quality=100)
        # print("画像を保存しました。")
        # キャプチャをJPEGとして保存
        img = ImageGrab.grab(bbox=(x, y, width, height))
        img = img.convert("RGB")  # RGBAをRGBに変換

        # 解像度を上げるためにリサイズ (倍率を2倍に設定)
        new_width = img.width * 2
        new_height = img.height * 2
        img_high_res = img.resize((new_width, new_height), Image.LANCZOS)  # 高品質なリサイズ

        # 高解像度で保存
        img_high_res.save("high_res_screenshot.jpg", "JPEG", quality=100)
        print("高解像度画像を保存しました。")

if __name__ == "__main__":
    root = tk.Tk()
    root.config(bg="grey")
    app = PolygonGridApp(root, outer_polygon)
    app.canvas.config(bg="grey")
    root.mainloop()

