import tkinter as tk
from tkinter import messagebox
import numpy as np

import GUI

if __name__ == "__main__":
    root = tk.Tk()
    app = GUI.building_shape_gui.BuildingShapeGUI(root)
    root.mainloop()