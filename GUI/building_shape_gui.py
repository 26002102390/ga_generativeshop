import tkinter as tk
from tkinter import messagebox
import itertools
import numpy as np
from GUI.polygon_grid_gui import PolygonGridApp

class BuildingShapeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Building Shape Generator")

        # ラベル
        self.label = tk.Label(root, text="建物の外形を描画してください")
        self.label.pack(pady=5)

        # モード選択ボタン
        self.mode = tk.StringVar(value="rectangle")
        self.rectangle_button = tk.Radiobutton(root, text="Rectangle", variable=self.mode, value="rectangle")
        self.circle_button = tk.Radiobutton(root, text="Circle", variable=self.mode, value="circle")
        self.rectangle_button.pack(pady=5)
        self.circle_button.pack(pady=5)

        # Undo/Redo/Clear/Apply ボタンを横並びに配置
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        # Undo/Redo ボタン
        self.undo_button = tk.Button(button_frame, text="Undo", command=self.undo)
        self.undo_button.pack(side="left", padx=5)
        self.redo_button = tk.Button(button_frame, text="Redo", command=self.redo)
        self.redo_button.pack(side="left", padx=5)

        # クリアボタン
        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear)
        self.clear_button.pack(side="left", padx=5)

        # 適用ボタン
        self.apply_button = tk.Button(button_frame, text="Apply", command=self.apply)
        self.apply_button.pack(side="left", padx=5)

        # キャンバスを追加して描画
        self.canvas = tk.Canvas(root, width=400, height=300, bg="white")
        self.canvas.pack(pady=5)

        # 描画の初期化
        self.start_x = None
        self.start_y = None
        self.shape = None

        # 描画履歴スタック
        self.shapes = []  # 図形IDを格納するリスト
        self.redo_stack = []  # Redo用のスタック

        self.update_button_state()  # ボタンの状態を更新

        # キャンバスにイベントをバインド
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.shape = None

    def on_mouse_drag(self, event):
        if self.shape:
            self.canvas.delete(self.shape)
        if self.mode.get() == "rectangle":
            self.shape = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="blue", width=3)
        elif self.mode.get() == "circle":
            self.shape = self.canvas.create_oval(self.start_x, self.start_y, event.x, event.y, outline="green", width=3)

    def on_button_release(self, event):
        if self.mode.get() == "rectangle":
            shape_id = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, fill="blue", width=3)
            shape_info = {"id": shape_id, "type": "rectangle", "coords": (self.start_x, self.start_y, event.x, event.y)}
        elif self.mode.get() == "circle":
            shape_id = self.canvas.create_oval(self.start_x, self.start_y, event.x, event.y, fill="yellow", width=3)
            shape_info = {"id": shape_id, "type": "circle", "coords": (self.start_x, self.start_y, event.x, event.y)}

        self.shapes.append(shape_info)
        self.redo_stack.clear()
        self.update_button_state()

    def undo(self):
        if self.shapes:
            shape_info = self.shapes.pop()
            self.canvas.delete(shape_info["id"])
            self.redo_stack.append(shape_info)
            self.update_button_state()

    def redo(self):
        if self.redo_stack:
            shape_info = self.redo_stack.pop()
            if shape_info["type"] == "rectangle":
                shape_id = self.canvas.create_rectangle(*shape_info["coords"], fill="blue", width=3)
            elif shape_info["type"] == "circle":
                shape_id = self.canvas.create_oval(*shape_info["coords"], fill="green", width=3)
            self.shapes.append({"id": shape_id, "type": shape_info["type"], "coords": shape_info["coords"]})
            self.update_button_state()

    def clear(self):
        self.canvas.delete("all")
        self.shapes.clear()
        self.redo_stack.clear()
        self.update_button_state()

    def apply(self):
        if not self.shapes:
            messagebox.showwarning("Warning", "No shapes to apply.")
            return

        # 全ての図形の座標を取得
        all_coords = []
        for shape_info in self.shapes:
            coords = shape_info["coords"]
            all_coords.append((coords[0], coords[1]))  # 左上
            all_coords.append((coords[0], coords[3]))  # 左下
            all_coords.append((coords[2], coords[1]))  # 右上
            all_coords.append((coords[2], coords[3]))  # 右下

        # ユニークな点を取得
        unique_points = set(all_coords)

        # 接点も考慮して外周を計算
        outer_polygon = self.get_outer_polygon(list(unique_points))
        # print(outer_polygon)

        # 斜めの線分を取得
        diagonal_segments = self.find_diagonal_segments(outer_polygon)

        if diagonal_segments:
            # self.canvas.create_polygon(diagonal_segments, fill="purple", outline="black", width=3)
            # print(f"Outer polygon: {diagonal_segments}")
            new_window = tk.Tk()
            new_window.config(bg="grey")
            app = PolygonGridApp(new_window, diagonal_segments)
            app.canvas.config(bg="grey")
            new_window.mainloop()
        self.update_button_state()

    # グラハムスキャンを用いた凸包の計算
    def get_outer_polygon(self, points):
        points = sorted(set(points))  # 重複を排除してソート
        if len(points) <= 1:
            return points

        def cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        # 下半分
        lower = []
        for p in points:
            while len(lower) >= 2 and cross(lower[-2], lower[-1], p) < 0:
                lower.pop()
            lower.append(p)

        # 上半分
        upper = []
        for p in reversed(points):
            while len(upper) >= 2 and cross(upper[-2], upper[-1], p) < 0:
                upper.pop()
            upper.append(p)

        return lower[:-1] + upper[:-1]  # 最後の点は重複しているため削除

    # 斜めの線になる部分を取得し、頂点を追加
    def find_diagonal_segments(self, vertices):
        diagonal_segments = []
        n = len(vertices)
        for i in range(n):
            # 現在の頂点と次の頂点を取得
            current_vertex = vertices[i]
            next_vertex = vertices[(i + 1) % n]  # 円環状にするためにmodを使用

            # 頂点の座標を取得
            x1, y1 = current_vertex
            x2, y2 = next_vertex

            if diagonal_segments not in current_vertex:
                diagonal_segments.append(current_vertex)

            # 垂直または水平の線分を確認
            if x1 != x2 and y1 != y2 and x1 < x2 and y1 < y2:
                diagonal_segments.append((x1, y2))
            elif x1 != x2 and y1 != y2 and x1 > x2 and y1 > y2:
                diagonal_segments.append((x1, y2))
            elif x1 != x2 and y1 != y2 and x1 < x2 and y1 > y2:
                diagonal_segments.append((x2, y1))
            elif x1 != x2 and y1 != y2 and x1 > x2 and y1 < y2:
                diagonal_segments.append((x2, y1))

            if diagonal_segments not in next_vertex:
                diagonal_segments.append(next_vertex)

        return diagonal_segments

    # ボタンの無効化の管理
    def update_button_state(self):
        if self.shapes:
            self.undo_button.config(state="normal")
        else:
            self.undo_button.config(state="disabled")

        if self.redo_stack:
            self.redo_button.config(state="normal")
        else:
            self.redo_button.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    gui = BuildingShapeGUI(root)
    root.mainloop()
