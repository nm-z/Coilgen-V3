import ezdxf
from datetime import datetime
import numpy as np
import math

# Constants
DXFoutputFormats = {'EasyEDA': 'EasyEDA', 'Altium': 'Altium'}
magneticConstant = 4 * np.pi * 10**-7
ozCopperToMM = lambda oz: (34.8 * oz * 10**-3)
RhoCopper = 1.72 * 10**-8
distUnitMult = 1/1000

# Shape Base Class
class _shapeBaseClass:
    def __init__(self):
        self.formulaCoefficients = {}
        self.stepsPerTurn = 0
        self.isDiscrete = True

    def calcPos(self, itt, diam, clearance, traceWidth, CCW):
        pass

    def calcLength(self, itt, diam, clearance, traceWidth):
        pass

    def __repr__(self):
        return f"shape({self.__class__.__name__})"

# Specific Shapes
class squareSpiral(_shapeBaseClass):
    def __init__(self):
        super().__init__()
        self.formulaCoefficients = {'wheeler': (2.34, 2.75)}
        self.stepsPerTurn = 4

    def calcPos(self, itt, diam, clearance, traceWidth, CCW=False):
        step = diam / self.stepsPerTurn
        return (itt * step, itt * step)  # Simplified version

    def calcLength(self, itt, diam, clearance, traceWidth):
        return diam * 4  # Simplified version

# Main Coil Class
class Coil:
    def __init__(self, diam, traceWidth, layers, shape):
        if diam <= 0 or traceWidth <= 0 or layers < 1:
            raise ValueError("Invalid parameters for Coil.")
        self.diam = diam
        self.traceWidth = traceWidth
        self.layers = layers
        self.shape = shape

    def generateCoilFilename(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"Coil_{self.diam}mm_{self.traceWidth}mm_{timestamp}"

    def renderAsCoordinateList(self):
        # Implement based on shape specifics
        return self.shape.calcPos(self.diam, self.traceWidth)

# Utility Functions
def saveDXF(coil, outputFormat):
    if outputFormat not in DXFoutputFormats:
        print(f"Output format: {outputFormat} not in list: {DXFoutputFormats}")
        return []
    try:
        filenames = []
        for i in range(coil.layers):
            filename = f"{outputFormat}_{coil.generateCoilFilename()}_Layer{i}.dxf"
            doc = ezdxf.new('R2010')
            doc.header['$INSUNITS'] = 4  # Millimeters
            msp = doc.modelspace()
            points = coil.renderAsCoordinateList()
            polyline = msp.add_lwpolyline(points, close=False, dxfattribs={'layer': f'Layer{i}'})
            doc.saveas(filename)
            filenames.append(filename)
            print(f"DXF file saved successfully: {filename}")
        return filenames
    except Exception as e:
        print(f"Error occurred: {e}")
        return []

# Example Usage
square = squareSpiral()
coil = Coil(diam=40, traceWidth=1.0, layers=2, shape=square)
saveDXF(coil, 'EasyEDA')
