import sys
sys.path.append('/Users/cdl/Desktop/VScode_workspace/ga_generativeshop')

import tkinter as tk
from tkinter import messagebox
import os
from GUI.polygon_saver import Saver  # Saverクラスをインポート

class LoadDatabaseDialog:
    def __init__(self, root, saver):
        self.root = root
        self.saver = saver
        self.db_folder = saver.db_folder

    def show(self):
        # データベースファイル一覧を取得
        db_files = [f for f in os.listdir(self.db_folder) if f.endswith(".db")]

        # .dbファイルがなければメッセージを表示
        if not db_files:
            messagebox.showinfo("情報", "ロード可能なデータベースが見つかりません。")
            return

        # 新しいウィンドウを作成
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.title("データベースを選択")
        self.selection_window.geometry("300x250")

        # データベースファイルをリストボックスに表示
        self.listbox = tk.Listbox(self.selection_window, selectmode=tk.SINGLE, width=40, height=10)
        for db_file in db_files:
            self.listbox.insert(tk.END, db_file)
        self.listbox.pack(pady=10)

        # 選択ボタンの作成
        select_button = tk.Button(self.selection_window, text="選択", command=self.on_select)
        select_button.pack(pady=5)

    def on_select(self):
        # 選択されたデータベースファイルをロード
        selected_index = self.listbox.curselection()
        if not selected_index:
            messagebox.showwarning("警告", "データベースを選択してください。")
            return

        db_name = self.listbox.get(selected_index)
        full_path = os.path.join(self.db_folder, db_name)

        # Saverクラスのメソッドを使ってデータベースをロード
        self.saver.db_name = full_path
        self.saver.create_table(self.saver.db_name)  # テーブルがなければ作成
        # 現在の表示をクリア
        # self.saver.clear_grid()
        self.saver.load_grid_shape()  # ポリゴンの座標を読み込み
        self.saver.load_grid_colors()  # セルの色を読み込み

        # 選択ウィンドウを閉じて、読み込み完了のメッセージを表示
        self.selection_window.destroy()
        messagebox.showinfo("読み込み完了", f"{db_name} からデータを読み込みました。")

    def show_outer_polygon(self):
        # データベースファイル一覧を取得
        db_files = [f for f in os.listdir(self.db_folder) if f.endswith(".db")]

        # .dbファイルがなければメッセージを表示
        if not db_files:
            messagebox.showinfo("情報", "ロード可能なデータベースが見つかりません。")
            return

        # 新しいウィンドウを作成
        self.selection_window = tk.Toplevel(self.root)
        self.selection_window.title("データベースを選択")
        self.selection_window.geometry("300x250")

        # データベースファイルをリストボックスに表示
        self.listbox = tk.Listbox(self.selection_window, selectmode=tk.SINGLE, width=40, height=10)
        for db_file in db_files:
            self.listbox.insert(tk.END, db_file)
        self.listbox.pack(pady=10)

        # 選択ボタンの作成
        select_button = tk.Button(self.selection_window, text="選択", command=self.get_outer_polygon)
        select_button.pack(pady=5)

        # 外部のイベントループを実行してウィンドウが閉じられるのを待つ
        self.root.wait_window(self.selection_window)
        return self.outer_polygon, self.db_name

    def get_outer_polygon(self):
        # 選択されたデータベースファイルをロード
        selected_index = self.listbox.curselection()
        if not selected_index:
            messagebox.showwarning("警告", "データベースを選択してください。")
            return

        self.db_name = self.listbox.get(selected_index)
        full_path = os.path.join(self.db_folder, self.db_name)

        # Saverクラスのメソッドを使ってデータベースをロード
        self.saver.db_name = full_path
        self.saver.create_table(self.saver.db_name)  # テーブルがなければ作成
        self.outer_polygon = self.saver.load_outer_polygon()  # ポリゴンの座標を読み込み

        # 選択ウィンドウを閉じて、読み込み完了のメッセージを表示
        self.selection_window.destroy()
        # messagebox.showinfo("読み込み完了", f"{db_name} からデータを読み込みました。")

