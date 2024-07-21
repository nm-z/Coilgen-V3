import os
import pcbnew
import tkinter as tk
from tkinter import filedialog
from PCBcoilV2 import coilClass
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Get the path to the Temp directory within the project folder
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'Temp')
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

global_output_directory = None

def set_output_directory():
    global global_output_directory
    if global_output_directory is None:
        root = tk.Tk()
        root.withdraw()
        global_output_directory = filedialog.askdirectory(title="Select Output Directory")
        root.destroy()
    return global_output_directory

def export_coil(coil, coil_line_list, export_options):
    output_dir = set_output_directory()
    if output_dir:
        for option, var in export_options.items():
            if var.get():
                if option == 'SVG':
                    generate_svg(coil, coil_line_list, [], combined=False)
                elif option == 'Gerber':
                    generate_gerber(coil, coil_line_list, [], combined=False)
                elif option == 'DXF':
                    generate_dxf(coil, coil_line_list, [], combined=False)

def export_loop(coil, coil_line_list, export_options, loop_with_pads=False, loop_with_pads_2_layer=False, combined=False):
    output_dir = set_output_directory()
    if output_dir:
        for option, var in export_options.items():
            if var.get():
                if option == 'SVG':
                    generate_svg(coil, coil_line_list, [], loop_with_pads=loop_with_pads, loop_with_pads_2_layer=loop_with_pads_2_layer, combined=combined)
                elif option == 'Gerber':
                    generate_gerber(coil, coil_line_list, [], loop_with_pads=loop_with_pads, loop_with_pads_2_layer=loop_with_pads_2_layer, combined=combined)
                elif option == 'DXF':
                    generate_dxf(coil, coil_line_list, [], loop_with_pads=loop_with_pads, loop_with_pads_2_layer=loop_with_pads_2_layer, combined=combined)

def generate_svg(coil, coil_line_list, loop_line_list, offset=(0, 0), loop_with_pads=False, loop_with_pads_2_layer=False, combined=False):
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth, layer, offset=(0, 0)):
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
            print(Fore.RED + f"Invalid coordinates: start={start}, end={end}")

    if combined:
        # Add coil to board
        for line in coil_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu, offset)
        # Add loop with pads
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
            track.SetLayer(pcbnew.F_Cu)
            board.Add(track)

        # Create a dummy footprint to host the pads
        dummy_module = pcbnew.FOOTPRINT(board)
        board.Add(dummy_module)

        # Calculate pad positions
        pad_gap = loop_data['pad_gap']
        pad_y = loop_points[2][1] + loop_data['pad_length'] / 2 - loop_data['loop_trace_width'] / 2
        pad_left_x = loop_points[3][0] + (loop_points[2][0] - loop_points[3][0] - pad_gap) / 2 - loop_data['pad_width'] / 2
        pad_right_x = pad_left_x + loop_data['pad_width'] + pad_gap

        # Add pads and connect them to the loop
        for i, pad_x in enumerate([pad_left_x, pad_right_x]):
            pad = pcbnew.PAD(dummy_module)
            pad.SetSize(pcbnew.VECTOR2I(int(loop_data['pad_width'] * 1e6), int(loop_data['pad_length'] * 1e6)))
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            pad_position = pcbnew.VECTOR2I(int(pad_x * 1e6), int(pad_y * 1e6))
            pad.SetPosition(pad_position)
            pad.SetLayerSet(pcbnew.LSET(pcbnew.F_Cu))
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
            track.SetLayer(pcbnew.F_Cu)
            board.Add(track)

        filename = f"COMBINED_{coil.generateCoilFilename()}"

    elif loop_with_pads:
        for line in loop_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu, offset)
        add_loop_antenna_with_pads(board, coil, offset)
        filename = f"LOOP_{coil.generateCoilFilename()}"
    elif loop_with_pads_2_layer:
        for line in loop_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.B_Cu, offset)
        add_loop_antenna_with_pads_2_layer(board, coil, offset)
        filename = f"LOOP_2LAYER_{coil.generateCoilFilename()}"
    else:
        # Add coil to board
        for line in coil_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu, offset)
        filename = f"COIL_{coil.generateCoilFilename()}"

    temp_board_file = os.path.join(TEMP_DIR, "temp_coil.kicad_pcb")
    pcbnew.SaveBoard(temp_board_file, board)

    plot_controller = pcbnew.PLOT_CONTROLLER(board)
    plot_options = plot_controller.GetPlotOptions()
    plot_options.SetOutputDirectory(global_output_directory)
    plot_options.SetPlotFrameRef(False)
    plot_options.SetAutoScale(False)
    plot_options.SetMirror(False)
    plot_options.SetUseGerberAttributes(False)
    plot_options.SetScale(1)
    plot_options.SetPlotMode(pcbnew.FILLED)
    plot_options.SetPlotViaOnMaskLayer(False)
    plot_options.SetSkipPlotNPTH_Pads(False)
    plot_options.SetSubtractMaskFromSilk(False)

    if combined:
        plot_controller.SetLayer(pcbnew.F_Cu)
        plot_controller.OpenPlotfile(filename, pcbnew.PLOT_FORMAT_SVG, "Combined Coil and Loop")
        plot_controller.PlotLayer()
    elif loop_with_pads:
        plot_controller.SetLayer(pcbnew.B_Cu)
        plot_controller.OpenPlotfile(filename, pcbnew.PLOT_FORMAT_SVG, "Generated Loop")
        plot_controller.PlotLayer()
    elif loop_with_pads_2_layer:
        plot_controller.SetLayer(pcbnew.B_Cu)
        plot_controller.OpenPlotfile(filename, pcbnew.PLOT_FORMAT_SVG, "Generated Loop")
        plot_controller.PlotLayer()
    else:
        plot_controller.SetLayer(pcbnew.F_Cu)
        plot_controller.OpenPlotfile(filename, pcbnew.PLOT_FORMAT_SVG, "Generated Coil")
        plot_controller.PlotLayer()

    plot_controller.ClosePlot()

    print(Fore.GREEN + f"SVG file(s) generated in {global_output_directory}")

def initialize_svg_generation(coil, coil_line_list, loop_line_list, loop_with_pads=False, loop_with_pads_2_layer=False, combined=False):
    generate_svg(coil, coil_line_list, loop_line_list, offset=(0, 0), loop_with_pads=loop_with_pads, loop_with_pads_2_layer=loop_with_pads_2_layer, combined=combined)

def generate_gerber(coil, coil_line_list, loop_line_list, offset=(0, 0), loop_with_pads=False, loop_with_pads_2_layer=False, combined=False):
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth, layer, offset=(0, 0)):
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
            print(Fore.RED + f"Invalid coordinates: start={start}, end={end}")




    if combined:
        # Add coil to board
        for line in coil_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu, offset)
        # Add loop with pads
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
            track.SetLayer(pcbnew.F_Cu)
            board.Add(track)

        # Create a dummy footprint to host the pads
        dummy_module = pcbnew.FOOTPRINT(board)
        board.Add(dummy_module)

        # Calculate pad positions
        pad_gap = loop_data['pad_gap']
        pad_y = loop_points[2][1] + loop_data['pad_length'] / 2 - loop_data['loop_trace_width'] / 2
        pad_left_x = loop_points[3][0] + (loop_points[2][0] - loop_points[3][0] - pad_gap) / 2 - loop_data['pad_width'] / 2
        pad_right_x = pad_left_x + loop_data['pad_width'] + pad_gap

        # Add pads and connect them to the loop
        for i, pad_x in enumerate([pad_left_x, pad_right_x]):
            pad = pcbnew.PAD(dummy_module)
            pad.SetSize(pcbnew.VECTOR2I(int(loop_data['pad_width'] * 1e6), int(loop_data['pad_length'] * 1e6)))
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            pad_position = pcbnew.VECTOR2I(int(pad_x * 1e6), int(pad_y * 1e6))
            pad.SetPosition(pad_position)
            pad.SetLayerSet(pcbnew.LSET(pcbnew.F_Cu))
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
            track.SetLayer(pcbnew.F_Cu)
            board.Add(track)

        filename = f"COMBINED_{coil.generateCoilFilename()}"




    elif loop_with_pads:
        for line in loop_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu, offset)
        add_loop_antenna_with_pads(board, coil, offset)
        filename = f"LOOP_{coil.generateCoilFilename()}"
    elif loop_with_pads_2_layer:
        for line in loop_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.B_Cu, offset)
        add_loop_antenna_with_pads_2_layer(board, coil, offset)
        filename = f"LOOP_2LAYER_{coil.generateCoilFilename()}"
    else:
        # Add coil to board
        for line in coil_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu, offset)
        filename = f"COIL_{coil.generateCoilFilename()}"

    temp_board_file = os.path.join(TEMP_DIR, "temp_coil.kicad_pcb")
    pcbnew.SaveBoard(temp_board_file, board)

    plot_controller = pcbnew.PLOT_CONTROLLER(board)
    plot_options = plot_controller.GetPlotOptions()
    plot_options.SetOutputDirectory(global_output_directory)
    plot_options.SetPlotFrameRef(False)
    plot_options.SetAutoScale(False)
    plot_options.SetMirror(False)
    plot_options.SetUseGerberAttributes(True)
    plot_options.SetScale(1)
    plot_options.SetPlotMode(pcbnew.FILLED)
    plot_options.SetPlotViaOnMaskLayer(False)
    plot_options.SetSkipPlotNPTH_Pads(False)
    plot_options.SetSubtractMaskFromSilk(False)

    if combined:
        plot_controller.SetLayer(pcbnew.F_Cu)
        plot_controller.OpenPlotfile(f"{filename}_F_Cu", pcbnew.PLOT_FORMAT_GERBER, "Combined Coil and Loop")
        plot_controller.PlotLayer()
    elif loop_with_pads:
        plot_controller.SetLayer(pcbnew.B_Cu)
        plot_controller.OpenPlotfile(f"{filename}_B_Cu", pcbnew.PLOT_FORMAT_GERBER, "Loop Back Copper Layer")
        plot_controller.PlotLayer()
    elif loop_with_pads_2_layer:
        plot_controller.SetLayer(pcbnew.B_Cu)
        plot_controller.OpenPlotfile(f"{filename}_B_Cu", pcbnew.PLOT_FORMAT_GERBER, "Loop Back Copper Layer")
        plot_controller.PlotLayer()
    else:
        plot_controller.SetLayer(pcbnew.F_Cu)
        plot_controller.OpenPlotfile(f"{filename}_F_Cu", pcbnew.PLOT_FORMAT_GERBER, "Coil Front Copper Layer")
        plot_controller.PlotLayer()

    plot_controller.ClosePlot()
    print(Fore.GREEN + f"Gerber file(s) generated in {global_output_directory}")

def initialize_gerber_generation(coil, coil_line_list, loop_line_list, loop_with_pads=False, loop_with_pads_2_layer=False, combined=False):
    # Set different offsets based on the loop type
    if loop_with_pads_2_layer:
        offset = (0, 0)  # Specific offset for Loop with Pads 2 Layer
    else:
        offset = (0, 0)  # Default offset for other types

    generate_gerber(coil, coil_line_list, loop_line_list, offset=offset, loop_with_pads=loop_with_pads, loop_with_pads_2_layer=loop_with_pads_2_layer, combined=combined)

def generate_dxf(coil, coil_line_list, loop_line_list, offset=(0, 0), loop_with_pads=False, loop_with_pads_2_layer=False, combined=False):
    board = pcbnew.BOARD()

    def add_track(board, start, end, traceWidth, layer, offset=(150, 100)):
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
            print(Fore.RED + f"Invalid coordinates: start={start}, end={end}")

    if combined:
        # Add coil to board
        for line in coil_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu, offset)
        # Add loop with pads
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
            track.SetLayer(pcbnew.F_Cu)
            board.Add(track)

        # Create a dummy footprint to host the pads
        dummy_module = pcbnew.FOOTPRINT(board)
        board.Add(dummy_module)

        # Calculate pad positions
        pad_gap = loop_data['pad_gap']
        pad_y = loop_points[2][1] + loop_data['pad_length'] / 2 - loop_data['loop_trace_width'] / 2
        pad_left_x = loop_points[3][0] + (loop_points[2][0] - loop_points[3][0] - pad_gap) / 2 - loop_data['pad_width'] / 2
        pad_right_x = pad_left_x + loop_data['pad_width'] + pad_gap

        # Add pads and connect them to the loop
        for i, pad_x in enumerate([pad_left_x, pad_right_x]):
            pad = pcbnew.PAD(dummy_module)
            pad.SetSize(pcbnew.VECTOR2I(int(loop_data['pad_width'] * 1e6), int(loop_data['pad_length'] * 1e6)))
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            pad_position = pcbnew.VECTOR2I(int(pad_x * 1e6), int(pad_y * 1e6))
            pad.SetPosition(pad_position)
            pad.SetLayerSet(pcbnew.LSET(pcbnew.F_Cu))
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
            track.SetLayer(pcbnew.F_Cu)
            board.Add(track)

        filename = f"COMBINED_{coil.generateCoilFilename()}"

    elif loop_with_pads:
        for line in loop_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu, offset)
        add_loop_antenna_with_pads(board, coil, offset)
        filename = f"LOOP_{coil.generateCoilFilename()}"
    elif loop_with_pads_2_layer:
        for line in loop_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.B_Cu, offset)
        add_loop_antenna_with_pads_2_layer(board, coil, offset)
        filename = f"LOOP_2LAYER_{coil.generateCoilFilename()}"
    else:
        # Add coil to board
        for line in coil_line_list:
            if len(line) == 2:
                start, end = line
                add_track(board, start, end, coil.traceWidth, pcbnew.F_Cu, offset)
        filename = f"COIL_{coil.generateCoilFilename()}"

    temp_board_file = os.path.join(TEMP_DIR, "temp_coil.kicad_pcb")
    pcbnew.SaveBoard(temp_board_file, board)

    plot_controller = pcbnew.PLOT_CONTROLLER(board)
    plot_options = plot_controller.GetPlotOptions()
    plot_options.SetDXFPlotUnits(pcbnew.DXF_UNITS_MILLIMETERS)
    plot_options.SetPlotFrameRef(False)
    plot_options.SetAutoScale(False)
    plot_options.SetMirror(False)
    plot_options.SetUseGerberAttributes(False)
    plot_options.SetScale(1)
    plot_options.SetPlotMode(pcbnew.FILLED)
    plot_options.SetPlotViaOnMaskLayer(False)
    plot_options.SetSkipPlotNPTH_Pads(False)
    plot_options.SetSubtractMaskFromSilk(False)
    plot_options.SetOutputDirectory(global_output_directory)

    if combined:
        plot_controller.SetLayer(pcbnew.F_Cu)
        plot_controller.OpenPlotfile(filename, pcbnew.PLOT_FORMAT_DXF, "Combined Coil and Loop")
        plot_controller.PlotLayer()
    elif loop_with_pads:
        plot_controller.SetLayer(pcbnew.B_Cu)
        plot_controller.OpenPlotfile(filename, pcbnew.PLOT_FORMAT_DXF, "Generated Loop")
        plot_controller.PlotLayer()
    elif loop_with_pads_2_layer:
        plot_controller.SetLayer(pcbnew.B_Cu)
        plot_controller.OpenPlotfile(filename, pcbnew.PLOT_FORMAT_DXF, "Generated Loop")
        plot_controller.PlotLayer()
    else:
        plot_controller.SetLayer(pcbnew.F_Cu)
        plot_controller.OpenPlotfile(filename, pcbnew.PLOT_FORMAT_DXF, "Generated Coil")
        plot_controller.PlotLayer()

    # Close plot file
    plot_controller.ClosePlot()

    print(Fore.GREEN + f"DXF file(s) generated in {global_output_directory}")

def initialize_dxf_generation(coil, coil_line_list, loop_line_list, loop_with_pads=False, combined=False):
    generate_dxf(coil, coil_line_list, loop_line_list, offset=(0, 0), loop_with_pads=loop_with_pads, combined=combined)



def generate_loop_antenna_with_pads_2_layer(coil, offset=(0, 0), scale_factor=0.8000):
    loop_trace_width = 0.6096  # mm
    coil_diameter = float(coil.diam)
    coil_trace_width = float(coil.traceWidth)    
    scale_factor=0.8000

    actual_coil_diam = coil_diameter + coil_trace_width 

#     loop_diameter = actual_coil_diam * scale_factor

    # Adjusted calculation to make actual_loop_diam equal to 80% of coil_diam_adjusted
    loop_diameter = (actual_coil_diam * scale_factor) - loop_trace_width




    # Calculate pad dimensions based on the scaled loop diameter
    if loop_diameter <= 12:
        pad_length, pad_width = 1.905, 1.5875
    else:
        pad_length, pad_width = 3.81, 3.175

    pad_gap = 1.27  # mm, space between pads

    # Calculate loop coordinates based on the scaled loop diameter
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

    # Apply offset to both loop and pad coordinates
    loop_coords = [(x + offset[0], y + offset[1]) for x, y in loop_coords]
    pad_left_center = (pad_left_x + offset[0], pad_y + offset[1])
    pad_right_center = (pad_right_x + offset[0], pad_y + offset[1])

    print(Fore.BLUE + f"Loop Diameter-2 Layer: {loop_diameter} mm")





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

def add_loop_antenna_with_pads_2_layer(board, coil, offset=(0, 0), scale_factor=0.8000):
    loop_data = generate_loop_antenna_with_pads_2_layer(coil, offset, scale_factor)
    
    # Use loop points directly without additional scaling
    loop_points = loop_data['loop']
    
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
    pad_gap = loop_data['pad_gap']
    pad_y = loop_points[2][1] + loop_data['pad_length'] / 2 - loop_data['loop_trace_width'] / 2
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
        trace_end_x = pad_x - loop_data['pad_width'] / 2 if i == 0 else pad_x + loop_data['pad_width'] / 2
        trace_end_y = loop_points[2][1]  # Keep the same y-coordinate as the loop corner
        
        track.SetEnd(pcbnew.VECTOR2I(int(trace_end_x * 1e6), int(trace_end_y * 1e6)))
        track.SetWidth(int(loop_data['loop_trace_width'] * 1e6))
        track.SetLayer(pcbnew.B_Cu)
        board.Add(track)

def generate_loop_antenna_with_pads(coil, offset=(0, 0)):
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
    
    print(Fore.BLUE + f"Loop diameter: {loop_diameter} mm")
    
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
print(Fore.BLUE + "Generated Loop Antenna With Pads")

def add_loop_antenna_with_pads(board, coil, offset=(0, 0)):
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
print(Fore.BLUE + "Added 'Loop Antenna With Pads' to the board")


