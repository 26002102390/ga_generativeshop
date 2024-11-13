import tkinter as tk
from tkinter import messagebox
import GUI
import GUI.database_loader
from PIL import ImageGrab,Image

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Menu")
        self.root.geometry("400x300")
        self.root.config(bg="#2C2F33")  # ダークグレーの背景

        self.saver = GUI.polygon_saver.Saver(self)

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
            button_frame, text="GAを実行する", bg="#FF7043", activebackground="#FF8A65",  # 編集系のオレンジ
            command=self.open_edit_screen, **button_style
        )
        edit_button.grid(row=1, column=0, pady=10)

    def open_create_screen(self):
        # 「作る」ボタンでBuildingShapeGUIを開く
        new_window = tk.Tk()
        app = GUI.building_shape_gui.BuildingShapeGUI(new_window)
        new_window.mainloop()

    def open_edit_screen(self):
        def open_load_dialog(self):
            # LoadDatabaseDialogを開いてロード処理を行う
            load_dialog = GUI.database_loader.LoadDatabaseDialog(self.root, self.saver)
            self.polygon_information = load_dialog.show_outer_polygon()
            self.outer_polygon = self.polygon_information[0]
            self.db_name = self.polygon_information[1]

        open_load_dialog(self)

        # 「GAを実行する」ボタンでPolygonGridAppを開く
        root = tk.Tk()
        root.config(bg="grey")
        self.app = GUI.polygon_grid_gui.PolygonGridApp_ga(root, self.outer_polygon)
        self.app.canvas.config(bg="grey")
        self.saver = GUI.polygon_saver.Saver(self.app)

        # 「GAを実行する」ボタンでデータをロード
        try:
            GUI.polygon_saver.Saver.load_colors_from_db(self.saver, self.db_name)
        except AttributeError:
            tk.messagebox.showerror("Error", "ロードに失敗しました。")
if __name__ == "__main__":
    root = tk.Tk()
    main_menu = MainMenu(root)
    root.mainloop()
