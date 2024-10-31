import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3
import os

class Saver:
    def __init__(self, app):
        self.app = app  # PolygonGridAppインスタンスへの参照を保持
        # スクリプトの存在場所から見て ../dbfiles ディレクトリを指定
        self.db_folder = os.path.join(os.path.dirname(__file__), "../dbfiles")
        os.makedirs(self.db_folder, exist_ok=True)  # フォルダが存在しない場合は作成
        self.db_name = os.path.join(self.db_folder, "default_grid_colors.db")  # デフォルトのデータベース名

    def create_table(self, db_name):
        # 指定されたデータベース名で接続し、テーブルを作成
        self.conn = sqlite3.connect(db_name)
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS cell_colors (
                          x INTEGER,
                          y INTEGER,
                          color TEXT,
                          PRIMARY KEY (x, y))''')
        self.conn.commit()

    def save_cell_color(self, x, y, color):
        # セルの色をデータベースに保存
        cursor = self.conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO cell_colors (x, y, color)
                          VALUES (?, ?, ?)''', (x, y, color))
        self.conn.commit()

    def save_with_name(self):
        # ユーザーにデータベース名を入力させて保存
        db_name = simpledialog.askstring("保存", "データベース名を入力してください（例: grid_colors.db）:")
        if db_name:
            self.db_path = os.path.join(self.db_folder, db_name) if db_name.endswith(".db") else os.path.join(self.db_folder, f"{db_name}.db")
            self.create_table(self.db_path)
            # 現在のセルの状態をすべてデータベースに保存
            for cell, color in self.app.cell_colors.items():
                x1, y1, x2, y2 = self.app.canvas.coords(cell)
                x, y = int(x1), int(y1)
                self.save_cell_color(x, y, color)
            messagebox.showinfo("保存完了", f"{db_name} を保存しました。")

    def load_from_db(self):
        # ../dbfiles ディレクトリの .db ファイルをリストアップ
        db_files = [f for f in os.listdir(self.db_folder) if f.endswith(".db")]

        # .db ファイルがなければメッセージを表示
        if not db_files:
            messagebox.showinfo("情報", "ロード可能なデータベースが見つかりません。")
            return

        # 選択用の新しいウィンドウを作成
        selection_window = tk.Toplevel(self.app.root)
        selection_window.title("データベースを選択")
        selection_window.geometry("300x250")

        # データベースファイルをリストボックスに表示
        listbox = tk.Listbox(selection_window, selectmode=tk.SINGLE, width=40, height=10)
        for db_file in db_files:
            listbox.insert(tk.END, db_file)
        listbox.pack(pady=10)

        # 選択ボタンのコールバック関数
        def on_select():
            selected_index = listbox.curselection()
            if not selected_index:
                messagebox.showwarning("警告", "データベースを選択してください。")
                return

            # 選択されたファイル名を取得し、フルパスを構築
            self.db_name = os.path.join(self.db_folder, db_files[selected_index[0]])
            self.create_table(self.db_name)  # テーブルがなければ作成
            self.load_grid_colors()  # データを読み込みキャンバスに反映
            selection_window.destroy()
            messagebox.showinfo("読み込み完了","データを読み込みました。")
            # messagebox.showinfo("読み込み完了", f"{self.db_name} からデータを読み込みました。")

        # 選択ボタンの作成
        select_button = tk.Button(selection_window, text="選択", command=on_select)
        select_button.pack(pady=5)

    def load_grid_colors(self):
        # データベースからセルの色を読み込んで復元
        conn = sqlite3.connect(self.db_name)  # 修正：self.db_nameを使用
        cursor = conn.cursor()
        cursor.execute("SELECT x, y, color FROM cell_colors")
        for row in cursor.fetchall():
            x, y, color = row
            cell = self.app.canvas.find_closest(x, y)
            self.app.canvas.itemconfig(cell, fill=color)
            self.app.cell_colors[cell] = color
        conn.close()
