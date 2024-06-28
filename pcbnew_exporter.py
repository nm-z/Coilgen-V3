import os
import pcbnew
import tkinter as tk
from tkinter import filedialog
from PCBcoilV2 import coilClass

# Get the path to the Temp directory within the project folder
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'Temp')
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def generate_svg(coil, line_list, output_directory, offset=(150, 100)):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth):
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            start_flipped = (start[0], -start[1])
            end_flipped = (end[0], -end[1])
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int((start_flipped[0] + offset[0]) * 1e6), int((start_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int((end_flipped[0] + offset[0]) * 1e6), int((end_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Use the provided line list to generate the coil tracks
    for line in line_list:
        if len(line) == 2:
            start, end = line
            add_track(board, start, end, coil.traceWidth)

    # Save the board to a temporary file in the Temp directory
    temp_board_file = os.path.join(TEMP_DIR, "temp_coil.kicad_pcb")
    pcbnew.SaveBoard(temp_board_file, board)

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

def initialize_svg_generation(coil, line_list):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Use a file dialog to select the output directory
    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        # Generate the SVG with the specified offset
        generate_svg(coil, line_list, output_directory, offset=(150, 100))

def generate_gerber(coil, line_list, output_directory, offset=(150, 100)):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth):
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            start_flipped = (start[0], -start[1])
            end_flipped = (end[0], -end[1])
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int((start_flipped[0] + offset[0]) * 1e6), int((start_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int((end_flipped[0] + offset[0]) * 1e6), int((end_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Use the provided line list to generate the coil tracks
    for line in line_list:
        if len(line) == 2:
            start, end = line
            add_track(board, start, end, coil.traceWidth)

    # Save the board to a temporary file in the Temp directory
    temp_board_file = os.path.join(TEMP_DIR, "temp_coil.kicad_pcb")
    pcbnew.SaveBoard(temp_board_file, board)

    # Plot to Gerber
    plot_controller = pcbnew.PLOT_CONTROLLER(board)
    plot_options = plot_controller.GetPlotOptions()

    plot_options.SetOutputDirectory(output_directory)
    plot_options.SetPlotFrameRef(False)
    plot_options.SetAutoScale(False)
    plot_options.SetMirror(False)
    plot_options.SetUseGerberAttributes(True)
    plot_options.SetScale(1)
    plot_options.SetPlotMode(pcbnew.FILLED)
    plot_options.SetPlotViaOnMaskLayer(False)
    plot_options.SetSkipPlotNPTH_Pads(False)
    plot_options.SetSubtractMaskFromSilk(False)

    # Plot only the Front Copper layer to Gerber
    plot_controller.SetLayer(pcbnew.F_Cu)
    plot_controller.OpenPlotfile("F_Cu", pcbnew.PLOT_FORMAT_GERBER, "Front Copper Layer")
    plot_controller.PlotLayer()

    # Finalize the plot
    plot_controller.ClosePlot()
    print(f"Gerber file generated as {output_directory}/F_Cu.gbr")

def initialize_gerber_generation(coil, line_list):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Use a file dialog to select the output directory
    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        # Generate the Gerber files with the specified offset
        generate_gerber(coil, line_list, output_directory, offset=(150, 100))

def generate_dxf(coil, line_list, output_directory, offset=(150, 100)):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth):
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            start_flipped = (start[0], -start[1])
            end_flipped = (end[0], -end[1])
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int((start_flipped[0] + offset[0]) * 1e6), int((start_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int((end_flipped[0] + offset[0]) * 1e6), int((end_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Use the provided line list to generate the coil tracks
    for line in line_list:
        if len(line) == 2:
            start, end = line
            add_track(board, start, end, coil.traceWidth)

    # Save the board to a temporary file in the Temp directory
    temp_board_file = os.path.join(TEMP_DIR, "temp_coil.kicad_pcb")
    pcbnew.SaveBoard(temp_board_file, board)

    # Plot to DXF
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

    # Set up the DXF plot
    plot_options.SetFormat(pcbnew.PLOT_FORMAT_DXF)

    # Plot the F.Cu (Front Copper) layer
    plot_controller.SetLayer(pcbnew.F_Cu)
    plot_controller.OpenPlotfile("coil", pcbnew.PLOT_FORMAT_DXF, "Generated Coil")
    plot_controller.PlotLayer()

    # Finalize the plot
    plot_controller.ClosePlot()

    print(f"DXF file generated as {output_directory}/coil.dxf")

def initialize_dxf_generation(coil, line_list):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Use a file dialog to select the output directory
    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        # Generate the DXF with the specified offset
        generate_dxf(coil, line_list, output_directory, offset=(150, 100))

def generate_drill(coil, line_list, output_directory, offset=(150, 100)):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth):
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            start_flipped = (start[0], -start[1])
            end_flipped = (end[0], -end[1])
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int((start_flipped[0] + offset[0]) * 1e6), int((start_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int((end_flipped[0] + offset[0]) * 1e6), int((end_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Use the provided line list to generate the coil tracks
    for line in line_list:
        if len(line) == 2:
            start, end = line
            add_track(board, start, end, coil.traceWidth)

    # Save the board to a temporary file in the Temp directory
    temp_board_file = os.path.join(TEMP_DIR, "temp_coil.kicad_pcb")
    pcbnew.SaveBoard(temp_board_file, board)

    # Generate the drill files
    drl_writer = pcbnew.EXCELLON_WRITER(board)
    drl_writer.SetMapFileFormat(pcbnew.PLOT_FORMAT_PDF)
    drl_writer.SetOptions(False, False, pcbnew.VECTOR2I(0, 0), False)
    drl_writer.SetFormat(True)
    drl_writer.CreateDrillandMapFilesSet(output_directory, True, False)

    print(f"Drill files generated in {output_directory}")

def initialize_drill_generation(coil, line_list):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Use a file dialog to select the output directory
    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        # Generate the drill files with the specified offset
        generate_drill(coil, line_list, output_directory, offset=(150, 100))
