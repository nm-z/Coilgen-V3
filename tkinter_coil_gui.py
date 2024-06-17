import tkinter as tk
from tkinter import ttk
from PCBcoilV2 import coilClass, shapes  # Make sure PCBcoilV2.py is in the same directory or properly referenced
from tkinter import Tk



class CoilUpdater:
     def __init__(self, master, shared_data=None):
          self.master = master
          self.master.title("Coil Parameter Updater")

          self.coil = coilClass(turns=10, diam=50, clearance=0.1, traceWidth=0.5, shape=shapes['circle'])
          self.shared_data = shared_data
          # Layout configuration
          ttk.Label(self.master, text="Turns:").grid(row=0, column=0, padx=10, pady=10)
          self.turns_var = tk.IntVar(value=self.coil.turns)
          ttk.Entry(self.master, textvariable=self.turns_var).grid(row=0, column=1)

          ttk.Label(self.master, text="Diameter:").grid(row=1, column=0, padx=10, pady=10)
          self.diam_var = tk.DoubleVar(value=self.coil.diam)
          ttk.Entry(self.master, textvariable=self.diam_var).grid(row=1, column=1)

          ttk.Label(self.master, text="Clearance:").grid(row=2, column=0, padx=10, pady=10)
          self.clearance_var = tk.DoubleVar(value=self.coil.clearance)
          ttk.Entry(self.master, textvariable=self.clearance_var).grid(row=2, column=1)

          ttk.Label(self.master, text="Trace Width:").grid(row=3, column=0, padx=10, pady=10)
          self.trace_width_var = tk.DoubleVar(value=self.coil.traceWidth)
          ttk.Entry(self.master, textvariable=self.trace_width_var).grid(row=3, column=1)

          ttk.Button(self.master, text="Update Coil", command=self.update_coil).grid(row=4, columnspan=2, padx=10, pady=10)

     def update_coil(self):
          # Update the coil object with new values from the GUI
          self.coil.turns = self.turns_var.get()
          self.coil.diam = self.diam_var.get()
          self.coil.clearance = self.clearance_var.get()
          self.coil.traceWidth = self.trace_width_var.get()
          print("Coil updated:", self.coil)
          self.shared_data['coil'] = self.coil
