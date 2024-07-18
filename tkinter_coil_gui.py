import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PCBcoilV2 import update_coil_params
import pcbnew_exporter

class CoilParameterGUI:
    def __init__(self, master, update_callback):
        self.master = master
        self.update_callback = update_callback
        self.master.title("Coil and Loop Antenna Designer")

        self.main_frame = ttk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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

        # Initialize the variables for comboboxes
        self.shape_var = tk.StringVar(value=self.shapes[0])  # Default to the first shape
        self.formula_var = tk.StringVar(value=self.formulas[0])  # Default to the first formula
        self.loop_shape_var = tk.StringVar(value='Loop Antenna with Pads')  # Default loop shape
        self.square_calc_var = tk.BooleanVar(value=False)  # Assuming it's a boolean, adjust as necessary

        self.create_parameters_section()
        self.create_export_section()
        self.create_update_button()

    def create_parameters_section(self):
        # Parameters Section
        ttk.Label(self.main_frame, text="Parameters", font=('TkDefaultFont', 14, 'bold')).grid(row=0, columnspan=4, sticky='w')

        # Coil Parameters
        self.create_coil_widgets()

        # Loop Parameters in a new row
        self.create_loop_widgets()

    def create_coil_widgets(self):
        ttk.Label(self.main_frame, text="Coil", font=('TkDefaultFont', 12, 'bold')).grid(row=1, columnspan=2, sticky='w')
        self.param_labels = [
            "Turns", "Diameter", "Width between traces", "Trace Width", "Layers",
            "PCB Thickness", "Copper Thickness", "Shape", "Formula"
        ]
        self.param_entries = []

        for idx, label in enumerate(self.param_labels):
            tk.Label(self.main_frame, text=label).grid(row=idx+1, column=0, sticky='w')
            if label in ["Shape", "Formula"]:
                combobox = ttk.Combobox(self.main_frame, textvariable=getattr(self, f"{label.lower()}_var"), values=getattr(self, f"{label.lower()}s"), width=28, state='readonly')
                combobox.grid(row=idx+1, column=1, sticky='ew')
                self.param_entries.append(combobox)
            else:
                entry = tk.Entry(self.main_frame, width=30)
                entry.grid(row=idx+1, column=1, sticky='ew')
                entry.insert(0, str(self.defaults.get(label, '')))
                self.param_entries.append(entry)
                setattr(self, f"{label.lower().replace(' ', '_')}_entry", entry)

        self.main_frame.columnconfigure(1, weight=1)

    def create_loop_widgets(self):
        ttk.Label(self.main_frame, text="Loop", font=('TkDefaultFont', 12, 'bold')).grid(row=12, columnspan=2, sticky='w')
        self.loop_shape_label = tk.Label(self.main_frame, text="Loop Antenna Shape")
        self.loop_shape_combobox = ttk.Combobox(self.main_frame, textvariable=self.loop_shape_var, values=['Loop Antenna with Pads', 'Loop Antenna with Pads 2 Layer'], width=28, state='readonly')
        self.loop_shape_label.grid(row=13, column=0, sticky='w')
        self.loop_shape_combobox.grid(row=13, column=1, sticky='ew')

        self.main_frame.columnconfigure(1, weight=1)

    def create_export_section(self):
        # Export Section
        ttk.Label(self.main_frame, text="Export", font=('TkDefaultFont', 14, 'bold')).grid(row=20, columnspan=4, sticky='w')

        # Files Subsection
        ttk.Label(self.main_frame, text="Files", font=('TkDefaultFont', 10, 'bold')).grid(row=21, column=0, columnspan=2, sticky='w')
        self.export_options = {
            'SVG': tk.BooleanVar(value=False),
            'Gerber': tk.BooleanVar(value=True),
            'DXF': tk.BooleanVar(value=False)
        }
        tk.Checkbutton(self.main_frame, text="SVG", variable=self.export_options['SVG']).grid(row=22, column=0, sticky='w')
        tk.Checkbutton(self.main_frame, text="Gerber", variable=self.export_options['Gerber']).grid(row=23, column=0, sticky='w')
        tk.Checkbutton(self.main_frame, text="DXF", variable=self.export_options['DXF']).grid(row=24, column=0, sticky='w')

        # Type Subsection
        ttk.Label(self.main_frame, text="Type", font=('TkDefaultFont', 10, 'bold')).grid(row=21, column=1, sticky='w')
        self.export_coil_var = tk.BooleanVar(value=False)
        self.export_loop_var = tk.BooleanVar(value=False)
        tk.Checkbutton(self.main_frame, text="Export Coil", variable=self.export_coil_var).grid(row=22, column=1, padx=5, pady=5, sticky='w')
        tk.Checkbutton(self.main_frame, text="Export Loop", variable=self.export_loop_var).grid(row=23, column=1, padx=5, pady=5, sticky='w')

    def create_update_button(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=30, columnspan=4, pady=10)
        ttk.Button(button_frame, text="Update", command=self.submit, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export", command=self.export, width=20).pack(side=tk.RIGHT, padx=5)

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
                "loop_shape": self.loop_shape_var.get(),
                "square_calc": self.square_calc_var.get()
            }
            coil = self.update_callback(self.params)
            return coil
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def export(self):
        if self.export_coil_var.get():
            self.export_coil()
        if self.export_loop_var.get():
            self.export_loop()

    def export_coil(self):
        if self.submit():
            coil = self.update_callback(self.params)
            coil_line_list = coil.renderAsCoordinateList()
            pcbnew_exporter.export_coil(coil, coil_line_list, self.export_options)

    def export_loop(self):
        if self.submit():
            coil = self.update_callback(self.params)
            loop_line_list = coil.render_loop_antenna()

            # Determine the loop type based on the selected option
            loop_shape = self.loop_shape_var.get()
            loop_with_pads = loop_shape == 'Loop Antenna with Pads'
            loop_with_pads_2_layer = loop_shape == 'Loop Antenna with Pads 2 Layer'
            
            # Pass the flags to the exporter to handle specific export logic for pads
            pcbnew_exporter.export_loop(coil, loop_line_list, self.export_options, 
                                        loop_with_pads=loop_with_pads, 
                                        loop_with_pads_2_layer=loop_with_pads_2_layer,
                                        loop_shape=loop_shape)


def main():
    import tkinter as tk
    from tkinter_coil_gui import CoilParameterGUI

    root = tk.Tk()
    root.geometry("400x600")  # Adjust the size as needed
    app = CoilParameterGUI(root, update_coil_params)
    root.mainloop()


if __name__ == "__main__":
    main()