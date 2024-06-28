import pcbnew
import tkinter as tk
from tkinter import filedialog
from PCBcoilV2 import coilClass

def generate_svg(coil, output_directory):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth):
        print(f"start: {start}, end: {end}")  # Debugging statement
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int(start[0] * 1e6), int(start[1] * 1e6)))  # Convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int(end[0] * 1e6), int(end[1] * 1e6)))  # Convert mm to nm
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Generate the coil lines using renderAsCoordinateList
    line_list = coil.renderAsCoordinateList()
    print(f"line_list: {line_list}")  # Debugging statement
    for line in line_list:
        if len(line) == 2:
            start, end = line
            add_track(board, start, end, coil.traceWidth)
        else:
            print(f"Invalid line segment: {line}")

    # Save the board to a file
    pcbnew.SaveBoard("coil.kicad_pcb", board)

    # Plot to SVG
    plot_controller = pcbnew.PLOT_CONTROLLER(board)
    plot_options = plot_controller.GetPlotOptions()

    plot_options.SetOutputDirectory(output_directory)
    plot_options.SetPlotFrameRef(False)
    plot_options.SetAutoScale(False)
    plot_options.SetMirror(False)
    plot_options.SetUseGerberAttributes(False)
    plot_options.SetScale(1)
    plot_options.SetPlotMode(pcbnew.FILLED)
    plot_options.SetPlotViaOnMaskLayer(False)
    plot_options.SetSkipPlotNPTH_Pads(False)
    plot_options.SetSubtractMaskFromSilk(False)

    # Set up the SVG plot
    plot_options.SetFormat(pcbnew.PLOT_FORMAT_SVG)

    # Plot the F.Cu (Front Copper) layer
    plot_controller.SetLayer(pcbnew.F_Cu)
    plot_controller.OpenPlotfile("coil", pcbnew.PLOT_FORMAT_SVG, "Generated Coil")
    plot_controller.PlotLayer()

    # Finalize the plot
    plot_controller.ClosePlot()

    print(f"SVG file generated as {output_directory}/coil.svg")

def initialize_svg_generation():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Use a file dialog to select the output directory
    output_directory = filedialog.askdirectory(title="Select Output Directory")

    # Initialize coil parameters (example values)
    coil = coilClass(
        turns=9,
        diam=30,
        clearance=0.6,
        traceWidth=0.9,
        layers=1,
        PCBthickness=1.6,
        copperThickness=0.035,
        shape='circle',
        formula='cur_sheet',
        CCW=False,
        loop_enabled=False,
        loop_diameter=0.0,
        loop_shape='circle'
    )

    # Generate the SVG
    generate_svg(coil, output_directory)
