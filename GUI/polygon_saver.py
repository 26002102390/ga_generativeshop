import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3
import os
import GUI

class Saver:
    def __init__(self, app):
        self.app = app
        self.db_folder = os.path.join(os.path.dirname(__file__), "../dbfiles")
        os.makedirs(self.db_folder, exist_ok=True)
        self.db_name = os.path.join(self.db_folder, "default_grid_colors.db")


    def open_db_connection(self, db_name=None):
        # デフォルトで現在の db_name に接続
        if db_name is None:
            db_name = self.db_name
        return sqlite3.connect(db_name)

    def create_table(self, db_name):
        try:
            with self.open_db_connection(db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS cell_colors (
                                    x INTEGER, y INTEGER, color TEXT, PRIMARY KEY (x, y, color))''')
                cursor.execute('''CREATE TABLE IF NOT EXISTS polygons (
                                    vertex_index INTEGER, x INTEGER, y INTEGER, PRIMARY KEY (vertex_index))''')
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("エラー", f"テーブル作成時にエラーが発生しました: {e}")

    def save_cell_color(self, x, y, color, db_name):
        try:
            with self.open_db_connection(db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT OR REPLACE INTO cell_colors (x, y, color)
                                VALUES (?, ?, ?)''', (x, y, color))
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("エラー", f"セルの色の保存中にエラーが発生しました: {e}")

    def save_polygon(self, outer_polygon, db_name):
        try:
            with self.open_db_connection(db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM polygons")  # 既存のデータを削除
                for index, (x, y) in enumerate(outer_polygon):
                    cursor.execute(
                        "INSERT INTO polygons (vertex_index, x, y) VALUES (?, ?, ?)", (index, x, y)
                    )
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("エラー", f"ポリゴンの保存中にエラーが発生しました: {e}")

    def save_with_name(self, outer_polygon):
        db_name = simpledialog.askstring("保存", "データベース名を入力してください（例: grid_colors.db）:")
        if db_name :#self.recent_cell_color==None:
            # print(self.recent_cell_color)
            # print("recent_cell_color is None")
            db_path = os.path.join(self.db_folder, db_name if db_name.endswith(".db") else f"{db_name}.db")
            self.create_table(db_path)
            for cell, color in self.app.cell_colors.items():
                # print(type(cell))
                # print(color)
                x1, y1, x2, y2 = self.app.canvas.coords(cell)
                x, y = int(x1), int(y1)
                self.save_cell_color(x, y, color, db_path)
            # print(outer_polygon)
            # print(db_path)
            self.save_polygon(outer_polygon, db_path)
            messagebox.showinfo("保存完了", f"{db_name} を保存しました。")
        elif db_name and self.recent_cell_color!=None:
            print("recent_cell_color is not None")
            db_path = os.path.join(self.db_folder, db_name if db_name.endswith(".db") else f"{db_name}.db")
            self.create_table(db_path)
            # 既存のキャンバスのセルカラー情報と recent_cell_color をマージ
            merged_colors = self.app.cell_colors.copy()  # 既存のセルカラーをコピー
            print("これがこのカラー",merged_colors)
            print("end")
            print(type(self.recent_cell_color))
            # merged_colors.update(self.recent_cell_color)  # recent_cell_color の情報で上書き

            # マージしたセルカラー情報を保存
            for cell, color in merged_colors.items():
                # cell が数字の場合でかつ白色で無い時のみ保存
                if isinstance(cell, int) and color != "white":
                    tuple_cell = (cell,)
                    if tuple_cell in self.recent_cell_color:
                        x1, y1, x2, y2 = self.app.canvas.coords(tuple_cell)
                        x, y = int(x1), int(y1)
                        self.save_cell_color(x, y, color, db_path)

            self.save_polygon(outer_polygon, db_path)
            messagebox.showinfo("保存完了", f"{db_name} を保存しました。")


    def load_from_db(self):
        # print("Loading from DB")
        db_files = [f for f in os.listdir(self.db_folder) if f.endswith(".db")]
        if not db_files:
            messagebox.showinfo("情報", "ロード可能なデータベースが見つかりません。")
            return

        selection_window = tk.Toplevel(self.app.root)
        selection_window.title("データベースを選択")
        selection_window.geometry("300x250")
        listbox = tk.Listbox(selection_window, selectmode=tk.SINGLE, width=40, height=10)
        for db_file in db_files:
            listbox.insert(tk.END, db_file)
        listbox.pack(pady=10)

        def on_select():
            selected_index = listbox.curselection()
            if not selected_index:
                messagebox.showwarning("警告", "データベースを選択してください。")
                return

            self.db_name = os.path.join(self.db_folder, db_files[selected_index[0]])
            self.create_table(self.db_name)
            self.load_grid_shape()
            self.load_grid_colors()
            selection_window.destroy()
            messagebox.showinfo("読み込み完了", "データを読み込みました。")

        select_button = tk.Button(selection_window, text="選択", command=on_select)
        select_button.pack(pady=5)

    def load_grid_colors(self):
        try:
            with self.open_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT x, y, color FROM cell_colors")
                for x, y, color in cursor.fetchall():
                    cell = self.app.canvas.find_closest(x, y)
                    self.app.canvas.itemconfig(cell, fill=color, outline="grey")
        except sqlite3.Error as e:
            messagebox.showerror("エラー", f"セルの色の読み込み中にエラーが発生しました: {e}")

    def load_grid_colors_not_outline(self):
        try:
            with self.open_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT x, y, color FROM cell_colors")
                for x, y, color in cursor.fetchall():
                    cell = self.app.canvas.find_closest(x, y)
                    self.app.canvas.itemconfig(cell, fill=color, outline=color)
        except sqlite3.Error as e:
            messagebox.showerror("エラー", f"セルの色の読み込み中にエラーが発生しました: {e}")

    def load_grid_shape(self):
        try:
            with self.open_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT x, y FROM polygons ORDER BY vertex_index")
                self.app.outer_polygon = cursor.fetchall()
                # print(self.app.outer_polygon)
                self.app.draw_polygon()
                self.app.draw_grid()
        except sqlite3.Error as e:
            messagebox.showerror("エラー", f"ポリゴンの読み込み中にエラーが発生しました: {e}")

    def load_outer_polygon(self):
        try:
            with self.open_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT x, y FROM polygons ORDER BY vertex_index")
                self.app.outer_polygon = cursor.fetchall()
                # print(self.app.outer_polygon)
                return self.app.outer_polygon
        except sqlite3.Error as e:
            messagebox.showerror("エラー", f"ポリゴンの読み込み中にエラーが発生しました: {e}")

    def load_colors_from_db(self, db_name):
        self.db_name = os.path.join(self.db_folder, db_name)
        # self.create_table(self.db_name)
        # self.load_grid_shape()
        self.load_grid_colors_not_outline()
        messagebox.showinfo("読み込み完了", "データを読み込みました。")