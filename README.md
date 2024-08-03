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

## 1. Introduction
Coilgen V3 is a powerful tool for designing and generating coil patterns. This version includes several improvements and new features over previous versions.

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

[Insert image of the Coilgen V3 interface here]

### Coil Parameters

The main window allows you to set various parameters for your coil design:

- **Turns**: Number of turns in the coil
- **Diameter**: Diameter of the coil (mm)
- **Width between traces**: Spacing between coil traces (mm)
- **Trace Width**: Width of the coil trace (mm)
- **Layers**: Number of layers in the coil
- **PCB Thickness**: Thickness of the PCB (mm)
- **Copper Thickness**: Thickness of the copper layer (mm)
- **Shape**: Choose from square, hexagon, octagon, or circle
- **Formula**: Select the formula for calculations (cur_sheet, monomial, or wheeler)

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
- Issue: Coil design is not valid.
  Solution: Use the geometry checking feature to identify and correct errors.
- Issue: Exported file is not in the correct format.
  Solution: Check the export options and adjust as needed.

## 10. FAQ
Q: What is the purpose of Coilgen V3?
A: Coilgen V3 is a tool for designing and generating coil patterns.

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
Coilgen V3 includes a feature for estimating the resonant frequency of the designed coil pattern. This feature uses a linear model to estimate the frequency based on the coil design parameters.

### Linear Model
The linear model used for resonant frequency estimation is as follows:

f = −0.9962700648151179 × L + 11.897391483473740

where f is the estimated resonant frequency and L is the coil design parameter.

### Example Data
The following table shows example data for the resonant frequency estimation feature:

| Trace Length (µm) | Frequency (MHz) |
|-------------------|-----------------|
| 268965.93         | 0.6             |
| 119384.76         | 1.3             |
| 61132.97          | 2.5             |
| 3355.24           | 44.7            |
| 845.31            | 177.4           |
| 3355.240          | 44.7            |
| 845.312           | 177.4           |
| 214.376           | 699.7           |
| 55.118            | 2721.4          |
| 2565.401          | 58.5            |
| 647.700           | 231.6           |
| 178.308           | 841.2           |
| 39.624            | 3785.6          |
| 2176.272          | 68.9            |
| 550.469           | 272.5           |
| 154.229           | 972.6           |
| 33.528            | 4473.9          |
| 96012.00          | 1.6             |
| 29763.72          | 5.0             |
