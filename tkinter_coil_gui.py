import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import ttk, filedialog, messagebox
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
        self.formulas = ['cur_sheet', 'Mohan', 'Jenei', 'Zhao']

        self.defaults = {
            "Turns": 9,
            "Diameter": 40,
            "Width between traces": 0.15,
            "Trace Width": 0.9,
            "Layers": 1,
            "PCB Thickness": 0.6,
            "Copper Thickness": 0.030
        }

        self.create_coil_widgets()
        self.create_loop_widgets()
        self.create_export_widgets()
        self.create_toggle_buttons()

        self.update_button_states()

    def create_toggle_buttons(self):
        self.toggle_frame = tk.Frame(self.master)
        self.toggle_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.coil_enabled = tk.BooleanVar(value=False)
        self.loop_enabled = tk.BooleanVar(value=True)

        self.coil_button = tk.Button(self.toggle_frame, text="Coil OFF", command=self.toggle_coil, width=20, height=2)
        self.coil_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.loop_button = tk.Button(self.toggle_frame, text="Loop ON", command=self.toggle_loop, width=20, height=2)
        self.loop_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))

        self.update_button = tk.Button(self.toggle_frame, text="Update", command=self.submit, width=20, height=2)
        self.update_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(5, 0))

        self.update_button_states()

    def toggle_coil(self):
        self.coil_enabled.set(not self.coil_enabled.get())
        if not self.coil_enabled.get() and not self.loop_enabled.get():
            self.loop_enabled.set(True)
        self.update_button_states()
        self.submit()

    def toggle_loop(self):
        self.loop_enabled.set(not self.loop_enabled.get())
        if not self.coil_enabled.get() and not self.loop_enabled.get():
            self.coil_enabled.set(True)
        self.update_button_states()
        self.submit()

    def update_button_states(self):
        self.coil_button.config(text="Coil ON" if self.coil_enabled.get() else "Coil OFF",
                                bg="green" if self.coil_enabled.get() else "red")
        self.loop_button.config(text="Loop ON" if self.loop_enabled.get() else "Loop OFF",
                                bg="green" if self.loop_enabled.get() else "red")
        self.update_widget_states()

    def update_widget_states(self):
        coil_state = 'normal' if self.coil_enabled.get() else 'disabled'
        loop_state = 'normal' if self.loop_enabled.get() else 'disabled'
        
        for widget in self.coil_frame.winfo_children():
            if isinstance(widget, (tk.Entry, ttk.Combobox, tk.Button)):
                widget.config(state=coil_state)
        
        for widget in self.loop_frame.winfo_children():
            if isinstance(widget, (tk.Entry, ttk.Combobox, tk.Button)):
                widget.config(state=loop_state)

    def create_coil_widgets(self):
        self.param_labels = [
            "Turns", "Diameter", "Width between traces", "Trace Width", "Layers",
            "PCB Thickness", "Copper Thickness", "Shape", "Formula"
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
                self.formula_var = tk.StringVar(value='cur_sheet')
                combobox = ttk.Combobox(self.coil_frame, textvariable=self.formula_var, values=self.formulas, state='readonly')
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
        self.loop_shape_combobox = ttk.Combobox(self.loop_frame, textvariable=self.loop_shape_var, values=['Loop Antenna with Pads', 'circle', 'square'], state='readonly')
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

    def submit(self):
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
            "loop_enabled": self.loop_enabled.get(),
            "loop_diameter": float(self.loop_diameter_entry.get()),
            "loop_shape": self.loop_shape_var.get()  # Pass the loop shape
        }
        coil = self.update_callback(self.params)
        return coil

    def export_coil(self):
        if not self.coil_enabled.get():
            tk.messagebox.showerror("Error", "Coil must be enabled to export.")
            return
        self.submit()
        coil = self.update_callback(self.params)
        coil_line_list = coil.renderAsCoordinateList()
        pcbnew_exporter.export_coil(coil, coil_line_list, self.export_options)

    def export_loop(self):
        if not self.loop_enabled.get():
            tk.messagebox.showerror("Error", "Loop must be enabled to export.")
            return
        self.submit()
        coil = self.update_callback(self.params)
        loop_line_list = coil.render_loop_antenna()
        loop_with_pads = self.loop_shape_var.get() == 'Loop Antenna with Pads'
        pcbnew_exporter.export_loop(coil, loop_line_list, self.export_options, loop_with_pads=loop_with_pads)