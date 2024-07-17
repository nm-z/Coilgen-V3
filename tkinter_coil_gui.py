import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PCBcoilV2 import update_coil_params
import pcbnew_exporter

class CoilParameterGUI:
    def __init__(self, master, update_callback):
        self.master = master
        self.update_callback = update_callback
        self.master.title("Coil and Loop Antenna Designer")

        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.coil_frame = ttk.Frame(self.notebook)
        self.loop_frame = ttk.Frame(self.notebook)
        self.export_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.coil_frame, text='Coil', sticky='nsew')
        self.notebook.add(self.loop_frame, text='Loop Antenna', sticky='nsew')
        self.notebook.add(self.export_frame, text='Export', sticky='nsew')

        self.shapes = ['square', 'hexagon', 'octagon', 'circle']
        self.formulas = ['cur_sheet', 'monomial', 'wheeler']
        self.defaults = {
            "Turns": 4,
            "Diameter": 10,
            "Width between traces": 0.5,
            "Trace Width": 0.5,
            "Layers": 1,
            "PCB Thickness": 0.6,
            "Copper Thickness": 0.035
        }

        self.create_coil_widgets()
        self.create_loop_widgets()
        self.create_export_widgets()
        self.create_update_button()

        # Set both coil and loop to always be enabled
        self.coil_enabled = tk.BooleanVar(value=True)
        self.loop_enabled = tk.BooleanVar(value=True)

    def create_coil_widgets(self):
        self.param_labels = [
            "Turns", "Diameter", "Width between traces", "Trace Width", "Layers",
            "PCB Thickness", "Copper Thickness", "Shape", "Formula", "Square Calculation"
        ]
        self.param_entries = []

        for idx, label in enumerate(self.param_labels):
            tk.Label(self.coil_frame, text=label).grid(row=idx, column=0, sticky='w')
            if label == "Shape":
                self.shape_var = tk.StringVar(value='square')
                combobox = ttk.Combobox(self.coil_frame, textvariable=self.shape_var, values=self.shapes, state='readonly')
                combobox.grid(row=idx, column=1, sticky='ew')
                self.param_entries.append(combobox)
            elif label == "Formula":
                self.formula_var = tk.StringVar(value='wheeler')
                combobox = ttk.Combobox(self.coil_frame, textvariable=self.formula_var, values=self.formulas, state='readonly')
                combobox.grid(row=idx, column=1, sticky='ew')
                self.param_entries.append(combobox)
            elif label == "Square Calculation":
                self.square_calc_var = tk.StringVar(value='Planar inductor')
                combobox = ttk.Combobox(self.coil_frame, textvariable=self.square_calc_var, values=['Planar inductor', 'thijses/PCBcoilGenerator'], state='readonly')
                combobox.grid(row=idx, column=1, sticky='ew')
                self.param_entries.append(combobox)
            else:
                entry = tk.Entry(self.coil_frame)
                entry.grid(row=idx, column=1, sticky='ew')
                entry.insert(0, str(self.defaults.get(label, '')))
                self.param_entries.append(entry)
                setattr(self, f"{label.lower().replace(' ', '_')}_entry", entry)

        self.coil_frame.columnconfigure(1, weight=1)

    def create_loop_widgets(self):
        self.loop_shape_var = tk.StringVar(value='Loop Antenna with Pads')
        self.loop_shape_label = tk.Label(self.loop_frame, text="Loop Antenna Shape")
        self.loop_shape_combobox = ttk.Combobox(self.loop_frame, textvariable=self.loop_shape_var, values=['Loop Antenna with Pads', 'Loop Antenna with Pads 2 Layer', 'circle', 'square'], state='readonly')
        self.loop_shape_combobox.grid(row=0, column=1, sticky='ew')
        self.loop_shape_label.grid(row=0, column=0, sticky='w')

        self.loop_diameter_label = tk.Label(self.loop_frame, text="Loop Antenna Diameter")
        self.loop_diameter_entry = tk.Entry(self.loop_frame)
        self.loop_diameter_label.grid(row=1, column=0, sticky='w')
        self.loop_diameter_entry.grid(row=1, column=1, sticky='ew')
        self.loop_diameter_entry.insert(0, "20")

        self.loop_frame.columnconfigure(1, weight=1)

    def create_export_widgets(self):
        self.export_options = {
            'SVG': tk.BooleanVar(value=False),
            'Gerber': tk.BooleanVar(value=True),
            'DXF': tk.BooleanVar(value=False)
        }

        for idx, (option, var) in enumerate(self.export_options.items()):
            tk.Checkbutton(self.export_frame, text=option, variable=var).grid(row=idx, column=0, sticky='w')

        self.export_coil_button = tk.Button(self.export_frame, text="Export Coil", command=self.export_coil)
        self.export_coil_button.grid(row=len(self.export_options), column=0, pady=5)

        self.export_loop_button = tk.Button(self.export_frame, text="Export Loop", command=self.export_loop)
        self.export_loop_button.grid(row=len(self.export_options), column=1, pady=5)

    def create_update_button(self):
        self.update_button = tk.Button(self.master, text="Update", command=self.submit, width=20, height=2)
        self.update_button.pack(side=tk.BOTTOM, pady=10)

    def submit(self):
        try:
            self.params = {
                "Turns": int(self.turns_entry.get()),
                "Diameter": float(self.diameter_entry.get()),
                "Width between traces": float(self.width_between_traces_entry.get()),
                "Trace Width": float(self.trace_width_entry.get()),
                "Layers": int(self.layers_entry.get()),
                "PCB Thickness": float(self.pcb_thickness_entry.get()),
                "Copper Thickness": float(self.copper_thickness_entry.get()),
                "Shape": self.shape_var.get(),
                "Formula": self.formula_var.get(),
                "loop_enabled": True,
                "loop_diameter": float(self.loop_diameter_entry.get()),
                "loop_shape": self.loop_shape_var.get(),
                "square_calc": self.square_calc_var.get()
            }
            coil = self.update_callback(self.params)

            # Print to console


            return coil
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def export_coil(self):
        self.submit()
        coil = self.update_callback(self.params)
        coil_line_list = coil.renderAsCoordinateList()
        pcbnew_exporter.export_coil(coil, coil_line_list, self.export_options)

    def export_loop(self):
        self.submit()  # Collect all parameters from the GUI
        coil = self.update_callback(self.params)  # Update the coil parameters based on GUI input
        loop_line_list = coil.render_loop_antenna()  # Generate the loop line list based on the current settings

        # Check if the loop shape is one of the pad-enabled types
        loop_with_pads = self.loop_shape_var.get() == 'Loop Antenna with Pads'
        loop_with_pads_2_layer = self.loop_shape_var.get() == 'Loop Antenna with Pads 2 Layer'
        
        # Pass the flags to the exporter to handle specific export logic for pads
        pcbnew_exporter.export_loop(coil, loop_line_list, self.export_options, loop_with_pads=loop_with_pads, loop_with_pads_2_layer=loop_with_pads_2_layer)


def main():
    import tkinter as tk
    from tkinter_coil_gui import CoilParameterGUI

    root = tk.Tk()
    root.geometry("400x600")  # Adjust the size as needed
    app = CoilParameterGUI(root, update_coil_params)
    root.mainloop()


if __name__ == "__main__":
    main()