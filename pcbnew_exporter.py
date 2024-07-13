import sys
import os
import traceback

# Adjust the path for packaged environment
if getattr(sys, 'frozen', False):
    kicad_bin_path = os.path.join(sys._MEIPASS, 'KiCad', 'bin')
    print(f"Running from frozen executable. KiCad bin path: {kicad_bin_path}")
else:
    kicad_bin_path = r'C:\Program Files\KiCad\8.0\bin'
    print(f"Running from source. KiCad bin path: {kicad_bin_path}")

sys.path.append(os.path.join(kicad_bin_path, 'Lib', 'site-packages'))
os.add_dll_directory(kicad_bin_path)

try:
    import pcbnew
    print(f"pcbnew version: {pcbnew.GetBuildVersion()}")
except ImportError as e:
    print(f"Error importing pcbnew: {e}")
    print(f"sys.path: {sys.path}")
    print(f"os.environ['PATH']: {os.environ['PATH']}")

import tkinter as tk
from tkinter import filedialog
from PCBcoilV2 import coilClass

# Get the path to the Temp directory within the project folder
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'Temp')
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def generateCoilFilename(coil):
    return coil.generateCoilFilename()

def generate_svg(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100), loop_with_pads=False):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth, layer):
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            start_flipped = (start[0], -start[1])
            end_flipped = (end[0], -end[1])
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int((start_flipped[0] + offset[0]) * 1e6), int((start_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int((end_flipped[0] + offset[0]) * 1e6), int((end_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetLayer(layer)
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Add tracks based on which list is provided
    if loop_with_pads:
        add_loop_antenna_with_pads(board, coil, offset)
    elif loop_line_list:
        for start, end in loop_line_list:
            add_track(board, start, end, coil.traceWidth, pcbnew.B_Cu)
    elif coil_line_list:
        for line in coil_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu)

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

    # Generate unique filenames for coil and loop
    coil_filename = f"COIL_{coil.generateCoilFilename()}"
    loop_filename = f"LOOP_{coil.generateCoilFilename()}"

    # Plot the F.Cu (Front Copper) layer
    if coil_line_list:
        plot_controller.SetLayer(pcbnew.F_Cu)
        plot_controller.OpenPlotfile(coil_filename, pcbnew.PLOT_FORMAT_SVG, "Generated Coil")
        plot_controller.PlotLayer()

    # Plot the B.Cu (Back Copper) layer if loop antenna exists
    if loop_with_pads or loop_line_list:
        plot_controller.SetLayer(pcbnew.B_Cu)
        plot_controller.OpenPlotfile(loop_filename, pcbnew.PLOT_FORMAT_SVG, "Generated Loop")
        plot_controller.PlotLayer()

    # Finalize the plot
    plot_controller.ClosePlot()

    print(f"SVG file(s) generated in {output_directory}")

def initialize_svg_generation(coil, coil_line_list, loop_line_list, loop_with_pads=False):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        generate_svg(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100), loop_with_pads=loop_with_pads)

def generate_gerber(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100), loop_with_pads=False):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth, layer):
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            start_flipped = (start[0], -start[1])
            end_flipped = (end[0], -end[1])
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int((start_flipped[0] + offset[0]) * 1e6), int((start_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int((end_flipped[0] + offset[0]) * 1e6), int((end_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetLayer(layer)
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Add tracks based on which list is provided
    if loop_with_pads:
        add_loop_antenna_with_pads(board, coil, offset)
    elif loop_line_list:
        for start, end in loop_line_list:
            add_track(board, start, end, coil.traceWidth, pcbnew.B_Cu)
    elif coil_line_list:
        for line in coil_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu)

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

    # Generate unique filenames for coil and loop
    coil_filename = f"COIL_{coil.generateCoilFilename()}"
    loop_filename = f"LOOP_{coil.generateCoilFilename()}"

    # Plot the F.Cu (Front Copper) layer to Gerber
    if coil_line_list:
        plot_controller.SetLayer(pcbnew.F_Cu)
        plot_controller.OpenPlotfile(f"{coil_filename}_F_Cu", pcbnew.PLOT_FORMAT_GERBER, "Coil Front Copper Layer")
        plot_controller.PlotLayer()

    # Plot the B.Cu (Back Copper) layer to Gerber if loop antenna exists
    if loop_with_pads or loop_line_list:
        plot_controller.SetLayer(pcbnew.B_Cu)
        plot_controller.OpenPlotfile(f"{loop_filename}_B_Cu", pcbnew.PLOT_FORMAT_GERBER, "Loop Back Copper Layer")
        plot_controller.PlotLayer()

    # Finalize the plot
    plot_controller.ClosePlot()
    print(f"Gerber file(s) generated in {output_directory}")

def initialize_gerber_generation(coil, coil_line_list, loop_line_list, loop_with_pads=False):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        generate_gerber(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100), loop_with_pads=loop_with_pads)

def generate_dxf(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100), loop_with_pads=False):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth, layer):
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            start_flipped = (start[0], -start[1])
            end_flipped = (end[0], -end[1])
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int((start_flipped[0] + offset[0]) * 1e6), int((start_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int((end_flipped[0] + offset[0]) * 1e6), int((end_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetLayer(layer)
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Add tracks based on which list is provided
    if loop_with_pads:
        add_loop_antenna_with_pads(board, coil, offset)
    elif loop_line_list:
        for start, end in loop_line_list:
            add_track(board, start, end, coil.traceWidth, pcbnew.B_Cu)
    elif coil_line_list:
        for line in coil_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu)

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

    # Generate unique filenames for coil and loop
    coil_filename = f"COIL_{coil.generateCoilFilename()}"
    loop_filename = f"LOOP_{coil.generateCoilFilename()}"

    # Plot the F.Cu (Front Copper) layer
    if coil_line_list:
        plot_controller.SetLayer(pcbnew.F_Cu)
        plot_controller.OpenPlotfile(coil_filename, pcbnew.PLOT_FORMAT_DXF, "Generated Coil")
        plot_controller.PlotLayer()

    # Plot the B.Cu (Back Copper) layer if loop antenna exists
    if loop_with_pads or loop_line_list:
        plot_controller.SetLayer(pcbnew.B_Cu)
        plot_controller.OpenPlotfile(loop_filename, pcbnew.PLOT_FORMAT_DXF, "Generated Loop")
        plot_controller.PlotLayer()

    # Finalize the plot
    plot_controller.ClosePlot()

    print(f"DXF file(s) generated in {output_directory}")

def initialize_dxf_generation(coil, coil_line_list, loop_line_list, loop_with_pads=False):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        generate_dxf(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100), loop_with_pads=loop_with_pads)

def generate_drill(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100)):
    # Initialize the board
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth, layer):
        if isinstance(start, (list, tuple)) and isinstance(end, (list, tuple)):
            start_flipped = (start[0], -start[1])
            end_flipped = (end[0], -end[1])
            track = pcbnew.PCB_TRACK(board)
            track.SetWidth(int(traceWidth * 1e6))  # Convert mm to nm
            track.SetStart(pcbnew.VECTOR2I(int((start_flipped[0] + offset[0]) * 1e6), int((start_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetEnd(pcbnew.VECTOR2I(int((end_flipped[0] + offset[0]) * 1e6), int((end_flipped[1] + offset[1]) * 1e6)))  # Apply offset and convert mm to nm
            track.SetLayer(layer)
            board.Add(track)
        else:
            print(f"Invalid coordinates: start={start}, end={end}")

    # Add tracks based on which list is provided
    if loop_line_list:
        for start, end in loop_line_list:
            add_track(board, start, end, coil.traceWidth, pcbnew.B_Cu)
    elif coil_line_list:
        for line in coil_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu)

    # Save the board to a temporary file in the Temp directory
    temp_board_file = os.path.join(TEMP_DIR, "temp_coil.kicad_pcb")
    pcbnew.SaveBoard(temp_board_file, board)

    # Generate the drill files
    excellon_writer = pcbnew.EXCELLON_WRITER(board)
    excellon_writer.SetMapFileFormat(pcbnew.PLOT_FORMAT_PDF)
    excellon_writer.SetOptions(False, False, pcbnew.VECTOR2I(0, 0), False)
    excellon_writer.SetFormat(True)

    # Generate unique filenames for coil and loop drill files
    coil_filename = f"COIL_{coil.generateCoilFilename()}"
    loop_filename = f"LOOP_{coil.generateCoilFilename()}"

    # Generate drill files
    if coil_line_list:
        excellon_writer.CreateDrillFile(os.path.join(output_directory, f"{coil_filename}-PTH.drl"))
        excellon_writer.CreateDrillFile(os.path.join(output_directory, f"{coil_filename}-NPTH.drl"))

    if loop_line_list:
        excellon_writer.CreateDrillFile(os.path.join(output_directory, f"{loop_filename}-PTH.drl"))
        excellon_writer.CreateDrillFile(os.path.join(output_directory, f"{loop_filename}-NPTH.drl"))

    print(f"Drill files generated in {output_directory}")

def initialize_drill_generation(coil, coil_line_list, loop_line_list):
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    output_directory = filedialog.askdirectory(title="Select Output Directory")
    if output_directory:
        generate_drill(coil, coil_line_list, loop_line_list, output_directory, offset=(150, 100))

def generate_loop_antenna_with_pads(coil, offset=(150, 100)):
    loop_trace_width = 0.6096  # mm
    coil_diameter = float(coil.diam)
    coil_trace_width = float(coil.traceWidth)
    loop_diameter = coil_diameter + 2 * (coil_trace_width + loop_trace_width)
    
    # Calculate pad dimensions
    if coil_diameter <= 12:
        pad_length, pad_width = 1.905, 1.5875
    else:
        pad_length, pad_width = 3.81, 3.175
    
    pad_gap = 1.27  # mm, space between pads
    
    # Calculate loop coordinates
    half_loop_size = loop_diameter / 2
    loop_coords = [
        (-half_loop_size, -half_loop_size),
        (half_loop_size, -half_loop_size),
        (half_loop_size, half_loop_size),
        (-half_loop_size, half_loop_size)
    ]
    
    # Calculate pad coordinates (flags facing outward, hanging downward)
    pad_y = half_loop_size
    pad_left_x = -pad_gap/2 - pad_width
    pad_right_x = pad_gap/2
    
    # Apply offset
    loop_coords = [(x + offset[0], y + offset[1]) for x, y in loop_coords]
    pad_left_center = (pad_left_x + offset[0], pad_y + offset[1])
    pad_right_center = (pad_right_x + offset[0], pad_y + offset[1])
    
    return {
        'loop': loop_coords,
        'loop_trace_width': loop_trace_width,
        'pad_left': pad_left_center,
        'pad_right': pad_right_center,
        'pad_length': pad_length,
        'pad_width': pad_width,
        'loop_diameter': loop_diameter,
        'pad_gap': pad_gap
    }

def add_loop_antenna_with_pads(board, coil, offset=(150, 100)):
    loop_data = generate_loop_antenna_with_pads(coil, offset)
    
    # Add C-shaped loop (top, left, right)
    loop_points = [
        (loop_data['loop'][0][0], loop_data['loop'][0][1]),  # Top-left
        (loop_data['loop'][1][0], loop_data['loop'][1][1]),  # Top-right
        (loop_data['loop'][2][0], loop_data['loop'][2][1]),  # Bottom-right
        (loop_data['loop'][3][0], loop_data['loop'][3][1])   # Bottom-left
    ]
    
    # Create top, left, and right sides
    for i in [0, 3, 1]:
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(pcbnew.VECTOR2I(int(loop_points[i][0] * 1e6), int(loop_points[i][1] * 1e6)))
        track.SetEnd(pcbnew.VECTOR2I(int(loop_points[(i+1)%4][0] * 1e6), int(loop_points[(i+1)%4][1] * 1e6)))
        track.SetWidth(int(loop_data['loop_trace_width'] * 1e6))
        track.SetLayer(pcbnew.B_Cu)
        board.Add(track)
    
    # Create a dummy footprint to host the pads
    dummy_module = pcbnew.FOOTPRINT(board)
    board.Add(dummy_module)
    
    # Calculate pad positions
    pad_gap = 1.27  # mm, space between pads
    pad_y = loop_points[2][1] + loop_data['pad_length'] / 2 - loop_data['loop_trace_width'] / 2  # Move pads up by half a trace width
    pad_left_x = loop_points[3][0] + (loop_points[2][0] - loop_points[3][0] - pad_gap) / 2 - loop_data['pad_width'] / 2
    pad_right_x = pad_left_x + loop_data['pad_width'] + pad_gap
    
    # Add pads and connect them to the loop
    for i, pad_x in enumerate([pad_left_x, pad_right_x]):
        pad = pcbnew.PAD(dummy_module)
        pad.SetSize(pcbnew.VECTOR2I(int(loop_data['pad_width'] * 1e6), int(loop_data['pad_length'] * 1e6)))
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad_position = pcbnew.VECTOR2I(int(pad_x * 1e6), int(pad_y * 1e6))
        pad.SetPosition(pad_position)
        pad.SetLayerSet(pcbnew.LSET(pcbnew.B_Cu))
        dummy_module.Add(pad)
        
        # Add trace connecting loop corner to pad
        track = pcbnew.PCB_TRACK(board)
        corner_x = loop_points[3][0] if i == 0 else loop_points[2][0]
        track.SetStart(pcbnew.VECTOR2I(int(corner_x * 1e6), int(loop_points[2][1] * 1e6)))
        
        # Calculate the end point of the trace to cover the entire width of the pad
        trace_end_x = pad_x - loop_data['pad_width']/2 if i == 0 else pad_x + loop_data['pad_width']/2
        trace_end_y = loop_points[2][1]  # Keep the same y-coordinate as the loop corner
        
        track.SetEnd(pcbnew.VECTOR2I(int(trace_end_x * 1e6), int(trace_end_y * 1e6)))
        track.SetWidth(int(loop_data['loop_trace_width'] * 1e6))
        track.SetLayer(pcbnew.B_Cu)
        board.Add(track)

# Example usage:
# board = pcbnew.GetBoard()
# coil = Coil(diam=10, traceWidth=1)
# add_c_shaped_loop_with_pads(board, coil)

def export_coil(coil, coil_line_list, export_options):
    for option, var in export_options.items():
        if var.get():
            if option == 'SVG':
                initialize_svg_generation(coil, coil_line_list, [])
            elif option == 'Gerber':
                initialize_gerber_generation(coil, coil_line_list, [])
            elif option == 'DXF':
                initialize_dxf_generation(coil, coil_line_list, [])
            # Drill file generation is commented out
            # elif option == 'Drill':
            #     initialize_drill_generation(coil, coil_line_list, [])

def export_loop(coil, loop_line_list, export_options, loop_with_pads=False):
    for option, var in export_options.items():
        if var.get():
            if loop_with_pads:
                loop_data = generate_loop_antenna_with_pads(coil)
                if option == 'SVG':
                    initialize_svg_generation(coil, [], loop_data['loop'], loop_with_pads=True)
                elif option == 'Gerber':
                    initialize_gerber_generation(coil, [], loop_data['loop'], loop_with_pads=True)
                elif option == 'DXF':
                    initialize_dxf_generation(coil, [], loop_data['loop'], loop_with_pads=True)
            else:
                if option == 'SVG':
                    initialize_svg_generation(coil, [], loop_line_list)
                elif option == 'Gerber':
                    initialize_gerber_generation(coil, [], loop_line_list)
                elif option == 'DXF':
                    initialize_dxf_generation(coil, [], loop_line_list)
z