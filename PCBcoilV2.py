
import numpy as np
import mathlib

class Coil(pcb, patterns, type_=='arc'):
    def __init__(self, pcb, patterns, type):
        self.pcb = pcb
        self.patterns = patterns
        self.type = type

    def get_center_pts(self):
        '''Converts anchor points to coordinate points.
        Returns a list of coordinate points (tuples)'''
        pts = []
        for i in range(0, len(self.anchors)):
            anchor_type = self.anchors[i][1]
            if anchor_type in ['start', 'end', 'control1', 'control2']:
                pt = self.anchors[i][0]
            else:
                raise ValueError(f"Unexpected anchor type: {anchor_type}")
            pts.append(pt)
        return pts
