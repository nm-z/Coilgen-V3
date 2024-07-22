
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
from prettytable import PrettyTable
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# trace too extended

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
    isDiscrete = True # most of the shapes have a discrete number points/corners/vertices by default. Only continous functions will need a render-resolution parameter
    def __repr__(self): # prints the name of the shape
        return("shape("+(self.__class__.__name__)+")")


def calcTraceSpacing(clearance: float, traceWidth: float) -> float:
    return clearance + traceWidth



# Ensure all calcPos methods return tuples
class squareSpiral(_shapeBaseClass):
    """ (static class) class to hold parameters and functions for square shaped coils """
    formulaCoefficients = {'wheeler' : (2.34, 2.75),
                            'monomial' : (1.62, -1.21, -0.147, 2.40, 1.78, -0.030),
                            'cur_sheet' : (1.27, 2.07, 0.18, 0.13)}
    stepsPerTurn: int = 4 # multiply with number of turns to get 'itt' for functions below

    @staticmethod
    def calcPos(itt, diam, clearance, traceWidth, CCW=False):
        r_outer = diam / 2
        r_inner = calcSimpleInnerDiam(itt / 4, diam, clearance, traceWidth, squareSpiral()) / 2
        
        spacing = calcTraceSpacing(clearance, traceWidth)

        r = r_outer - (itt // 4) * spacing
        next_r = r - spacing

        if not CCW:
            if itt % 4 == 0:
                return (r, -r)
            elif itt % 4 == 1:
                return (-r, -r)
            elif itt % 4 == 2:
                return (-r, r)
            else:
                return (r, r)
        else:
            if itt % 4 == 0:
                return (r, r)
            elif itt % 4 == 1:
                return (-r, r)
            elif itt % 4 == 2:
                return (-r, -r)
            else:
                return (r, -r)
            


    @staticmethod
    def calcPos_alt(itt: int, diam: float, clearance: float, traceWidth: float, CCW=False) -> tuple[float, float]:
        """ input is the number of steps (corners), 4 steps would be a full circle, generally: itt=(stepsPerTurn*turns)
            output is a 2D coordinate along the spiral, starting outwards """
        spacing = calcTraceSpacing(clearance, traceWidth)
        x =      (1 if (((itt%4)>=2) ^ CCW) else -1)      * (((diam-traceWidth)/2) - ((itt//4)     * spacing))
        y = (1 if (((itt%4)==1) or ((itt%4)==2)) else -1) * (((diam-traceWidth)/2) - (((itt-1)//4) * spacing))
        return(x,y)


    @staticmethod
    def calcLength(itt: float, diam: float, clearance: float, traceWidth: float) -> float:
        n_turns = itt / 4  # Convert steps to turns
        r_outer = diam / 2
        r_inner = calcSimpleInnerDiam(n_turns, diam, clearance, traceWidth, squareSpiral()) / 2
        
        if n_turns > 1:
            delta_r = (r_outer - r_inner) / (n_turns - 1)
        else:
            delta_r = 2 * traceWidth
        
        length = 0.0
        for i in range(int(n_turns)):
            r = r_outer - i * delta_r
            length += 4 * (2 * r)  # Perimeter of the square at this turn
        
        # Add any partial turn
        if n_turns % 1 > 0:
            r = r_outer - int(n_turns) * delta_r
            length += 4 * (2 * r) * (n_turns % 1)
        
        return length

    @staticmethod
    def calcLength_alt(itt: int, diam: float, clearance: float, traceWidth: float) -> float:
        """ returns the length of the spiral at a given itt (without iterating, direct calculation) """
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
        print(Fore.RED + Style.BRIGHT + f"could not calcInductanceSingleLayer(), for shape={shape} and formula={formula}" + Style.RESET_ALL)
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
        print(Fore.RED + Style.BRIGHT + "impossible point reached in calcInductanceSingleLayer(), check the formulaCoefficients formula names in this function!" + Style.RESET_ALL)
        return (-1.0)

def calcInductanceMultilayer(turns: int, diam: float, clearance: float, traceWidth: float, layers: int, layerSpacing: float, shape: _shapeBaseClass, formula: str) -> float:
    singleInduct = calcInductanceSingleLayer(turns, diam, clearance, traceWidth, shape, formula)
    if (singleInduct < 0):
        print(Fore.RED + Style.BRIGHT + f"can't calcInductanceMultilayer(), calcInductanceSingleLayer() returned <0: {singleInduct}" + Style.RESET_ALL)
        return (-1.0)
    couplingConstant_D = (1.025485443, -0.201166582)
    sumOfSpacings = layerSpacing * ((layers * (layers + 1) * (layers - 1)) / 6)
    triangularNumber = (layers * (layers - 1)) / 2
    sumOfCouplingFactors = (couplingConstant_D[1] * sumOfSpacings) + (triangularNumber * couplingConstant_D[0])
    totalInduct = singleInduct * (layers + 2 * sumOfCouplingFactors)
    return totalInduct

def generateCoilFilename(coil: 'coilClass') -> str:
    filename = coil.shape.__class__.__name__[0:2].upper()
    filename += f'_di{int(coil.diam)}'
    filename += f'_tu{coil.turns}'
    filename += f'_wi{int(coil.traceWidth * 1000)}'
    filename += f'_cl{int(coil.clearance * 1000)}'
    filename += f'_cT{int(coil.copperThickness * 1000)}'
    if coil.layers > 1:
        filename += f'_La{coil.layers}'
        filename += f'_Pt{int(coil.PCBthickness * 1000)}'
    filename += f'_Re{int(coil.calcTotalResistance() * 1000)}'
    filename += f'_In{int(coil.calcInductance() * 1000000)}'
    return filename

class coilClass:
    def __init__(self, turns, diam, clearance, traceWidth, layers=1, PCBthickness=1.6, copperThickness=0.035, shape='circle', formula='cur_sheet', CCW=False, loop_enabled=False, loop_diameter=0.0, loop_shape='circle', calcPos=None, calcLength=None):
        self.turns = turns
        self.diam = diam - (traceWidth)
        self.clearance = clearance
        self.traceWidth = traceWidth
        self.layers = layers
        self.PCBthickness = PCBthickness
        self.copperThickness = copperThickness
        if shape in shapes:
            self.shape = shapes[shape]
        else:
            print(Fore.RED + Style.BRIGHT + f"Shape {shape} is not recognized. Available shapes are: {list(shapes.keys())}" + Style.RESET_ALL)
            raise ValueError(f"Shape {shape} is not recognized. Available shapes are: {list(shapes.keys())}")
        self.formula = formula
        self.CCW = CCW
        self.loop_enabled = loop_enabled
        self.loop_diameter = loop_diameter
        if loop_shape in shapes:
            self.loop_shape = loop_shape  # Store the key
        else:
            print(Fore.RED + Style.BRIGHT + f"Loop shape {loop_shape} is not recognized. Available shapes are: {list(shapes.keys())}" + Style.RESET_ALL)
            raise ValueError(f"Loop shape {loop_shape} is not recognized. Available shapes are: {list(shapes.keys())}")
        self.calcPos = calcPos if calcPos else self.shape.calcPos
        self.calcLength = calcLength if calcLength else self.shape.calcLength

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


    def calcResonantFrequency(self, capacitance):
        """
        Calculate the resonant frequency of the coil using the actual trace length.
        
        Parameters:
        self.traceWidth: The trace width in mm.
        self.calcCoilTraceLength(): The trace length in mm.
        
        Returns:
        float: The resonant frequency in MHz.
        """
        traceWidth = self.traceWidth
        trace_length = self.calcCoilTraceLength()

        actual_trace_length = traceWidth + trace_length

        # Linear model parameters
        slope = -0.9962700648151179283473766190581955015659332275390625
        intercept = 11.897391483473739981491235084831714630126953125

        # Calculate resonant frequency
        log_frequency = slope * np.log(actual_trace_length) + intercept
        resonant_frequency = np.exp(log_frequency)
        
        return resonant_frequency


# Add this method to the coilClass in PCBcoilV2.py

    def calculate_diameter_for_frequency(self, target_frequency):
        """
        Calculate the diameter needed to achieve the target resonant frequency.
        
        Parameters:
        target_frequency: The desired resonant frequency in MHz.
        
        Returns:
        tuple: (suggested diameter in mm, actual achieved frequency in MHz)
        """
        # Linear model parameters
        slope = -0.9962700648151179283473766190581955015659332275390625
        intercept = 11.897391483473739981491235084831714630126953125

        # Reverse the equation to get the required trace length
        log_frequency = np.log(target_frequency)
        required_trace_length = np.exp((log_frequency - intercept) / slope)

        # Calculate the required diameter
        # We need to solve: required_trace_length = traceWidth + self.calcCoilTraceLength()
        # Since calcCoilTraceLength is complex, we'll use an iterative approach

        tolerance = 1e-6  # Tighter tolerance for more accuracy

        original_diameter = self.diam + self.traceWidth  # Store original actual diameter

        # Start with the original actual diameter as an initial guess
        current_diameter = original_diameter
        step_size = current_diameter / 2  # Initial step size

        max_iterations = 10000  # Increase max iterations for more accuracy
        for _ in range(max_iterations):
            self.diam = current_diameter - self.traceWidth  # Adjust diam for internal calculations
            actual_trace_length = self.traceWidth + self.calcCoilTraceLength()
            
            if abs(actual_trace_length - required_trace_length) < tolerance:
                break  # We've found a sufficiently close match
            elif actual_trace_length < required_trace_length:
                current_diameter += step_size
            else:
                current_diameter -= step_size
            
            step_size /= 2  # Reduce step size for finer adjustments

        suggested_diameter = current_diameter  # Don't round here for maximum accuracy
        actual_frequency = self.calcResonantFrequency(1e-9)  # Calculate the actual frequency achieved

        self.diam = original_diameter - self.traceWidth  # Restore original diameter

        return suggested_diameter, actual_frequency



    def renderAsCoordinateList(self, reverseDirection=False, angleResOverride: float = None):
        coordinates = []
        if self.shape.isDiscrete:
            if angleResOverride is not None:
                print(Fore.YELLOW + Style.BRIGHT + "renderAsCoordinateList() ignoring angleResOverride, shape not circular" + Style.RESET_ALL)
            
            # Square coil specific logic
            n_turns = int(self.turns)
            if abs(n_turns - self.turns) > 0.01:
                print(Fore.YELLOW + Style.BRIGHT + f'[WARNING] square coil can only have integer number of turns; reducing n_turns to {n_turns}' + Style.RESET_ALL)

            if self.calcPos == self.shape.calcPos:
                points = []
                r_outer = self.diam / 2
                r_inner = self.calcSimpleInnerDiam() / 2

                spacing = self.calcTraceSpacing()

                points = [(r_outer, -r_outer)]
                for i in range(n_turns):
                    r = r_outer - i * spacing
                    next_r = r - spacing
                    if not (self.CCW ^ reverseDirection):
                        turn_points = [
                            (-r, -r),
                            (-r, r),
                            (r, r),
                            (r, -next_r),
                        ]
                    else:
                        turn_points = [
                            (r, r),
                            (-r, r),
                            (-r, -r),
                            (next_r, -r),
                        ]
                    points.extend(turn_points)

                # Convert list of points to list of line segments
                line_segments = []
                for i in range(len(points) - 1):
                    line_segments.append((points[i], points[i + 1]))

                # Print trace lengths for square coil
                print(Style.BRIGHT + Fore.LIGHTBLUE_EX + "Trace Lengths for Square Coil:" + Style.RESET_ALL)
                for i, segment in enumerate(line_segments):
                    length = math.sqrt((segment[1][0] - segment[0][0])**2 + (segment[1][1] - segment[0][1])**2)
                    print(f"Trace {i+1} Length: {length:.2f} mm")

                return line_segments
            else:
                coordinates = [self.calcPos(i, self.diam, self.clearance, self.traceWidth, self.CCW ^ reverseDirection) for i in range(self.shape.stepsPerTurn * self.turns + 1)]
                if len(coordinates) % 10 == 0:  # Example condition: print only if the number of coordinates is a multiple of 10
                    print(Fore.CYAN + Style.BRIGHT + f"renderAsCoordinateList (Discrete): {len(coordinates)} points" + Style.RESET_ALL)

        else:
            angleRes = angleResOverride if angleResOverride else angleRenderResDefault
            coordinates = [self.shape.calcPos(i * angleRes, self.diam, self.clearance, self.traceWidth, self.CCW ^ reverseDirection) for i in range(int(round((self.shape.stepsPerTurn * self.turns) / angleRes, 0)) + 1)]
            if len(coordinates) % 10 == 0:  # Same example condition
                print(Fore.CYAN + Style.BRIGHT + f"renderAsCoordinateList (Continuous): {len(coordinates)} points" + Style.RESET_ALL)

        # Convert list of points to list of line segments
        line_segments = []
        for i in range(len(coordinates) - 1):
            line_segments.append((coordinates[i], coordinates[i + 1]))

        return line_segments

# loop 
    def render_loop_antenna(self):
        if self.loop_shape == 'Loop Antenna with Pads':
            loop_trace_width = 0.6096  # Fixed trace width for the loop in mm
            gap = self.traceWidth  # Gap between the outer edge of the coil and the inner edge of the loop

            # Calculate the loop's diameter
            loop_diameter = self.diam + 2 * (gap + loop_trace_width)

            # Calculate half the side of the square loop
            half_side = loop_diameter / 2

            # Define the loop with a square shape
            pad_gap = 1.27  # Gap between pads
            loop_lines = [
                ((self.x_center - half_side, self.y_center - half_side), (self.x_center + half_side, self.y_center - half_side)),
                ((self.x_center + half_side, self.y_center - half_side), (self.x_center + half_side, self.y_center + half_side)),
                ((self.x_center + half_side, self.y_center + half_side), (self.x_center - half_side, self.y_center + half_side)),
                ((self.x_center - half_side, self.y_center + half_side), (self.x_center - half_side, self.y_center - half_side))
            ]

            # Define pad sizes based on coil diameter
            if self.diam <= 12:
                pad_length, pad_width = 1.905, 1.5875
            else:
                pad_length, pad_width = 3.81, 3.175

            # Position of pads (pointing downward and moved up by half a trace width)
            pad_x1_center = self.x_center - pad_gap/2 - pad_width/2
            pad_x2_center = self.x_center + pad_gap/2 + pad_width/2
            pad_y_center = self.y_center + half_side + pad_length/2 - loop_trace_width/2

            # Create pads (pointing downward)
            pad1 = ((pad_x1_center - pad_width/2, pad_y_center - pad_length/2),
                    (pad_x1_center + pad_width/2, pad_y_center + pad_length/2))
            pad2 = ((pad_x2_center - pad_width/2, pad_y_center - pad_length/2),
                    (pad_x2_center + pad_width/2, pad_y_center + pad_length/2))

            # Add horizontal traces from loop corners to pads
            trace1 = [
                (self.x_center - half_side, self.y_center + half_side),
                (pad_x1_center + pad_width/2, self.y_center + half_side)
            ]
            trace2 = [
                (self.x_center + half_side, self.y_center + half_side),
                (pad_x2_center - pad_width/2, self.y_center + half_side)
            ]

            return loop_lines + [trace1, trace2, pad1, pad2]

        elif self.loop_shape == 'Loop Antenna with Pads 2 Layer':
            loop_trace_width = 0.6096  # Fixed trace width for the loop in mm
            gap = self.traceWidth  # Gap between the outer edge of the coil and the inner edge of the loop
            pad_gap = 1.27  # Gap between pads
           
            center_offset = 0.8

            loop_diameter = self.diam

            print(Fore.GREEN + Style.BRIGHT + f"Calculated Loop Diameter: {loop_diameter}" + Style.RESET_ALL)  # Debugging statement


            # Calculate half the side of the square loop + the scale
            half_side = (loop_diameter / 2) * center_offset

            loop_lines = [
                ((self.x_center - half_side, self.y_center - half_side),
                (self.x_center + half_side, self.y_center - half_side)),
                ((self.x_center + half_side, self.y_center - half_side),
                (self.x_center + half_side, self.y_center + half_side)),
                ((self.x_center + half_side, self.y_center + half_side),
                (self.x_center - half_side, self.y_center + half_side)),
                ((self.x_center - half_side, self.y_center + half_side),
                (self.x_center - half_side, self.y_center - half_side))
            ]

            print(Fore.BLUE + Style.BRIGHT + f"Loop Coordinates: {loop_lines}" + Style.RESET_ALL)  # Debugging statement


            # Define pad sizes based on coil diameter
            if self.diam <= 12:
                pad_length, pad_width = 1.905, 1.5875
            else:
                pad_length, pad_width = 3.81, 3.175

            # Position of pads (pointing downward and moved up by half a trace width)
            pad_x1_center = self.x_center - (pad_gap/2 + pad_width/2) * center_offset
            pad_x2_center = self.x_center + (pad_gap/2 + pad_width/2) * center_offset
            pad_y_center = self.y_center + (half_side + pad_length/2 - loop_trace_width/2) * center_offset

            pad1 = ((pad_x1_center - pad_width/2, pad_y_center - pad_length/2),
                    (pad_x1_center + pad_width/2, pad_y_center + pad_length/2))
            pad2 = ((pad_x2_center - pad_width/2, pad_y_center - pad_length/2),
                    (pad_x2_center + pad_width/2, pad_y_center + pad_length/2))

            # Add horizontal traces from loop corners to pads
            trace1 = [
                (self.x_center - half_side, self.y_center + half_side),
                (pad_x1_center + pad_width/2, self.y_center + half_side)
            ]
            trace2 = [
                (self.x_center + half_side, self.y_center + half_side),
                (pad_x2_center - pad_width/2, self.y_center + half_side)
            ]
            return loop_lines + [trace1, trace2, pad1, pad2]


        elif self.loop_shape == 'circle':
            # Existing code for rendering circular loop antenna
            shape_instance = shapes[self.loop_shape]
            true_outer_diam = self.calcTrueDiam()
            x_offset = (true_outer_diam / 2) + 5 + (self.loop_diameter / 2)
            y_offset = (true_outer_diam / 2) - 20
            loop_radius = self.loop_diameter / 2
            adjusted_radius = loop_radius - (self.traceWidth / 2)

            points = []
            num_segments = 64  # Increase for smoother circles
            for i in range(num_segments):
                angle_start = 2 * np.pi * i / num_segments
                angle_end = 2 * np.pi * (i + 1) / num_segments
                x_start = x_offset + adjusted_radius * np.cos(angle_start)
                y_start = y_offset + adjusted_radius * np.sin(angle_start)
                x_end = x_offset + adjusted_radius * np.cos(angle_end)
                y_end = y_offset + adjusted_radius * np.sin(angle_end)
                points.append(((x_start, y_start), (x_end, y_end)))
            return points
        elif self.loop_shape == 'square':
            # Existing code for rendering square loop antenna
            shape_instance = shapes[self.loop_shape]
            true_outer_diam = self.calcTrueDiam()
            x_offset = (true_outer_diam / 2) + 5 + (self.loop_diameter / 2)
            y_offset = (true_outer_diam / 2) - 20
            loop_radius = self.loop_diameter / 2
            adjusted_radius = loop_radius - (self.traceWidth / 2)

            side_length = adjusted_radius * 2
            half_side = side_length / 2
            corners = [
                (x_offset - half_side, y_offset - half_side),
                (x_offset + half_side, y_offset - half_side),
                (x_offset + half_side, y_offset + half_side),
                (x_offset - half_side, y_offset + half_side),
            ]
            points = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
            return points
        else:
            print(Fore.RED + Style.BRIGHT + f"Unsupported loop shape: {self.loop_shape}" + Style.RESET_ALL)
            return []
    

    def generateCoilFilename(self):
        return(generateCoilFilename(self))

def print_trace_lengths(coil, line_segments, already_printed):
    if not already_printed:
        table = PrettyTable()
        table.field_names = ["Trace", "Trace Length (mm)"]
        table.align["Trace"] = "r"
        table.align["Trace Length (mm)"] = "r"
        
        total_length = 0
        for i, ((x1, y1), (x2, y2)) in enumerate(line_segments):
            segment_length = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            total_length += segment_length
            table.add_row([f"Trace {i+1}", f"{segment_length:.2f}"])
        
        table.add_row(["Total", f"{total_length:.2f}"])
        print(Fore.WHITE + Style.BRIGHT + str(table) + Style.RESET_ALL)
        return True  # Set already_printed to True after printing
    return False


def update_coil_params(params):
    global coil, renderedLineLists, drawer, updated
    print(Fore.CYAN + Style.BRIGHT + "Updating coil parameters..." + Style.RESET_ALL)  # Debugging statement to confirm function call

    turns = int(params["Turns"])
    diam = float(params["Diameter"])
    clearance = float(params["Width between traces"])
    traceWidth = float(params["Trace Width"])
    layers = int(params["Layers"])
    PCBthickness = float(params["PCB Thickness"])
    copperThickness = float(params["Copper Thickness"])
    shape = params["Shape"]
    formula = params["Formula"]
    square_calc = params.get("square_calc", 'Planar inductor')
    loop_enabled = params.get("loop_enabled", False)
    loop_diameter = float(params.get("loop_diameter", 0))
    loop_shape = params.get("loop_shape", "circle")

    if loop_shape in ['Loop Antenna with Pads', 'Loop Antenna with Pads 2 Layer']:
        coil_loop_shape = 'circle'  # Use circle as a default for the coil
    else:
        coil_loop_shape = loop_shape

    if shape == 'square':
        if square_calc == 'thijses/PCBcoilGenerator':
            coil = coilClass(
                turns, diam, clearance, traceWidth, layers, PCBthickness, copperThickness, shape, formula, False, loop_enabled, loop_diameter, coil_loop_shape,
                calcPos=squareSpiral.calcPos_alt, calcLength=squareSpiral.calcLength_alt
            )
        else:
            coil = coilClass(
                turns, diam, clearance, traceWidth, layers, PCBthickness, copperThickness, shape, formula, False, loop_enabled, loop_diameter, coil_loop_shape
            )
    else:
        coil = coilClass(
            turns, diam, clearance, traceWidth, layers, PCBthickness, copperThickness, shape, formula, False, loop_enabled, loop_diameter, coil_loop_shape
        )

    # Add this line to set the x_center and y_center attributes
    coil.x_center, coil.y_center = 0, 0

    renderedLineLists = [coil.renderAsCoordinateList()]
    if coil.loop_enabled:
        loop_antenna_coords = coil.render_loop_antenna()
        if not loop_antenna_coords:
            print(Fore.YELLOW + Style.BRIGHT + "Warning: Loop antenna coordinates are empty" + Style.RESET_ALL)
        renderedLineLists.append(loop_antenna_coords)
    else:
        renderedLineLists.append([])

    drawer.localVar = coil
    drawer.localVarUpdated = True
    drawer.debugText = drawer.makeDebugText(coil)
    drawer.lastFilename = coil.generateCoilFilename()
    updated = True  # Set the update flag to true after updating the coil parameters    
    print(Fore.GREEN + Style.BRIGHT + "Update complete." + Style.RESET_ALL) 
    resonant_frequency = coil.calcResonantFrequency(1e-9)  # Calculate resonant frequency
    print(Fore.MAGENTA + Style.BRIGHT + f"Estimated Resonant Frequency: {resonant_frequency:.2f} MHz" + Style.RESET_ALL)
 # Debugging statement to confirm update completion
    return coil  # Ensure the coil object is returned
    
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

    print(Fore.GREEN + Style.BRIGHT + "Starting PCBcoilV2..." + Style.RESET_ALL)  # Add this line to confirm the script is running

    root = tk.Tk()
    app = CoilParameterGUI(root, update_coil_params)
    root.after(0, root.deiconify)
    
    initial_params = {
        "Turns": 10, "Diameter": 20, "Width between traces": 0.5, "Trace Width": 0.5, 
        "Layers": 1, "PCB Thickness": 0.6, "Copper Thickness": 0.030, 
        "Shape": 'square', "Formula": 'cur_sheet', "loop_enabled": False, "loop_diameter": 0.0, "loop_shape": 'circle',
        "square_calc": 'Planar inductor'
    }

    if visualization:
        import pygameRenderer as PR
        import pygameUI as UI

        windowHandler = PR.pygameWindowHandler([1280, 720], "PCB coil generator", "fancy/icon.png")
        drawer = PR.pygameDrawer(windowHandler)
        drawer.windowHandler = windowHandler  # Assign the window handler
        update_coil_params(initial_params)

        listUpdated = True  # Flag to track if the list has been updated

        try:
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
                            print(Fore.RED + Style.BRIGHT + str(e) + Style.RESET_ALL)
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
        except Exception as e:
            print(f"An error occurred: {e}")  # Print any exceptions that occur
        finally:
            print(Fore.GREEN + "Exiting PCBcoilV2..." + Style.RESET_ALL)  # Add this line to confirm the script is ending
    else:
        update_coil_params(initial_params)
        print(Fore.WHITE + "coil details:")
        print(Fore.CYAN + f"resistance [mOhm]: {round(coil.calcTotalResistance() * 1000, 3)}")
        print(Fore.CYAN + f"inductance [uH]: {round(coil.calcInductance() * 1000000, 3)}")
        print(Fore.CYAN + f"induct/resist [uH/Ohm]: {round(coil.calcInductance() * 1000000 / coil.calcTotalResistance(), 3)}")
        print(Fore.CYAN + f"induct/radius [uH/mm]: {round(coil.calcInductance() * 1000000 / (coil.diam / 2), 3)}")


if __name__ == "__main__":
    main()