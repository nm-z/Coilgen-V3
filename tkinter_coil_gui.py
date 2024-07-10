import tkinter as tk
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

        self.create_coil_widgets()
        self.create_loop_widgets()
        self.create_export_widgets()
        self.create_toggle_buttons()

        self.update_button_states()

    def create_toggle_buttons(self):
        self.toggle_frame = tk.Frame(self.master)
        self.toggle_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.coil_enabled = tk.BooleanVar(value=True)
        self.loop_enabled = tk.BooleanVar(value=False)

        self.coil_button = tk.Button(self.toggle_frame, text="Coil ON", command=self.toggle_coil, width=20, height=2)
        self.coil_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))

        self.loop_button = tk.Button(self.toggle_frame, text="Loop OFF", command=self.toggle_loop, width=20, height=2)
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
        self.defaults = {
            "Turns": 9,
            "Diameter": 40,
            "Width between traces": 0.15,
            "Trace Width": 0.9,
            "Shape": 'square'
        }
        self.shapes = ['square', 'hexagon', 'octagon', 'circle']

        self.param_labels = [
            "Turns", "Diameter", "Width between traces", "Trace Width", "Shape"
        ]
        self.param_entries = []

        for idx, label in enumerate(self.param_labels):
            tk.Label(self.coil_frame, text=label).grid(row=idx, column=0, sticky='w')
            if label == "Shape":
                combobox = ttk.Combobox(self.coil_frame, values=self.shapes, state='readonly')
                combobox.set(self.defaults[label])
                combobox.grid(row=idx, column=1, sticky='ew')
                self.param_entries.append(combobox)
            else:
                entry = tk.Entry(self.coil_frame)
                entry.grid(row=idx, column=1, sticky='ew')
                entry.insert(0, self.defaults[label])
                self.param_entries.append(entry)

        self.coil_frame.columnconfigure(1, weight=1)

    def create_loop_widgets(self):
        self.loop_shape_var = tk.StringVar(value='circle')
        self.loop_shape_label = tk.Label(self.loop_frame, text="Loop Antenna Shape")
        self.loop_shape_combobox = ttk.Combobox(self.loop_frame, textvariable=self.loop_shape_var, values=['circle', 'square'], state='readonly')
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
            'SVG': tk.BooleanVar(value=True),
            'Gerber': tk.BooleanVar(value=True),
            'DXF': tk.BooleanVar(value=True),
            'Drill': tk.BooleanVar(value=False)
        }

        for idx, (option, var) in enumerate(self.export_options.items()):
            tk.Checkbutton(self.export_frame, text=option, variable=var).grid(row=idx, column=0, sticky='w')

        self.export_coil_button = tk.Button(self.export_frame, text="Export Coil", command=self.export_coil)
        self.export_coil_button.grid(row=len(self.export_options), column=0, pady=5)

        self.export_loop_button = tk.Button(self.export_frame, text="Export Loop", command=self.export_loop)
        self.export_loop_button.grid(row=len(self.export_options), column=1, pady=5)

    def submit(self):
        self.params = {label: entry.get() for label, entry in zip(self.param_labels, self.param_entries)}
        self.params['coil_enabled'] = self.coil_enabled.get()
        self.params['loop_enabled'] = self.loop_enabled.get()
        self.params['loop_diameter'] = self.loop_diameter_entry.get() if self.loop_enabled.get() else 0.0
        self.params['loop_shape'] = self.loop_shape_var.get() if self.loop_enabled.get() else 'circle'
        self.params['Layers'] = 2 if self.loop_enabled.get() else 1
        self.params['PCB Thickness'] = 0.6  # Default value
        self.params['Copper Thickness'] = 0.035  # Default value
        self.params['Formula'] = 'cur_sheet'  # Default value
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
        
        # Debug print
        print(f"Loop enabled: {self.loop_enabled.get()}")
        print(f"Loop diameter: {self.params['loop_diameter']}")
        print(f"Loop shape: {self.params['loop_shape']}")
        print(f"Loop line list: {loop_line_list}")
        
        pcbnew_exporter.export_loop(coil, loop_line_list, self.export_options)