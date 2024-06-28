# TODO: Add Loop Antenna Option
# TODO: 2 trace widths from the outermost trace. 2 fiducias, diagonally (1 Upper right hand corner and 1 Lower Left hand corner)
# - Loop antenna option (1/2 size of sensor): Use second layer, default layer 2 to a single turn  at ½ the diameter of layer 1. Use layer 1 trace-width for now.
# All imports are correctly placed at the top
import tkinter as tk
import numpy as np
import time
import math  # Import the math module to use its functions
from typing import Callable
from numpy import linspace, pi, cos, sin, arctan2  # Import additional functions for rounded corners


visualization = True  # if you don't have pygame, you can still use the math
saveToFile = True  # if visualization == False! (if True, then just use 's' key)

angleRenderResDefault = np.deg2rad(5)  # angular resolution when rendering continuous (circular) coils
rotateNthDimSpirals = True

# Scientific constants
magneticConstant = 4 * np.pi * 10**-7  # Mu_0 = Newtons / Ampere
ozCopperToMeters = lambda ozCopper: (34.8 * ozCopper * 10**-6)  # convert oz of copper to meters
ozCopperToMM = lambda ozCopper: (34.8 * ozCopper * 10**-3)  # convert oz of copper to mm
mmCopperToOz = lambda mmCopper: ((mmCopper * 10**-3) / 34.8)  # convert mm of copper to oz
umCopperToOz = lambda umCopper: (umCopper / 34.8)  # convert um of copper to oz
RhoCopper = 1.72 * 10**-8  # Ohms * meter

# Code constants
distUnitMult = 1/1000  # convert mm to meters

class _shapeBaseClass:
    """ (static class) base class for defining a shape (and it's associated math) """
    formulaCoefficients: dict[str, tuple[float]]
    stepsPerTurn: int | float # discrete shapes use an int (number of corners), continuous shapes (circularSpiral) uses a float (angle in radians)
    @staticmethod
    def calcPos(itt:int|float,diam:float,clearance:float,traceWidth:float,CCW:bool)->tuple[float, float]:  ... # the modern python way of type-hinting an undefined function
    @staticmethod
    def calcLength(itt:int|float,diam:float,clearance:float,traceWidth:float)->float:  ...
    isDiscrete: bool = True # most of the shapes have a discrete number points/corners/vertices by default. Only continous functions will need a render-resolution parameter
    def __repr__(self): # prints the name of the shape
        return("shape("+(self.__class__.__name__)+")")

# Ensure all calcPos methods return tuples
class squareSpiral(_shapeBaseClass):
    """ (static class) class to hold parameters and functions for square shaped coils """
    formulaCoefficients = {'wheeler' : (2.34, 2.75),
                            'monomial' : (1.62, -1.21, -0.147, 2.40, 1.78, -0.030),
                            'cur_sheet' : (1.27, 2.07, 0.18, 0.13)}
    stepsPerTurn: int = 4 # multiply with number of turns to get 'itt' for functions below
    @staticmethod
    def calcPos(itt: int, diam: float, clearance: float, traceWidth: float, CCW=False) -> tuple[float, float]:
        """ input is the number of steps (corners), 4 steps would be a full circle, generally: itt=(stepsPerTurn*turns)
            output is a 2D coordinate along the spiral, starting outwards """
        spacing = calcTraceSpacing(clearance, traceWidth)
        x =      (1 if (((itt%4)>=2) ^ CCW) else -1)      * (((diam-traceWidth)/2) - ((itt//4)     * spacing))
        y = (1 if (((itt%4)==1) or ((itt%4)==2)) else -1) * (((diam-traceWidth)/2) - (((itt-1)//4) * spacing))
        return(x,y)
    @staticmethod
    def calcLength(itt: int, diam: float, clearance: float, traceWidth: float) -> float:
        """ returns the length of the spiral at a given itt (without iterating, direct calculation) """
        ## NOTE: if the spiral goes beyond the center point and grows larger again (it shouldn't), then the length will be negative). I'm intentionally not fixing that, becuase it makes for good debug info
        spacing = calcTraceSpacing(clearance, traceWidth)
        horLines = (itt//2)
        sumOfWidths = (horLines * (diam-traceWidth)) - ((((horLines-1)*horLines) / 2) * spacing) # length of all hor. lines = (horLines * diam) - triangular number of (horLines-1)
        vertLines = ((itt+1)//2)
        sumOfHeights = (vertLines * (diam-traceWidth)) - ((max(((vertLines-2)*(vertLines-1)) / 2, 0) - 1) * spacing) # length of all vert. lines
        return(sumOfWidths + sumOfHeights)
        ## paper[3] mentioned the formula: 4*turns*diam - 4*turns*tracewidth - (2*turns+1)^2 * (spacing)   but, please review their definitions of outer diameter and spacing before using this!

class circularSpiral(_shapeBaseClass):
    """ (static class) class to hold parameters and functions for circularly shaped coils """
    formulaCoefficients = {'wheeler' : (2.23, 3.45),
                            # the monomial formula does cover circular spirals
                            'cur_sheet' : (1.00, 2.46, 0.00, 0.20)}
    stepsPerTurn: float = 2*np.pi # multiply with number of turns to get 'angle' for functions below
    isDiscrete = False # let the renderer know that this shape needs a resolution parameter
    @staticmethod
    def calcPos(angle: float, diam: float, clearance: float, traceWidth: float, CCW=False) -> tuple[float, float]:
        """ input is an angle in radians, 2pi would be a full circle, generally: angle=(stepsPerTurn*turns)
            output is a 2D coordinate along the spiral, starting outwards """
        spacing = calcTraceSpacing(clearance, traceWidth)
        phaseShift = 0.0 # note: i have already phase-shifted (and inverted) the conventional cirlce by 90deg by using sin() for x and cos() for y (normally you would do it the other way around)
        x = (1 if CCW else -1) * np.sin(angle) * (((diam-traceWidth)/2) - ((angle/(2*np.pi)) * spacing))
        y =         -1         * np.cos(angle) * (((diam-traceWidth)/2) - ((angle/(2*np.pi)) * spacing))
        return(x,y)
    @staticmethod
    def calcLength(angle: float, diam: float, clearance: float, traceWidth: float) -> float:
        """ returns the length of the spiral at a given angle (without iterating, direct calculation) """
        turns = (angle/circularSpiral.stepsPerTurn) # (float)
        return(np.pi * turns * (diam + calcSimpleInnerDiam(turns, diam, clearance, traceWidth, circularSpiral())) / 2) # pi * turns * (diam + innerDiam) / 2 = basically just the circumference of the average diameter (outer+inner)/2

class NthDimSpiral(_shapeBaseClass): # a general class for Nth dimensional polygon spirals. Specify the number of points/corners/sides (6 for hexagon, 8 for octagon, etc.) and provide formulaCoefficients in the subclass
    """ (static class) a base class for Nth dimensional polygon spirals.
        Specify the number of points/corners/sides as .stepsPerTurn (6 for hexagon, 8 for octagon, etc.) and provide .formulaCoefficients in the subclass """
    @classmethod
    def circumDiam(subclass, inscribedDiam: float) -> float:  return(inscribedDiam / np.cos(np.deg2rad(180/subclass.stepsPerTurn))) # just a macro for calculating the diameter of a circumscribed circle (spiral diam is inscribed)
    @classmethod # class methods let you use subclass static variables
    def calcPos(subclass, itt: int, diam: float, clearance: float, traceWidth: float, CCW=False) -> tuple[float, float]:
        """ input is the number of steps (corners), 'stepsPerTurn' steps would be a full circle, generally: itt=(stepsPerTurn*turns)
            output is a 2D coordinate along the spiral, starting outwards """
        ## the easiest way is just to consider it as a circularSpiral, sampled at 6 points per rotation, with the diameter and spacing of a a circumscribed circle (sothat the inscribed circle has the desired diam)
        # return(circularSpiral.calcPos(itt*np.deg2rad(360/subclass.stepsPerTurn), subclass.circumDiam(diam), subclass.circumDiam(clearance), subclass.circumDiam(traceWidth), CCW))
        ## but i wish to have custom phase-shift based on the number of corners (to orient it straight)
        spacing = calcTraceSpacing(subclass.circumDiam(clearance), subclass.circumDiam(traceWidth))
        angle = itt*np.deg2rad(360/subclass.stepsPerTurn)
        circumscribedDiam = subclass.circumDiam(diam-traceWidth)
        phaseShift = ((np.deg2rad(180/subclass.stepsPerTurn)*(-1 if CCW else 1)) if rotateNthDimSpirals else 0.0)
        x = (1 if CCW else -1) * np.sin(angle+phaseShift) * ((circumscribedDiam/2) - ((angle/(2*np.pi)) * spacing))
        y =         -1         * np.cos(angle+phaseShift) * ((circumscribedDiam/2) - ((angle/(2*np.pi)) * spacing))
        return(x,y)
    @classmethod
    def calcLength(subclass, itt: int, diam: float, clearance: float, traceWidth: float) -> float:
        """ returns the length of the spiral at a given itt (without iterating, direct calculation) """
        return(itt * np.sin(np.deg2rad(180/subclass.stepsPerTurn)) * (subclass.circumDiam(diam) + calcSimpleInnerDiam(itt/subclass.stepsPerTurn, subclass.circumDiam(diam), subclass.circumDiam(clearance), subclass.circumDiam(traceWidth), NthDimSpiral())) / 2)
        ## similar to the circularSpiral, the perimiter (circumference) of an NthDimSpiral can be seem as the perimiter of the average polygon. Then just simplify the equations after inserting itt (calculating turn variable is a little extra)

class hexagonSpiral(NthDimSpiral):
    """ (static class) class to hold parameters and functions for hexagonally-shaped (sortof, the angles are not actually 60deg) coils """
    formulaCoefficients = {'wheeler' : (2.33, 3.82),
                            'monomial' : (1.28, -1.24, -0.174, 2.47, 1.77, -0.049),
                            'cur_sheet' : (1.09, 2.23, 0.00, 0.17)}
    stepsPerTurn: int = 6

class octagonSpiral(NthDimSpiral):
    """ (static class) class to hold parameters and functions for octagonally-shaped (sortof, the angles are not actually 45deg) coils """
    formulaCoefficients = {'wheeler' : (2.25, 3.55),
                            'monomial' : (1.33, -1.21, -0.163, 2.43, 1.75, -0.049),
                            'cur_sheet' : (1.07, 2.29, 0.00, 0.19)}
    stepsPerTurn: int = 8

shapes = {'square': squareSpiral(), 'hexagon': hexagonSpiral(), 'octagon': octagonSpiral(), 'circle': circularSpiral()}

def calcSimpleInnerDiam(turns: int, diam: float, clearance: float, traceWidth: float, shape: _shapeBaseClass) -> float:
    spacing = calcTraceSpacing(clearance, traceWidth)
    return (((diam / 2) - ((turns - (1 if (isinstance(shape, squareSpiral)) else 0)) * spacing) - traceWidth) * 2)

def _calcTrueDiamOffset(clearance: float, traceWidth: float, shape: _shapeBaseClass) -> float:
    if (isinstance(shape, squareSpiral)):
        return 0.0
    else:
        return calcTraceSpacing(clearance, traceWidth) / 4

def calcTrueInnerDiam(turns: int, diam: float, clearance: float, traceWidth: float, shape: _shapeBaseClass) -> float:
    return calcSimpleInnerDiam(turns, diam, clearance, traceWidth, shape) + (_calcTrueDiamOffset(clearance, traceWidth, shape) * 2)

def calcTrueDiam(diam: float, clearance: float, traceWidth: float, shape: _shapeBaseClass) -> float:
    return (diam - (_calcTrueDiamOffset(clearance, traceWidth, shape) * 2))

def calcReturnTraceLength(turns: int, clearance: float, traceWidth: float) -> float:
    return (turns * calcTraceSpacing(clearance, traceWidth))

def calcTraceSpacing(clearance: float, traceWidth: float) -> float:
    return (clearance + traceWidth)

def calcCoilTraceResistance(turns: int, diam: float, clearance: float, traceWidth: float, resistConst: float, shape: _shapeBaseClass) -> float:
    coilLength = shape.calcLength(shape.stepsPerTurn * turns, diam, clearance, traceWidth) * distUnitMult
    coilResistance = resistConst * (coilLength / (traceWidth * distUnitMult))
    return coilResistance

def calcTotalResistance(turns: int, diam: float, clearance: float, traceWidth: float, layers: int, resistConst: float, shape: _shapeBaseClass) -> float:
    singleResist = calcCoilTraceResistance(turns, diam, clearance, traceWidth, resistConst, shape)
    coilResistance = singleResist * layers
    return coilResistance

def calcLayerSpacing(layers: int, PCBthickness: float, copperThickness: float) -> float:
    if (layers <= 1):
        return 0.0
    return ((PCBthickness - copperThickness) / (layers - 1))

def calcInductanceSingleLayer(turns: int, diam: float, clearance: float, traceWidth: float, shape: _shapeBaseClass, formula: str) -> float:
    if (formula not in shape.formulaCoefficients):
        print("could not calcInductanceSingleLayer(), for shape=", shape, " and formula=", formula)
        return (-1.0)
    trueInnerDiamM = calcTrueInnerDiam(turns, diam, clearance, traceWidth, shape) * distUnitMult
    trueDiamM = calcTrueDiam(diam, clearance, traceWidth, shape) * distUnitMult
    fillFactor = (trueDiamM - trueInnerDiamM) / (trueDiamM + trueInnerDiamM)
    averageDiamM = ((trueDiamM + trueInnerDiamM) / 2)
    coeff = shape.formulaCoefficients[formula]
    if (formula == 'wheeler'):
        return (coeff[0] * magneticConstant * (turns**2) * averageDiamM / (1 + (coeff[1] * fillFactor)))
    elif (formula == 'monomial'):
        outputMult = (10**-6)
        return (outputMult * coeff[0] * (trueDiamM**coeff[1]) * ((traceWidth * distUnitMult)**coeff[2]) * (averageDiamM**coeff[3]) * (turns**coeff[4]) * (clearance**coeff[5]))
    elif (formula == 'cur_sheet'):
        return ((coeff[0] * magneticConstant * (turns**2) * averageDiamM * (np.log(coeff[1] / fillFactor) + (coeff[2] * fillFactor) + (coeff[3] * (fillFactor**2)))) / 2)
    else:
        print("impossible point reached in calcInductanceSingleLayer(), check the formulaCoefficients formula names in this function!")
        return (-1.0)

def calcInductanceMultilayer(turns: int, diam: float, clearance: float, traceWidth: float, layers: int, layerSpacing: float, shape: _shapeBaseClass, formula: str) -> float:
    singleInduct = calcInductanceSingleLayer(turns, diam, clearance, traceWidth, shape, formula)
    if (singleInduct < 0):
        print("can't calcInductanceMultilayer(), calcInductanceSingleLayer() returned <0:", singleInduct)
        return (-1.0)
    couplingConstant_D = (1.025485443, -0.201166582)
    sumOfSpacings = layerSpacing * ((layers * (layers + 1) * (layers - 1)) / 6)
    triangularNumber = (layers * (layers - 1)) / 2
    sumOfCouplingFactors = (couplingConstant_D[1] * sumOfSpacings) + (triangularNumber * couplingConstant_D[0])
    totalInduct = singleInduct * (layers + 2 * sumOfCouplingFactors)
    return totalInduct

def generateCoilFilename(coil: 'coilClass') -> str:
    filename = coil.shape.__class__.__name__[0:2]
    filename += '_di' + str(int(round(coil.diam, 0)))
    filename += '_tu' + str(coil.turns)
    filename += '_wi' + str(int(round(coil.traceWidth * 1000, 0)))
    filename += '_cl' + str(int(round(coil.clearance * 1000, 0)))
    filename += '_cT' + str(int(round(coil.copperThickness * 1000, 0)))
    if (coil.layers > 1):
        filename += '_La' + str(coil.layers)
        filename += '_Pt' + str(int(round(coil.PCBthickness * 1000, 0)))
    filename += '_Re' + str(int(round(coil.calcTotalResistance() * 1000, 0)))
    filename += '_In' + str(int(round(coil.calcInductance() * 1000000000, 0)))
    return filename

class coilClass:
    def __init__(self, turns, diam, clearance, traceWidth, layers=1, PCBthickness=1.6, copperThickness=0.035, shape='circle', formula='cur_sheet', CCW=False, loop_enabled=False, loop_diameter=0.0, loop_shape='circle'):
        self.turns = turns
        self.diam = diam
        self.clearance = clearance
        self.traceWidth = traceWidth
        self.layers = layers
        self.PCBthickness = PCBthickness
        self.copperThickness = copperThickness
        if shape in shapes:
            self.shape = shapes[shape]
        else:
            raise ValueError(f"Shape {shape} is not recognized. Available shapes are: {list(shapes.keys())}")
        self.formula = formula
        self.CCW = CCW
        self.loop_enabled = loop_enabled
        self.loop_diameter = loop_diameter
        if loop_shape in shapes:
            self.loop_shape = loop_shape  # Store the key
        else:
            raise ValueError(f"Loop shape {loop_shape} is not recognized. Available shapes are: {list(shapes.keys())}")

    def calcCoilTraceLength(self):
        return self.shape.calcLength(self.turns * self.shape.stepsPerTurn, self.diam, self.clearance, self.traceWidth) * self.layers

    def calcSimpleInnerDiam(self):
        return calcSimpleInnerDiam(self.turns, self.diam, self.clearance, self.traceWidth, self.shape)

    def calcTrueInnerDiam(self):
        return calcTrueInnerDiam(self.turns, self.diam, self.clearance, self.traceWidth, self.shape)

    def calcTrueDiam(self):
        return calcTrueDiam(self.diam, self.clearance, self.traceWidth, self.shape)

    def _calcTrueDiamOffset(self):
        return _calcTrueDiamOffset(self.clearance, self.traceWidth, self.shape)

    def calcTraceSpacing(self):
        return calcTraceSpacing(self.clearance, self.traceWidth)

    def calcReturnTraceLength(self):
        return calcReturnTraceLength(self.turns, self.clearance, self.traceWidth) if ((self.layers % 2) != 0) else 0.0

    def calcTotalResistance(self):
        return calcTotalResistance(self.turns, self.diam, self.clearance, self.traceWidth, self.layers, RhoCopper / (self.copperThickness * distUnitMult), self.shape)

    def calcLayerSpacing(self):
        return calcLayerSpacing(self.layers, self.PCBthickness, self.copperThickness)

    def calcInductanceSingleLayer(self):
        return calcInductanceSingleLayer(self.turns, self.diam, self.clearance, self.traceWidth, self.shape, self.formula)

    def calcInductance(self):
        return self.calcInductanceSingleLayer() if (self.layers == 1) else calcInductanceMultilayer(self.turns, self.diam, self.clearance, self.traceWidth, self.layers, self.calcLayerSpacing(), self.shape, self.formula)

    def renderAsCoordinateList(self, reverseDirection=False, angleResOverride: float = None):
        coordinates = []
        if self.shape.isDiscrete:
            if angleResOverride is not None:
                print("renderAsCoordinateList() ignoring angleResOverride, shape not circular")
            coordinates = [self.shape.calcPos(i, self.diam, self.clearance, self.traceWidth, self.CCW ^ reverseDirection) for i in range(self.shape.stepsPerTurn * self.turns + 1)]
            if len(coordinates) % 10 == 0:  # Example condition: print only if the number of coordinates is a multiple of 10
                print(f"renderAsCoordinateList (Discrete): {len(coordinates)} points")
        else:
            angleRes = angleResOverride if angleResOverride else angleRenderResDefault
            coordinates = [self.shape.calcPos(i * angleRes, self.diam, self.clearance, self.traceWidth, self.CCW ^ reverseDirection) for i in range(int(round((self.shape.stepsPerTurn * self.turns) / angleRes, 0)) + 1)]
            if len(coordinates) % 10 == 0:  # Same example condition
                print(f"renderAsCoordinateList (Continuous): {len(coordinates)} points")

        # Convert list of points to list of line segments
        line_segments = []
        for i in range(len(coordinates) - 1):
            line_segments.append((coordinates[i], coordinates[i + 1]))

        return line_segments

    def render_loop_antenna(self):
        if not self.loop_enabled:
            print("Loop antenna is disabled.")
            return []

        print("Available shapes:", shapes.keys())
        print("Current loop shape:", self.loop_shape)
        if self.loop_shape not in shapes:
            print(f"Error: Shape {self.loop_shape} not recognized.")
            return []
        
        shape_instance = shapes[self.loop_shape]        
        points = []
        true_outer_diam = self.calcTrueDiam()  
        # Adjusting the offset to move the loop next to the coil
        x_offset = (true_outer_diam / 2) + 5 + (self.loop_diameter / 2)
        y_offset = (true_outer_diam / 2)  - 20 # KEEP THIS, it sets the y_offset to the middle of the coil
        loop_radius = self.loop_diameter / 2
        adjusted_radius = loop_radius - (self.traceWidth / 2)  # Adjust radius to account for trace width
        
        if isinstance(shape_instance, squareSpiral):
            side_length = adjusted_radius * 2  # Full diameter to side length for square
            half_side = side_length / 2
            corner_radius = 0.5  # Define the radius of the corner curve
            points = [
                (x_offset + half_side - corner_radius, y_offset + half_side),
                (x_offset + half_side, y_offset + half_side - corner_radius),
                (x_offset + half_side, y_offset - half_side + corner_radius),
                (x_offset + half_side - corner_radius, y_offset - half_side),
                (x_offset - half_side + corner_radius, y_offset - half_side),
                (x_offset - half_side, y_offset - half_side + corner_radius),
                (x_offset - half_side, y_offset + half_side - corner_radius),
                (x_offset - half_side + corner_radius, y_offset + half_side),
                (x_offset + half_side - corner_radius, y_offset + half_side)  # Closing the square with a smooth corner
            ]
        elif isinstance(shape_instance, circularSpiral):
            # Increase the resolution by using a smaller step size for angle increment
            step_size = 0.01  # smaller step size for higher resolution
            points = [(adjusted_radius * np.cos(2 * np.pi * step * step_size) + x_offset, adjusted_radius * np.sin(2 * np.pi * step * step_size) + y_offset) for step in range(int(1/step_size) + 1)]
        elif self.loop_shape == 'hexagonalSpiral':
            num_sides = 6
            angle_increment = 360 / num_sides
            points = [(x_offset + adjusted_radius * np.cos(math.radians(i * angle_increment)), y_offset + adjusted_radius * np.sin(math.radians(i * angle_increment))) for i in range(num_sides + 1)]
        else:
            print(f"Shape type {type(shape_instance)} not handled.")
        
        return points

    def generateCoilFilename(self):
        return(generateCoilFilename(self))

    def saveDXF(self) -> list[str]:
        import DXFexporter as DXFexp
        filenames: list[str] = []
        for outputFormat in DXFexp.DXFoutputFormats:
            filenames += DXFexp.saveDXF(self, outputFormat)
        return(filenames)

    def to_excel(self, filename:str = None) -> str:
        """ produce an excel file with only 1 row of data; this coil """
        import excelExporter as excExp
        if(filename is None):  filename = self.generateCoilFilename() + excExp.fileExtension
        excExp.exportCoils([self,], filename)

    def imwrite(self, *arg) -> list[np.ndarray]:
        """ just a macro that imports cv2exporter.py and runs .imwrite() with the provided arguments """
        import cv2exporter as cv2exp
        cv2exp.imwrite(self, *arg)


def update_coil_params(params):
    global coil, renderedLineLists, drawer, updated
    coil = coilClass(
        turns=int(params['Turns']),
        diam=float(params['Diameter']),
        clearance=float(params['Width between traces']),
        traceWidth=float(params['Trace Width']),
        layers=int(params['Layers']),
        PCBthickness=float(params['PCB Thickness']),
        copperThickness=float(params['Copper Thickness']),
        shape=params['Shape'],
        formula=params['Formula'],
        loop_enabled=params.get('loop_enabled', False),
        loop_diameter=float(params.get('loop_diameter', 0)),
        loop_shape=params.get('loop_shape', 'circle')  # Ensure loop_shape is passed correctly
    )
    renderedLineLists = [coil.renderAsCoordinateList()]
    if coil.loop_enabled:
        loop_antenna_coords = coil.render_loop_antenna()
        if not loop_antenna_coords:
            print("Warning: Loop antenna coordinates are empty")
        renderedLineLists.append(loop_antenna_coords)
    else:
        renderedLineLists.append([])
    drawer.localVar = coil
    drawer.localVarUpdated = True
    drawer.debugText = drawer.makeDebugText(coil)
    drawer.lastFilename = coil.generateCoilFilename()
    updated = True  # Set the update flag to true after updating the coil parameters      
    


# Helper function to flatten nested tuples
def flatten_and_convert_to_floats(point):
    if isinstance(point, (list, tuple)) and len(point) == 2:
        # Check if the elements within the point are also tuples
        if isinstance(point[0], (list, tuple)):
            point = (point[0][0], point[0][1])
        elif isinstance(point[1], (list, tuple)):
            point = (point[1][0], point[1][1])
        return (float(point[0]), float(point[1]))
    else:
        raise ValueError(f"Invalid point format: {point}")

def main():
    from tkinter_coil_gui import CoilParameterGUI
    global coil, renderedLineLists, drawer

    root = tk.Tk()
    app = CoilParameterGUI(root, update_coil_params)
    root.after(0, root.deiconify)
    
    initial_params = {
        "Turns": 9, "Diameter": 40, "Width between traces": 0.15, "Trace Width": 0.9, 
        "Layers": 1, "PCB Thickness": 0.6, "Copper Thickness": 0.030, 
        "Shape": 'square', "Formula": 'cur_sheet', "loop_enabled": False, "loop_diameter": 0.0, "loop_shape": 'circle'
    }

    if visualization:
        import pygameRenderer as PR
        import pygameUI as UI

        windowHandler = PR.pygameWindowHandler([1280, 720], "PCB coil generator", "fancy/icon.png")
        drawer = PR.pygameDrawer(windowHandler)
        drawer.windowHandler = windowHandler  # Assign the window handler
        update_coil_params(initial_params)

        listUpdated = True  # Flag to track if the list has been updated

        while windowHandler.keepRunning:
            loopStart = time.time()
            drawer.renderBG()

            # Ensure the elements in renderedLineLists are tuples of tuples containing floats
            formattedLineLists = []
            for line in renderedLineLists:
                formattedLine = []
                for point in line:
                    try:
                        formattedLine.append(flatten_and_convert_to_floats(point))
                    except ValueError as e:
                        print(e)
                formattedLineLists.append(tuple(formattedLine))

            drawer.drawLineList(formattedLineLists)  # Always draw the coil
            drawer.renderFG()
            windowHandler.frameRefresh()
            UI.handleAllWindowEvents(drawer)

            if drawer.localVarUpdated:
                drawer.localVarUpdated = False
                listUpdated = True  # Set the flag when localVar is updated

            loopEnd = time.time()
            sleep_time = max(0, (1 / 60) - (loopEnd - loopStart))
            time.sleep(sleep_time)

            root.update()

    else:
        update_coil_params(initial_params)
        print("coil details:")
        print(f"resistance [mOhm]: {round(coil.calcTotalResistance() * 1000, 3)}")
        print(f"inductance [uH]: {round(coil.calcInductance() * 1000000, 3)}")
        print(f"induct/resist [uH/Ohm]: {round(coil.calcInductance() * 1000000 / coil.calcTotalResistance(), 3)}")
        print(f"induct/radius [uH/mm]: {round(coil.calcInductance() * 1000000 / (coil.diam / 2), 3)}")

if __name__ == "__main__":
    main()
