import contextlib
import io
import unittest

import numpy as np

from PCBcoilV2 import coilClass


class PreviewGeometryTest(unittest.TestCase):
    def make_coil(self, shape, diameter=30, trace_width=0.5, loop_diameter=12):
        return coilClass(2, diameter, 0.5, trace_width, shape=shape,
                         loop_enabled=True, loop_diameter=loop_diameter)

    def test_polygon_shapes_do_not_use_the_square_trace_layout(self):
        for shape, edges in [("square", 4), ("hexagon", 6), ("octagon", 8)]:
            coil = self.make_coil(shape)
            with contextlib.redirect_stdout(io.StringIO()):
                segments = coil.renderAsCoordinateList()
            self.assertEqual(len(segments), 2 * edges)
            if shape != "square":
                self.assertTrue(any(abs(end[0] - start[0]) > 1e-6 and
                                    abs(end[1] - start[1]) > 1e-6
                                    for start, end in segments))

    def test_circle_loop_keeps_ten_mm_of_conductor_clearance(self):
        for shape in ["square", "hexagon", "octagon", "circle"]:
            for diameter, width, loop_diameter in [(20, 0.3, 8), (30, 0.5, 12), (50, 1.0, 24)]:
                with self.subTest(shape=shape, diameter=diameter, width=width):
                    coil = self.make_coil(shape, diameter, width, loop_diameter)
                    with contextlib.redirect_stdout(io.StringIO()):
                        geometry = coil.circle_loop_geometry()
                        segments = np.asarray(coil.renderAsCoordinateList(), dtype=float)
                    start, end = segments[:, 0], segments[:, 1]
                    center = np.asarray(geometry["center"])
                    direction = end - start
                    lengths = np.sum(direction * direction, axis=1)
                    fraction = np.clip(np.divide(np.sum((center - start) * direction, axis=1),
                                                 lengths, out=np.zeros_like(lengths),
                                                 where=lengths != 0), 0, 1)
                    closest = start + fraction[:, None] * direction
                    distance = np.min(np.linalg.norm(closest - center, axis=1))
                    gap = distance - geometry["radius"] - width
                    self.assertAlmostEqual(gap, 10.0, places=8)

    def test_zero_loop_diameter_uses_a_positive_auto_radius(self):
        with contextlib.redirect_stdout(io.StringIO()):
            geometry = self.make_coil("circle", loop_diameter=0).circle_loop_geometry()
        self.assertGreater(geometry["radius"], 0)

    def test_loop_diameter_must_exceed_trace_width(self):
        with self.assertRaisesRegex(ValueError, "exceed"):
            self.make_coil("circle", trace_width=1, loop_diameter=0.5).circle_loop_geometry()


if __name__ == "__main__":
    unittest.main()
