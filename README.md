# Coilgen V3 Documentation

## Table of Contents
1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Getting Started](#3-getting-started)
4. [Features](#4-features)
5. [User Interface](#5-user-interface)
   - [Coil Design Parameters](#5-coil-design-parameters)
   - [Loop Antenna Options](#5-loop-antenna-options)
   - [Export Options](#5-export-options)
   - [Resonant Frequency Estimation](#5-resonant-frequency-estimation)
   - [Update and Export Buttons](#5-update-and-export-buttons)
6. [Usage Guide](#6-usage-guide)
7. [Configuration](#7-configuration)
8. [Export Options](#8-export-options)
9. [Troubleshooting](#9-troubleshooting)
10. [FAQ](#10-faq)
11. [Changelog](#11-changelog)
12. [Resonant Frequency Estimation](#12-resonant-frequency-estimation)
13. [Square Coil Geometry](#13-square-coil-geometry)
14. [Acknowledgements](#14-acknowledgements)
15. [Importing pcbnew Module](#15-importing-pcbnew-module)

## 1. Introduction

Coilgen V3 is a powerful tool specifically designed for creating and generating SansEC (Sans Electric Connection) coil patterns. This version includes several improvements and new features over previous versions, all tailored to the unique requirements of SansEC sensor technology.

## 2. SansEC Coil Technology

### What is a SansEC Coil?
A SansEC (Sans Electrical Connections) coil is an innovative type of sensor developed by NASA's Langley Research Center. It is an open-circuit, resonant sensor that operates without electrical connections. The coil is designed as a self-resonating planar pattern of electrically conductive material that can be wirelessly powered using external oscillating magnetic fields.

### How it Works
When exposed to a time-varying magnetic field, the SansEC coil induces an electromotive force and responds with its own harmonic magnetic and electric fields. Changes to these fields due to deformation, damage, or alterations in the surrounding material can be correlated to the magnitude of the physical quantity being measured, enabling the coil to function as a versatile sensor.

### Applications
SansEC coils have a wide range of applications, including:
- Damage detection and monitoring in composite materials
- Wireless sensing for axial load force, linear displacement, rotation, strain, pressure, torque, and motion sensing
- Smart skin for composite aircraft
- Geological spectroscopy
- Nondestructive testing
- Hazardous material monitoring
- Zero-gravity fluid volume measurement
- Noninvasive medical monitoring and scanning

### Benefits
The SansEC coil technology offers several advantages:
- No electrical connections required
- Wirelessly powered and interrogated
- Damage resilient and environmentally friendly to manufacture and use
- Can measure multiple physical attributes simultaneously
- Improves reliability by reducing the number of electrical connections within the circuit
- Suitable for mass production and can be manufactured to specific sizes

Coilgen V3 is designed to facilitate the creation and optimization of these innovative SansEC coil patterns, making this advanced technology accessible to both experts in the field and those new to SansEC sensor development.

## 2. Installation

### Windows Installation
1. Go to the official Coilgen V3 releases page on GitHub.
2. Download the latest Windows executable (.exe) file.
3. Once downloaded, double-click the .exe file to run Coilgen V3 directly. No additional installation is required.

### Linux Installation
1. Visit the official Coilgen V3 releases page on GitHub.
2. Download the latest Linux executable file.
3. Once downloaded, double-click the executable file to run Coilgen V3 directly. No additional installation is required.

Note: For both Windows and Linux, you can create a shortcut or alias to the executable for easy access.

## 3. Getting Started

To get started with Coilgen V3, follow these steps:
1. Launch the application and select the desired coil pattern from the menu.
2. Adjust the parameters as needed to customize the coil design.
3. Use the intuitive menu and UI to navigate and configure the application.
4. Export the designed coil pattern in the desired format (DXF, SVG, etc.).

## 4. Features

Coilgen V3 includes the following features:
- 2nd layer Loop antenna Exporting
- Intuitive Menu and UI
- SansEC Loop Antenna DXF and SVG export
- Geometry checking
- 2-layer loop antenna with pads option
- Resonant Frequency Estimation
- Configuration saving

## 5. User Interface

The Coilgen V3 user interface is designed to be intuitive and user-friendly.

![image](https://github.com/user-attachments/assets/1d8bbf4d-86a5-4e66-b63c-118846bcee9b)

### 5. Coil Design Parameters

Coilgen V3 allows you to customize various parameters for your SansEC coil design. Here's a breakdown of each parameter:

- **Turns**: Number of coil revolutions, affecting inductance, resistance, and resonant frequency.
- **Diameter**: Overall coil diameter, influencing inductance and sensing area.
- **Width between traces**: Spacing between turns, affecting mutual inductance and parasitic capacitance.
- **Trace Width**: Conductor width, minimizing resistance while considering skin effect.
- **Layers**: Number of PCB layers used, impacting inductance and manufacturing complexity.
- **PCB Thickness**: PCB substrate thickness, affecting layer spacing and parasitic capacitance.
- **Copper Thickness**: Copper trace thickness, reducing resistance but impacting manufacturing costs.
- **Shape**: Choose from square, hexagon, octagon, or circle.
- **Formula**: Select the calculation method for estimating coil properties (cur_sheet, monomial, or wheeler).

These parameters allow for fine-tuning of the SansEC coil design to meet specific requirements for resonant frequency, sensing area, sensitivity, and manufacturability. The optimal values depend on the intended application of the SansEC sensor.

### 5. Loop Antenna Options

- **Loop Antenna Layer**: Choose between "Loop Antenna with Pads" or "Loop Antenna with Pads 2 Layer"
- **Loop Diameter**: Option to set as "Auto" or "Custom"
  - When "Custom" is selected, you can input a specific diameter for the loop antenna

### 5. Export Options

You can choose which files to export:
- SVG
- Gerber
- DXF

Additionally, you can select whether to export the coil, the loop, or both.

### 5. Resonant Frequency Estimation

The interface includes a section for resonant frequency estimation:
- Display of the estimated resonant frequency based on current parameters
- Input field for desired resonant frequency
- Button to calculate the diameter needed for a specific frequency

### 5. Update and Export Buttons

- **Update**: Recalculates the coil parameters based on your inputs
- **Export**: Generates the selected file formats with the current coil design

This interface provides a comprehensive set of tools for designing and exporting your coil patterns, with real-time updates and estimations to aid in the design process.

## 6. Usage Guide

To use Coilgen V3, follow these steps:
1. Select the desired coil pattern from the menu.
2. Adjust the parameters as needed to customize the coil design.
3. Use the geometry checking feature to ensure the design is valid.
4. Export the designed coil pattern in the desired format (DXF, SVG, etc.).

## 7. Configuration

Coilgen V3 allows for configuration of various options, including:
- Coil design parameters
- Export options
- UI preferences

## 8. Export Options

Coilgen V3 supports the following export options:
- DXF export
- SVG export
- Gerber file export

## 9. Troubleshooting

Common issues and their solutions:

- Issue: `pcbnew` not found.
  Solution: You may need to download KiCad 8.0. and add Python to your PATH. Install Python 3.11 specifically.

## 10. FAQ

Q: What is the purpose of Coilgen V3?
A: Coilgen V3 is a tool for designing and generating SansEC coil patterns.

Q: What file formats does Coilgen V3 support?
A: Coilgen V3 supports DXF, SVG, and Gerber file formats.

## 11. Changelog

List of changes and new features in V3:
- Do not grey out on init since 2 layer is selected by default
- 1 and 2 layer: change from Shape to Layer
- Using auto-scaled diameter for loop
- Loop Diameter-2 Layer: 15.3904 mm
- Gerber file(s) generated in /home/nate/Desktop/Coilgen_Exports

### Example Usage

The following example demonstrates the usage of Coilgen V3:
```
Using auto-scaled diameter for loop.
Loop Diameter-2 Layer: 15.3904 mm
Gerber file(s) generated in /home/nate/Desktop/Coilgen_Exports
```

## 12. Resonant Frequency Estimation

Coilgen V3 includes a feature for estimating the resonant frequency of the designed coil pattern. This feature uses a linear regression model based on actual measurement data to estimate the frequency based on the coil design parameters.

The model was developed using data collected from real-world measurements of various SansEC coil designs. This data includes trace lengths and corresponding resonant frequencies. A linear regression model was then fitted to this data, resulting in an equation that relates trace length to resonant frequency.

![Figure 1](https://github.com/user-attachments/assets/c82b1e01-2ae0-4663-a8fc-92451234c56b)

This model provides a reasonable approximation of the resonant frequency for a wide range of SansEC coil designs. However, it's important to note that the accuracy of the estimation depends on the validity of the assumptions and the quality of the measurement data used to develop the model. For critical applications, it's recommended to validate the estimated resonant frequency through actual measurements.

## 13. Square Coil Geometry

The square coil geometry is configured in a perfect square. The changes were made to ensure that the first three traces starting from the outside (right side, top, then left) are the same length as the diameter.

| Trace   | Calculation                           | Turn | Length |
|---------|---------------------------------------|------|--------|
| Trace 1 | = diam                                | 1    | 30mm   |
| Trace 2 | = diam                                | 1    | 30mm   |
| Trace 3 | = diam                                | 1    | 30mm   |
| Trace 4 | = diam - (Trace Width + Clearance)    | 1    | 27mm   |
| Trace 5 | = diam - (Trace Width + Clearance)    | 2    | 27mm   |
| Trace 6 | = diam - 2(Trace Width + Clearance)   | 2    | 24mm   |
| Trace 7 | = diam - 2(Trace Width + Clearance)   | 2    | 24mm   |
| Trace 8 | = diam - 3(Trace Width + Clearance)   | 2    | 21mm   |
| Trace 9 | = diam - 3(Trace Width + Clearance)   | 3    | 21mm   |
| Trace 10| = diam - 4(Trace Width + Clearance)   | 3    | 18mm   |
| Trace 11| = diam - 4(Trace Width + Clearance)   | 3    | 18mm   |
| Trace 12| = diam - 5(Trace Width + Clearance)   | 3    | 15mm   |

## 14. Acknowledgements

Coilgen V3 builds upon the work of other open-source projects. I would like to acknowledge the following contribution:

- The Python calculations and Pygame rendering in Coilgen V3 are based on the [PCBcoilGenerator](https://github.com/thijses/PCBcoilGenerator) project by thijses. I am grateful for their work, which has been instrumental in developing certain aspects of Coilgen V3.

I encourage users to check out the PCBcoilGenerator project for more information on the underlying calculations and rendering techniques used in Coilgen V3.

## 15. Importing pcbnew Module

The script begins by importing the pcbnew module, which provides the necessary functions and classes to interact with KiCad's PCB design environment.

python
```
import pcbnew
```
### Accessing the PCB Layout

The pcbnew module is used to access the current PCB layout. This is typically done by creating an instance of the pcbnew.BOARD class, which represents the entire PCB design.

python
```
board = pcbnew.GetBoard()
```
### Creating and Modifying PCB Elements

The script uses various classes and methods from the pcbnew module to create and modify PCB elements like tracks, vias, and zones. Here are some key examples:

#### Adding a Track

Tracks are the conductive paths on the PCB. The script adds tracks using the pcbnew.TRACK class.

python
```
track = pcbnew.TRACK(board)
track.SetStart(start_point)
track.SetEnd(end_point)
track.SetWidth(track_width)
track.SetLayer(pcbnew.F_Cu)  # Place track on the front copper layer
board.Add(track)
```
#### Adding a Via

Vias are used to connect tracks between different layers of the PCB. The script adds vias using the pcbnew.VIA class.

python
```
via = pcbnew.VIA(board)
via.SetPosition(via_position)
via.SetDrillSize(drill_size)
via.SetViaSize(via_size)
board.Add(via)
```
The `via_position` coordinates define the location of the via, and `drill_size` and `via_size` define the dimensions of the via.

#### Saving the PCB Layout

After making modifications, the script can save the PCB layout using the Save() method of the pcbnew.BOARD class.

python
```
board.Save("/path/to/output/file.kicad_pcb")
```
### Example Code Snippet

Here is a complete example that demonstrates how pcbnew is used to create a simple track and save the modified PCB layout:

python
```
import pcbnew

# Access the current PCB layout
board = pcbnew.GetBoard()

# Define points for the track
start_point = pcbnew.wxPointMM(10, 10)
end_point = pcbnew.wxPointMM(50, 10)

# Create a new track
track = pcbnew.TRACK(board)
track.SetStart(start_point)
track.SetEnd(end_point)
track.SetWidth(pcbnew.FromMM(0.25))
track.SetLayer(pcbnew.F_Cu)  # Place track on the front copper layer
board.Add(track)

# Save the modified PCB layout
board.Save("/path/to/output/file.kicad_pcb")
```
### Summary

- Import pcbnew: To access KiCad's PCB layout functions.
- Access PCB Layout: Using pcbnew.GetBoard().
- Create and Modify Elements: Using classes like pcbnew.TRACK, pcbnew.ZONE_CONTAINER, and pcbnew.VIA.
- Save Layout: Using the Save() method of the pcbnew.BOARD class.
