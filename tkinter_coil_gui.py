import tkinter as tk
from tkinter import ttk

class CoilParameterGUI:
    def __init__(self, master, update_callback):
        self.master = master
        self.update_callback = update_callback
        self.master.title("Coil Parameter Input")

        self.defaults = {
            "Turns": 9,
            "Diameter": 40,
            "Clearance": 0.15,
            "Trace Width": 0.9,
            "Layers": 2,
            "PCB Thickness": 0.6,
            "Copper Thickness": 0.030,
            "Shape": 'circle',
            "Formula": 'cur_sheet'
        }

        self.shapes = ['square', 'hexagon', 'octagon', 'circle']
        self.formulas = ['wheeler', 'monomial', 'cur_sheet']

        self.create_widgets()

    def create_widgets(self):
        self.param_labels = [
            "Turns", "Diameter", "Clearance", "Trace Width",
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
                entry.insert(0, str(self.defaults[label]))
                self.param_entries.append(entry)

        self.submit_button = tk.Button(self.master, text="Submit", command=self.submit)
        self.submit_button.grid(row=len(self.param_labels), columnspan=2)

    def submit(self):
        self.params = [entry.get() for entry in self.param_entries]
        self.update_callback(self.params)

if __name__ == "__main__":
    root = tk.Tk()
    app = CoilParameterGUI(root, lambda x: print("Updated params:", x))
    root.mainloop()
