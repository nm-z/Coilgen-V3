# TODO: Add Loop Antenna Option
# TODO: 2 trace widths from the outermost trace. 2 fiducias, diagonally (1 Upper right hand corner and 1 Lower Left hand corner)
# - Loop antenna option (1/2 size of sensor): Use second layer, default layer 2 to a single turn  at ½ the diameter of layer 1. Use layer 1 trace-width for now.


from tkinter_coil_gui import CoilParameterGUI
import tkinter as tk
import numpy as np
import time
from typing import Callable

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
    formulaCoefficients: dict[str, tuple[float]]
    stepsPerTurn: int | float
    isDiscrete: bool = True

    @staticmethod
    def calcPos(itt: int | float, diam: float, clearance: float, traceWidth: float, CCW: bool) -> tuple[float, float]: ...
    @staticmethod
    def calcLength(itt: int | float, diam: float, clearance: float, traceWidth: float) -> float: ...

    def __repr__(self):
        return "shape(" + self.__class__.__name__ + ")"

class squareSpiral(_shapeBaseClass):
    formulaCoefficients = {
        'wheeler': (2.34, 2.75),
        'monomial': (1.62, -1.21, -0.147, 2.40, 1.78, -0.030),
        'cur_sheet': (1.27, 2.07, 0.18, 0.13)
    }
    stepsPerTurn: int = 4

    @staticmethod
    def calcPos(itt: int, diam: float, clearance: float, traceWidth: float, CCW=False) -> tuple[float, float]:
        spacing = calcTraceSpacing(clearance, traceWidth)
        x = (1 if (((itt % 4) >= 2) ^ CCW) else -1) * (((diam - traceWidth) / 2) - ((itt // 4) * spacing))
        y = (1 if (((itt % 4) == 1) or ((itt % 4) == 2)) else -1) * (((diam - traceWidth) / 2) - (((itt - 1) // 4) * spacing))
        return (x, y)

    @staticmethod
    def calcLength(itt: int, diam: float, clearance: float, traceWidth: float) -> float:
        spacing = calcTraceSpacing(clearance, traceWidth)
        horLines = (itt // 2)
        sumOfWidths = (horLines * (diam - traceWidth)) - ((((horLines - 1) * horLines) / 2) * spacing)
        vertLines = ((itt + 1) // 2)
        sumOfHeights = (vertLines * (diam - traceWidth)) - ((max(((vertLines - 2) * (vertLines - 1)) / 2, 0) - 1) * spacing)
        return (sumOfWidths + sumOfHeights)

class circularSpiral(_shapeBaseClass):
    formulaCoefficients = {'wheeler': (2.23, 3.45), 'cur_sheet': (1.00, 2.46, 0.00, 0.20)}
    stepsPerTurn: float = 2 * np.pi
    isDiscrete = False

    @staticmethod
    def calcPos(angle: float, diam: float, clearance: float, traceWidth: float, CCW=False) -> tuple[float, float]:
        spacing = calcTraceSpacing(clearance, traceWidth)
        x = (1 if CCW else -1) * np.sin(angle) * (((diam - traceWidth) / 2) - ((angle / (2 * np.pi)) * spacing))
        y = -1 * np.cos(angle) * (((diam - traceWidth) / 2) - ((angle / (2 * np.pi)) * spacing))
        return (x, y)

    @staticmethod
    def calcLength(angle: float, diam: float, clearance: float, traceWidth: float) -> float:
        turns = (angle / circularSpiral.stepsPerTurn)
        return (np.pi * turns * (diam + calcSimpleInnerDiam(turns, diam, clearance, traceWidth, circularSpiral())) / 2)

class NthDimSpiral(_shapeBaseClass):
    @classmethod
    def circumDiam(subclass, inscribedDiam: float) -> float:
        return (inscribedDiam / np.cos(np.deg2rad(180 / subclass.stepsPerTurn)))

    @classmethod
    def calcPos(subclass, itt: int, diam: float, clearance: float, traceWidth: float, CCW=False) -> tuple[float, float]:
        spacing = calcTraceSpacing(subclass.circumDiam(clearance), subclass.circumDiam(traceWidth))
        angle = itt * np.deg2rad(360 / subclass.stepsPerTurn)
        circumscribedDiam = subclass.circumDiam(diam - traceWidth)
        phaseShift = ((np.deg2rad(180 / subclass.stepsPerTurn) * (-1 if CCW else 1)) if rotateNthDimSpirals else 0.0)
        x = (1 if CCW else -1) * np.sin(angle + phaseShift) * ((circumscribedDiam / 2) - ((angle / (2 * np.pi)) * spacing))
        y = -1 * np.cos(angle + phaseShift) * ((circumscribedDiam / 2) - ((angle / (2 * np.pi)) * spacing))
        return (x, y)

    @classmethod
    def calcLength(subclass, itt: int, diam: float, clearance: float, traceWidth: float) -> float:
        return (itt * np.sin(np.deg2rad(180 / subclass.stepsPerTurn)) * (subclass.circumDiam(diam) + calcSimpleInnerDiam(itt / subclass.stepsPerTurn, subclass.circumDiam(diam), subclass.circumDiam(clearance), subclass.circumDiam(traceWidth), NthDimSpiral())) / 2)

class hexagonSpiral(NthDimSpiral):
    formulaCoefficients = {'wheeler': (2.33, 3.82), 'monomial': (1.28, -1.24, -0.174, 2.47, 1.77, -0.049), 'cur_sheet': (1.09, 2.23, 0.00, 0.17)}
    stepsPerTurn: int = 6

class octagonSpiral(NthDimSpiral):
    formulaCoefficients = {'wheeler': (2.25, 3.55), 'monomial': (1.33, -1.21, -0.163, 2.43, 1.75, -0.049), 'cur_sheet': (1.07, 2.29, 0.00, 0.19)}
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
    def __init__(self, turns: int, diam: float, clearance: float, traceWidth: float, layers: int = 1, PCBthickness: float = 1.6, copperThickness: float = ozCopperToMM(1.0), shape: _shapeBaseClass = shapes['circle'], formula: str = 'cur_sheet', CCW: bool = False):
        self.turns = turns
        self.diam = diam
        self.clearance = clearance
        self.traceWidth = traceWidth
        self.layers = max(layers, 1)
        self.PCBthickness = PCBthickness
        self.copperThickness = copperThickness
        self.shape = (shape if issubclass(shape.__class__, _shapeBaseClass) else self.__init__.__defaults__[-2])
        if (self.shape.__class__ != shape.__class__):
            print("coilClass init() changing shape from:", shape, "to", self.shape, "because it's not a _shapeBaseClass subclass")
        self.formula = (formula if (formula in self.shape.formulaCoefficients) else self.__init__.__defaults__[-1])
        if (self.formula != formula):
            print("coilClass init() changing formula from:", formula, "to", self.formula, "because it's not in the " + str(self.shape) + ".formulaCoefficients")
        self.CCW = CCW

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

    def renderAsCoordinateList(self, reverseDirection=False, angleResOverride: float = None) -> list[tuple[float, float]]:
        if self.shape.isDiscrete:
            if angleResOverride is not None:
                print("renderAsCoordinateList() ignoring angleResOverride, shape not circular")
            return [self.shape.calcPos(i, self.diam, self.clearance, self.traceWidth, self.CCW ^ reverseDirection) for i in range(self.shape.stepsPerTurn * self.turns + 1)]
        else:
            angleRes = (angleResOverride if (angleResOverride is not None) else angleRenderResDefault)
            return [self.shape.calcPos(i * angleRes, self.diam, self.clearance, self.traceWidth, self.CCW ^ reverseDirection) for i in range(int(round((self.shape.stepsPerTurn * self.turns) / angleRes, 0)) + 1)]

    def generateCoilFilename(self):
        return generateCoilFilename(self)

def update_coil_params(params):
    global coil, renderedLineLists, drawer
    turns, diameter, width_between_traces, trace_width, layers, pcb_thickness, copper_thickness, shape, formula = params
    turns = int(turns)
    diameter = float(diameter)
    clearance = float(width_between_traces)  # Updated variable name
    trace_width = float(trace_width)
    layers = int(layers)
    pcb_thickness = float(pcb_thickness)
    copper_thickness = float(copper_thickness)
    shape = shapes[shape]
    formula = formula

    coil = coilClass(turns, diameter, clearance, trace_width, layers, pcb_thickness, copper_thickness, shape, formula)
    print(f"Updated coil with parameters: {coil}")

    renderedLineLists = [coil.renderAsCoordinateList(False), coil.renderAsCoordinateList(True)]
    drawer.localVar = coil
    drawer.localVarUpdated = True
    drawer.debugText = drawer.makeDebugText(coil)
    drawer.lastFilename = coil.generateCoilFilename()

def main():
    global coil, renderedLineLists, drawer

    root = tk.Tk()
    app = CoilParameterGUI(root, update_coil_params)
    root.after(0, root.deiconify)
    
    initial_params = [
        9, 40, 0.15, 0.9, 2, 0.6, 0.030, 'circle', 'cur_sheet'
    ]

    if visualization:
        import pygameRenderer as PR
        import pygameUI as UI

        windowHandler = PR.pygameWindowHandler([1280, 720], "PCB coil generator", "fancy/icon.png")
        drawer = PR.pygameDrawer(windowHandler)
        update_coil_params(initial_params)

        while windowHandler.keepRunning:
            loopStart = time.time()
            drawer.renderBG()
            drawer.drawLineList(renderedLineLists)
            drawer.renderFG()
            windowHandler.frameRefresh()
            UI.handleAllWindowEvents(drawer)

            if drawer.localVarUpdated:
                drawer.localVarUpdated = False

            loopEnd = time.time()
            if (loopEnd - loopStart) < (1 / (60 * 1.05)):
                time.sleep((1 / 60) - (loopEnd - loopStart))

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
