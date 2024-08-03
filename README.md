# Coilgen V3 Documentation

## Table of Contents
1. Introduction
2. Installation
3. Getting Started
4. Features
5. User Interface
6. Usage Guide
7. Configuration
8. Export Options
9. Troubleshooting
10. FAQ
11. Changelog
12. Resonant Frequency Estimation
13. Square Coil Geometry

## 1. Introduction
Coilgen V3 is a powerful tool for designing and generating coil patterns. This version includes several improvements and new features over previous versions.

## 2. Installation
### Windows Installation
1. Download the installation package from the official website.
2. Run the installer and follow the prompts to complete the installation.
3. Once installed, launch Coilgen V3 from the Start menu.

### Linux Installation
1. Download the installation package from the official website.
2. Extract the contents of the package to a directory of your choice.
3. Navigate to the extracted directory and run the coilgen executable to launch the application.

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
The Coilgen V3 UI consists of the following elements:
- Menu bar: Provides access to various menus and options.
- Toolbar: Offers quick access to frequently used tools and features.
- Design area: Displays the coil pattern and allows for interactive design and customization.
- Parameter panel: Allows for adjustment of coil design parameters.
- Status bar: Displays information about the current design and application status.

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

## 13. Square Coil Geometry

The square coil geometry in Coilgen V3 is designed based on principles outlined in the paper "Inductance calculation and layout optimization for planar spiral inductors". This design ensures optimal performance and efficiency for the generated coil patterns.

### Key Geometric Principles

1. **Coil Shape**: The square shape is chosen for its balance between inductance density and ease of fabrication. Square coils offer higher inductance per unit area compared to circular coils, while still maintaining relatively simple manufacturing processes.

2. **Turn Spacing**: The spacing between turns is optimized to balance between maximizing mutual inductance (which increases with tighter spacing) and minimizing parasitic capacitance (which decreases with wider spacing).

3. **Conductor Width**: The width of the conductor is carefully calculated to minimize resistance while considering skin effect at the intended operating frequency.

4. **Number of Turns**: The number of turns is determined based on the desired inductance value and the available area, taking into account that inductance increases approximately with the square of the number of turns.

5. **Inner Diameter**: The inner diameter is optimized to maximize the Q-factor of the inductor. A larger inner diameter reduces the negative impact of the innermost turns on the overall inductance.

6. **Outer Diameter**: The outer diameter is constrained by the available area and the desired inductance value. It's optimized to achieve the target inductance while maintaining a compact design.

### Optimization Process

Coilgen V3 uses an iterative optimization process to determine the best geometric parameters for the square coil. This process involves:

1. Initial parameter estimation based on the target inductance and available area.
2. Calculation of inductance using accurate models that account for mutual inductance between turns.
3. Adjustment of parameters to minimize resistance and maximize Q-factor.
4. Verification that the design meets all specified constraints.

This optimization ensures that the generated square coil designs provide high performance and efficiency for the intended application.
