import tkinter as tk
from tkinter import ttk
import svg_plotter

class CoilParameterGUI:
    def __init__(self, master, update_callback):
        self.master = master
        self.update_callback = update_callback
        self.master.title("Coil Parameter Input")

        self.defaults = {
            "Turns": 9,
            "Diameter": 40,
            "Width between traces": 0.15,
            "Trace Width": 0.9,
            "Layers": 1,
            "PCB Thickness": 0.6,
            "Copper Thickness": 0.035,
            "Shape": 'square',
            "Formula": 'cur_sheet',
            "loop_enabled": False,
            "loop_diameter": 0.0,
            "loop_shape": 'circle'
        }
        self.shapes = ['square', 'hexagon', 'octagon', 'circle']
        self.formulas = ['wheeler', 'monomial', 'cur_sheet']

        self.create_widgets()

    def create_widgets(self):
        self.param_labels = [
            "Turns", "Diameter", "Width between traces", "Trace Width",
            "Layers", "PCB Thickness", "Copper Thickness",
            "Shape", "Formula"
        ]
        self.param_entries = []

        for idx, label in enumerate(self.param_labels):
            tk.Label(self.master, text=label).grid(row=idx, column=0)
            if label in ["Shape", "Formula"]:
                values = self.shapes if label == "Shape" else self.formulas
                combobox = ttk.Combobox(self.master, values=values, state='readonly')
                combobox.set(self.defaults[label])
                combobox.grid(row=idx, column=1)
                self.param_entries.append(combobox)
            else:
                entry = tk.Entry(self.master)
                entry.grid(row=idx, column=1)
                entry.insert(0, self.defaults[label])
                self.param_entries.append(entry)

        self.loop_var = tk.BooleanVar()
        self.loop_check = tk.Checkbutton(self.master, text="Enable Loop Antenna", variable=self.loop_var, command=self.update_loop_diameter)
        self.loop_check.grid(row=len(self.param_labels), column=0, columnspan=2)

        self.loop_diameter_label = tk.Label(self.master, text="Loop Antenna Diameter")
        self.loop_diameter_entry = tk.Entry(self.master)
        self.loop_diameter_label.grid(row=len(self.param_labels) + 1, column=0)
        self.loop_diameter_entry.grid(row=len(self.param_labels) + 1, column=1)
        self.update_loop_diameter()

        self.submit_button = tk.Button(self.master, text="Submit", command=self.submit)
        self.submit_button.grid(row=len(self.param_labels) + 2, columnspan=2)

        self.generate_svg_button = tk.Button(self.master, text="Generate SVG", command=self.generate_svg)
        self.generate_svg_button.grid(row=len(self.param_labels) + 3, columnspan=2)

    def update_loop_diameter(self):
        if self.loop_var.get():
            self.loop_diameter_label.config(state='normal')
            self.loop_diameter_entry.config(state='normal')
        else:
            self.loop_diameter_label.config(state='disabled')
            self.loop_diameter_entry.config(state='disabled')

    def submit(self):
        self.params = {label: entry.get() for label, entry in zip(self.param_labels, self.param_entries)}
        self.params['loop_enabled'] = self.loop_var.get()
        self.params['loop_diameter'] = self.loop_diameter_entry.get() if self.loop_var.get() else 0.0
        self.update_callback(self.params)

    def generate_svg(self):
        svg_plotter.initialize_svg_generation()

def update_coil_params(params):
    print("Updated coil parameters:", params)

if __name__ == "__main__":
    root = tk.Tk()
    gui = CoilParameterGUI(root, update_coil_params)
    root.mainloop()
