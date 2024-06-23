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
            "Width between traces": 0.15,
            "Trace Width": 0.9,
            "Layers": 1,
            "PCB Thickness": 0.6,
            "Copper Thickness": 0.030,
            "Shape": 'square',
            "Formula": 'cur_sheet',
            "loop_enabled": False,
            "loop_diameter": 0.0
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
                entry.insert(0, str(self.defaults[label]))
                self.param_entries.append(entry)

        # Define current_row_index for the new elements
        current_row_index = len(self.param_labels)

        # Add checkbox for loop antenna
        self.loop_var = tk.BooleanVar()
        self.loop_check = tk.Checkbutton(self.master, text="Enable Loop Antenna", variable=self.loop_var, command=self.update_loop_diameter)
        self.loop_check.grid(row=current_row_index, column=0, columnspan=2, sticky=tk.W)
        current_row_index += 1  # Increment row index

        # Add entry for loop antenna diameter
        self.loop_diameter_label = tk.Label(self.master, text="Loop Antenna Diameter")
        self.loop_diameter_entry = tk.Entry(self.master, state='disabled')
        self.loop_diameter_label.grid(row=current_row_index, column=0)
        self.loop_diameter_entry.grid(row=current_row_index, column=1)
        current_row_index += 1  # Increment row index

        # Loop shape selection
        self.loop_shape_var = tk.StringVar(value='circle')
        self.loop_shape_label = tk.Label(self.master, text="Loop Antenna Shape")
        self.loop_shape_combobox = ttk.Combobox(self.master, textvariable=self.loop_shape_var, values=['circle', 'square', 'hexagon'], state='readonly')
        self.loop_shape_combobox.grid(row=current_row_index, column=1)
        self.loop_shape_label.grid(row=current_row_index, column=0)
        current_row_index += 1  # Increment row index

        self.submit_button = tk.Button(self.master, text="Submit", command=self.submit)
        self.submit_button.grid(row=current_row_index, columnspan=2)

    def update_loop_diameter(self):
        if self.loop_var.get():
            self.loop_diameter_entry.config(state='normal')
        else:
            self.loop_diameter_entry.config(state='disabled')

    def submit(self):
        self.params = {label: entry.get() for label, entry in zip(self.param_labels, self.param_entries)}
        self.params['loop_enabled'] = self.loop_var.get()
        loop_diameter_input = self.loop_diameter_entry.get().strip()
        if self.loop_var.get() and loop_diameter_input:
            try:
                self.params['loop_diameter'] = float(loop_diameter_input)
            except ValueError:
                raise ValueError("Invalid input for loop diameter. Please enter a numeric value.")
        else:
            self.params['loop_diameter'] = 0.0
        self.params['loop_shape'] = self.loop_shape_var.get()  # Ensure this is captured correctly
        print("Submitted parameters:", self.params)  # Debugging print
        self.update_callback(self.params)


    def get_params(self):
        return {label: entry.get() for label, entry in zip(self.param_labels, self.param_entries)}


# For testing purposes
if __name__ == "__main__":
    def print_params(params):
        print(params)

    root = tk.Tk()
    gui = CoilParameterGUI(root, print_params)
    root.mainloop()
