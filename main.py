import tkinter as tk
from tkinter import messagebox
import GUI

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Menu")
        self.root.geometry("400x300")
        self.root.config(bg="#2C2F33")  # 落ち着いたダークグレーの背景

        # ボタンのフレームを中央に配置
        button_frame = tk.Frame(root, bg="#2C2F33")
        button_frame.place(relx=0.5, rely=0.5, anchor="center")

        # スタイル設定
        button_style = {
            "font": ("Helvetica", 16, "bold"),
            "width": 12,
            "height": 2,
            "bd": 0,
            "relief": "solid",
            "fg": "black",  # 文字色を黒
            "activeforeground": "#FFFFFF"  # 押された時の文字色も白
        }

        # 作るボタン
        create_button = tk.Button(
            button_frame, text="作る", bg="#4CAF50", activebackground="#66BB6A",  # 作成系のグリーン
            command=self.open_create_screen, **button_style
        )
        create_button.grid(row=0, column=0, pady=10)

        # 編集するボタン
        edit_button = tk.Button(
            button_frame, text="編集する", bg="#FF7043", activebackground="#FF8A65",  # 編集系のオレンジ
            command=self.open_edit_screen, **button_style
        )
        edit_button.grid(row=1, column=0, pady=10)

    def open_create_screen(self):
        # 「作る」ボタンでBuildingShapeGUIを開く
        new_window = tk.Tk()
        app = GUI.building_shape_gui.BuildingShapeGUI(new_window)
        new_window.mainloop()

    def open_edit_screen(self):
        # 「編集する」ボタンでデータをロード
        try:
            GUI.polygon_saver.Saver.load_from_db(self.root)
        except AttributeError:
            messagebox.showerror("Error", "ロードに失敗しました。")

if __name__ == "__main__":
    root = tk.Tk()
    main_menu = MainMenu(root)
    root.mainloop()
