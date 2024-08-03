# Coilgen V3 Documentation

## Table of Contents
1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Getting Started](#3-getting-started)
4. [Features](#4-features)
5. [User Interface](#5-user-interface)
6. [Usage Guide](#6-usage-guide)
7. [Configuration](#7-configuration)
8. [Export Options](#8-export-options)
9. [Troubleshooting](#9-troubleshooting)
10. [FAQ](#10-faq)
11. [Changelog](#11-changelog)
12. [Resonant Frequency Estimation](#12-resonant-frequency-estimation)
13. [Square Coil Geometry](#13-square-coil-geometry)
14. [Acknowledgements](#14-acknowledgements)

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

The Coilgen V3 user interface is designed to be intuitive and user-friendly. Here's an overview of the main components:

![image](https://github.com/user-attachments/assets/1d8bbf4d-86a5-4e66-b63c-118846bcee9b)

### Coil Parameters

The main window allows you to set various parameters for your coil design:

- **Turns**: Number of turns in the coil
- **Diameter**: Diameter of the coil (mm)a
- **Width between traces**: Spacing between coil traces (mm)
- **Trace Width**: Width of the coil trace (mm)
- **Layers**: Number of layers in the coil
- **PCB Thickness**: Thickness of the PCB (mm)
- **Copper Thickness**: Thickness of the copper layer (mm)
- **Shape**: 
    - Square
    - Hexagon
    - Octagon
    - Circle
- **Formula**: Select the formula for calculations (cur_sheet, monomial, or wheeler)

### Coil Design Parameters

Coilgen V3 allows you to customize various parameters for your SansEC coil design. Here's a detailed explanation of each parameter:

1. **Turns**: The number of complete revolutions the coil makes. More turns generally increase inductance but also increase resistance and self-capacitance. For SansEC sensors, this affects the resonant frequency and sensitivity.

2. **Diameter**: The overall diameter of the coil in millimeters. This parameter influences the coil's inductance and its sensing area. Larger diameters typically result in higher inductance and a larger sensing area, but may reduce the spatial resolution of the sensor.

3. **Width between traces**: The space between adjacent turns of the coil, measured in millimeters. This affects the mutual inductance between turns and the overall capacitance of the coil. Wider spacing can reduce parasitic capacitance but may decrease the overall inductance.

4. **Trace Width**: The width of the conductive path forming the coil, measured in millimeters. Wider traces reduce resistance but increase the overall size of the coil. For SansEC sensors, this parameter can affect the Q-factor and the sensor's sensitivity.

5. **Layers**: The number of PCB layers used for the coil. SansEC coils can be single or multi-layer. Multi-layer designs can achieve higher inductance in a smaller footprint but may increase manufacturing complexity and cost.

6. **PCB Thickness**: The thickness of the PCB substrate in millimeters. This affects the distance between layers in multi-layer designs and can influence the coil's parasitic capacitance and overall performance.

7. **Copper Thickness**: The thickness of the copper traces in millimeters. Thicker copper reduces resistance but may increase manufacturing costs. For SansEC sensors, this can affect the Q-factor and the sensor's sensitivity to surface phenomena.

8. **Shape**: The geometric shape of the coil. Options include:
   - Square: Offers high inductance per unit area and is easy to manufacture.
   - Hexagon: Provides a balance between inductance and circular symmetry.
   - Octagon: Closer approximation to a circular coil while maintaining relatively simple manufacturing.
   - Circle: Offers the most uniform magnetic field but may be more challenging to manufacture.

9. **Formula**: The calculation method used for estimating coil properties. Options include:
   - cur_sheet: Current sheet approximation, suitable for closely wound coils.
   - monomial: Uses fitted monomial expressions, generally accurate for a wide range of geometries.
   - wheeler: Wheeler's approximation, often used for its simplicity and reasonable accuracy.

These parameters allow for fine-tuning of the SansEC coil design to meet specific requirements for resonant frequency, sensing area, sensitivity, and manufacturability. The optimal values depend on the intended application of the SansEC sensor.

### Loop Antenna Options

- **Loop Antenna Layer**: Choose between "Loop Antenna with Pads" or "Loop Antenna with Pads 2 Layer"
- **Loop Diameter**: Option to set as "Auto" or "Custom"
  - When "Custom" is selected, you can input a specific diameter for the loop antenna

### Export Options

You can choose which files to export:
- SVG
- Gerber
- DXF

Additionally, you can select whether to export the coil, the loop, or both.

### Resonant Frequency Estimation

The interface includes a section for resonant frequency estimation:
- Display of the estimated resonant frequency based on current parameters
- Input field for desired resonant frequency
- Button to calculate the diameter needed for a specific frequency

### Update and Export Buttons

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

![Figure_1](https://github.com/user-attachments/assets/c82b1e01-2ae0-4663-a8fc-92451234c56b)

This model provides a reasonable approximation of the resonant frequency for a wide range of SansEC coil designs. However, it's important to note that the accuracy of the estimation depends on the validity of the assumptions and the quality of the measurement data used to develop the model. For critical applications, it's recommended to validate the estimated resonant frequency through actual measurements.

## 13. Square Coil Geometry

The square coil geometry is a common design choice for coil patterns. Research has shown that square coils can exhibit improved performance compared to circular coils in certain applications. For more information on the benefits and design considerations of square coils, refer to the following research paper: [Insert paper reference].

## 14. Acknowledgements

Coilgen V3 builds upon the work of other open-source projects. I would like to acknowledge the following contribution:

- The Python calculations and Pygame rendering in Coilgen V3 are based on the [PCBcoilGenerator](https://github.com/thijses/PCBcoilGenerator) project by thijses. I am grateful for their work, which has been instrumental in developing certain aspects of Coilgen V3.

I encourage users to check out the PCBcoilGenerator project for more information on the underlying calculations and rendering techniques used in Coilgen V3.
