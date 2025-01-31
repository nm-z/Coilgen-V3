import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PCBcoilV2 import update_coil_params
import pcbnew_exporter
from tkinter import StringVar, DoubleVar, Radiobutton
import logging

# At the top of the file, after the imports
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
            "Turns": 10,
            "Diameter": 20,
            "Width between traces": 0.5,
            "Trace Width": 0.5,
            "Layers": 1,
            "PCB Thickness": 0.5,
            "Copper Thickness": 0.05
        }

        # Initialize the variables for comboboxes
        self.shape_var = tk.StringVar(value=self.shapes[0])  # Default to the first shape
        self.formula_var = tk.StringVar(value=self.formulas[0])  # Default to the first formula
        self.loop_shape_var = tk.StringVar(value='Loop Antenna with Pads 2 Layer')  # Default loop shape
        self.square_calc_var = tk.BooleanVar(value=False)  # Assuming it's a boolean, adjust as necessary

        # In the __init__ method, add these variables
        self.loop_diameter_mode = StringVar(value="Auto")
        self.custom_loop_diameter = DoubleVar(value=0.0)


        self.create_parameters_section()
        self.create_export_section()
        self.create_update_button()
        self.create_resonant_frequency_display()
        self.create_resonant_frequency_input()
        self.create_loop_widgets()

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
        
        # Loop Antenna Shape
        self.loop_shape_label = tk.Label(self.main_frame, text="Loop Antenna Layer")
        self.loop_shape_combobox = ttk.Combobox(self.main_frame, textvariable=self.loop_shape_var, values=['Loop Antenna with Pads', 'Loop Antenna with Pads 2 Layer'], width=28, state='readonly')
        self.loop_shape_label.grid(row=13, column=0, sticky='w')
        self.loop_shape_combobox.grid(row=13, column=1, sticky='ew')

        # Loop Diameter options (directly under the Loop Antenna Shape)
        ttk.Label(self.main_frame, text="Loop Diameter", font=('TkDefaultFont', 10, 'bold')).grid(row=14, column=0, columnspan=2, sticky='w', pady=(10, 0))

        # Radio buttons for Auto and Custom options
        self.auto_radio = Radiobutton(self.main_frame, text="Auto", variable=self.loop_diameter_mode, value="Auto", command=self.toggle_custom_diameter)
        self.auto_radio.grid(row=15, column=0, sticky='w')
        self.custom_radio = Radiobutton(self.main_frame, text="Custom", variable=self.loop_diameter_mode, value="Custom", command=self.toggle_custom_diameter)
        self.custom_radio.grid(row=15, column=1, sticky='w')

        # Custom diameter input
        self.custom_diameter_label = ttk.Label(self.main_frame, text="Custom Diameter (mm):")
        self.custom_diameter_label.grid(row=16, column=0, sticky='w')
        self.custom_diameter_entry = ttk.Entry(self.main_frame, textvariable=self.custom_loop_diameter, width=10)
        self.custom_diameter_entry.grid(row=16, column=1, sticky='w')

        # Initially enable the Loop Diameter options since 2-layer is default
        self.enable_loop_diameter_options()

        # Bind the combobox selection to a method that enables/disables the Loop Diameter options
        self.loop_shape_combobox.bind("<<ComboboxSelected>>", self.on_loop_shape_change)

        self.main_frame.columnconfigure(1, weight=1)

    def disable_loop_diameter_options(self):
        self.auto_radio.config(state='disabled')
        self.custom_radio.config(state='disabled')
        self.custom_diameter_entry.config(state='disabled')

    def enable_loop_diameter_options(self):
        self.auto_radio.config(state='normal')
        self.custom_radio.config(state='normal')
        self.toggle_custom_diameter()  # This will set the correct state for the custom diameter entry

    def on_loop_shape_change(self, event):
        if self.loop_shape_var.get() == 'Loop Antenna with Pads 2 Layer':
            self.enable_loop_diameter_options()
        else:
            self.disable_loop_diameter_options()

    def toggle_custom_diameter(self):
        if self.loop_diameter_mode.get() == "Custom" and self.loop_shape_var.get() == 'Loop Antenna with Pads 2 Layer':
            self.custom_diameter_entry.config(state='normal')
        else:
            self.custom_diameter_entry.config(state='disabled')

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
        self.export_coil_var = tk.BooleanVar(value=True)
        self.export_loop_var = tk.BooleanVar(value=True)
        tk.Checkbutton(self.main_frame, text="Export Coil", variable=self.export_coil_var).grid(row=22, column=1, padx=5, pady=5, sticky='w')
        tk.Checkbutton(self.main_frame, text="Export Loop", variable=self.export_loop_var).grid(row=23, column=1, padx=5, pady=5, sticky='w')

    def create_update_button(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=30, columnspan=4, pady=10)
        ttk.Button(button_frame, text="Update", command=self.submit, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export", command=self.export, width=20).pack(side=tk.RIGHT, padx=5)

    def create_resonant_frequency_display(self):
        # Create a frame for the resonant frequency display
        self.freq_frame = ttk.Frame(self.main_frame)
        self.freq_frame.grid(row=29, columnspan=4, pady=10)

        # The label for the resonant frequency
        self.freq_label = ttk.Label(self.freq_frame, text="Estimated Resonant Frequency: N/A", font=('TkDefaultFont', 12))
        self.freq_label.pack()

    def create_resonant_frequency_input(self):
        # Create a frame for the resonant frequency input
        self.freq_input_frame = ttk.Frame(self.main_frame)
        self.freq_input_frame.grid(row=28, columnspan=4, pady=10)

        # Label for the input
        ttk.Label(self.freq_input_frame, text="Desired Resonant Frequency (MHz):").pack(side=tk.LEFT)

        # Entry for the desired frequency
        self.desired_freq_var = tk.StringVar()
        self.desired_freq_entry = tk.Entry(self.freq_input_frame, textvariable=self.desired_freq_var, width=10)
        self.desired_freq_entry.pack(side=tk.LEFT, padx=5)

        # Button to calculate diameter
        ttk.Button(self.freq_input_frame, text="Calculate Diameter", command=self.calculate_diameter).pack(side=tk.LEFT, padx=5)

    def calculate_diameter(self):
        try:
            desired_freq = float(self.desired_freq_var.get())
            coil = self.submit()
            if coil:
                suggested_diameter, actual_frequency = coil.calculate_diameter_for_frequency(desired_freq)
                self.diameter_entry.delete(0, tk.END)
                self.diameter_entry.insert(0, str(suggested_diameter))
                
                message = (f"Suggested diameter: {suggested_diameter:.2f} mm\n"
                        f"Resulting frequency: {actual_frequency:.6f} MHz\n"
                        f"Desired frequency: {desired_freq:.6f} MHz\n"
                        f"Difference: {abs(actual_frequency - desired_freq):.6f} MHz")
                
                messagebox.showinfo("Suggested Diameter", message)
                
                # Update the coil with the new diameter and recalculate
                self.diameter_entry.delete(0, tk.END)
                self.diameter_entry.insert(0, str(suggested_diameter))
                self.submit()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

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
                "square_calc": self.square_calc_var.get(),
                "loop_diameter_mode": self.loop_diameter_mode.get(),
                "custom_loop_diameter": self.custom_loop_diameter.get() if self.loop_diameter_mode.get() == "Custom" else None
            }
            coil = self.update_callback(self.params)
            
            # Calculate and display the resonant frequency
            resonant_freq = coil.calcResonantFrequency(1e-9)  # Using a dummy capacitance
            self.freq_label.config(text=f"Estimated Resonant Frequency: {resonant_freq:.6f} MHz")
            
            return coil
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        return None
    
    def export(self):
        coil = self.submit()
        if coil:
            loop_shape = self.loop_shape_var.get()
            loop_with_pads = loop_shape == 'Loop Antenna with Pads'
            loop_with_pads_2_layer = loop_shape == 'Loop Antenna with Pads 2 Layer'
            
            export_coil = self.export_coil_var.get()
            export_loop = self.export_loop_var.get()
            
            loop_diameter_mode = self.loop_diameter_mode.get()
            custom_loop_diameter = self.custom_loop_diameter.get() if loop_diameter_mode == "Custom" else None
            
            logging.debug(f"GUI - Loop shape: {loop_shape}")
            logging.debug(f"GUI - Loop diameter mode: {loop_diameter_mode}")
            logging.debug(f"GUI - Custom loop diameter: {custom_loop_diameter}")
            
            try:
                if loop_with_pads:
                    if export_coil and not export_loop:
                        # Only export coil
                        pcbnew_exporter.export_coil(coil, coil.renderAsCoordinateList(), self.export_options)
                    elif not export_coil and export_loop:
                        # Only export loop_with_pads
                        pcbnew_exporter.export_loop(coil, [], self.export_options, loop_with_pads=True, combined=False)
                    elif export_coil and export_loop:
                        # Combined export (loop_with_pads and coil)
                        pcbnew_exporter.export_loop(coil, coil.renderAsCoordinateList(), self.export_options, loop_with_pads=True, combined=True)
                elif loop_with_pads_2_layer:
                    if export_coil:
                        # Only export coil
                        pcbnew_exporter.export_coil(coil, coil.renderAsCoordinateList(), self.export_options)
                    if export_loop:
                        # Only export loop_with_pads_2_layer
                        logging.debug(f"GUI - Calling export_loop with custom_loop_diameter: {custom_loop_diameter}")
                        pcbnew_exporter.export_loop(coil, [], self.export_options, loop_with_pads_2_layer=True, combined=False, loop_diameter_mode=loop_diameter_mode, custom_loop_diameter=custom_loop_diameter)
                    if export_coil and export_loop:
                        # Export coil and loop_with_pads_2_layer separately
                        pcbnew_exporter.export_coil(coil, coil.renderAsCoordinateList(), self.export_options)
                        logging.debug(f"GUI - Calling export_loop with custom_loop_diameter: {custom_loop_diameter}")
                        pcbnew_exporter.export_loop(coil, [], self.export_options, loop_with_pads_2_layer=True, combined=False, loop_diameter_mode=loop_diameter_mode, custom_loop_diameter=custom_loop_diameter)
                else:
                    if export_coil:
                        # Only export coil
                        pcbnew_exporter.export_coil(coil, coil.renderAsCoordinateList(), self.export_options)
            except Exception as e:
                logging.error(f"GUI - Export error: {str(e)}")
                messagebox.showerror("Export Error", f"An error occurred during export: {str(e)}")


def main():
    import tkinter as tk
    from tkinter_coil_gui import CoilParameterGUI

    root = tk.Tk()
    root.geometry("400x600")  # Adjust the size as needed
    app = CoilParameterGUI(root, update_coil_params)
    root.mainloop()


if __name__ == "__main__":
    main()