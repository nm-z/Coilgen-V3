import tkinter as tk
import unittest
from unittest.mock import patch

from tkinter_coil_gui import CoilParameterGUI


class TestCoil:
    def calcResonantFrequency(self, capacitance):
        return 1.0

    def renderAsCoordinateList(self):
        return [((0.0, 0.0), (1.0, 1.0))]


class LayerMenuTest(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = CoilParameterGUI(self.root, lambda params: TestCoil())
        self.root.update()

    def tearDown(self):
        self.root.destroy()

    def test_tabs_keep_coil_loop_and_export_controls_separate(self):
        tabs = [self.app.notebook.tab(tab, "text") for tab in self.app.notebook.tabs()]
        self.assertEqual(tabs, ["Coil", "Loop", "Export"])
        self.assertEqual(self.app.loop_shape_combobox.master, self.app.loop_frame)
        self.assertTrue(all(entry.master == self.app.coil_frame for entry in self.app.param_entries))
        loop_selectors = [widget for widget in self.app.loop_frame.winfo_children()
                          if widget.winfo_class() == "TCombobox"]
        self.assertEqual(len(loop_selectors), 1)

    def test_selected_components_export_once_for_each_loop_layer(self):
        for layer in ["Loop Antenna with Pads", "Loop Antenna with Pads 2 Layer"]:
            for coil_selected, loop_selected in [(True, False), (False, True), (True, True)]:
                with self.subTest(layer=layer, coil=coil_selected, loop=loop_selected):
                    self.app.loop_shape_var.set(layer)
                    self.app.export_coil_var.set(coil_selected)
                    self.app.export_loop_var.set(loop_selected)
                    with patch("tkinter_coil_gui.pcbnew_exporter.export_coil") as coil_export, \
                         patch("tkinter_coil_gui.pcbnew_exporter.export_loop") as loop_export:
                        self.app.export()
                    self.assertEqual(coil_export.call_count, int(coil_selected))
                    self.assertEqual(loop_export.call_count, int(loop_selected))
                    if loop_selected:
                        self.assertFalse(loop_export.call_args.kwargs["combined"])

    def test_export_all_preserves_the_selected_component_preferences(self):
        self.app.export_coil_var.set(False)
        self.app.export_loop_var.set(True)
        with patch("tkinter_coil_gui.pcbnew_exporter.export_coil") as coil_export, \
             patch("tkinter_coil_gui.pcbnew_exporter.export_loop") as loop_export:
            self.app.export_all()
        self.assertEqual(coil_export.call_count, 1)
        self.assertEqual(loop_export.call_count, 1)
        self.assertFalse(self.app.export_coil_var.get())
        self.assertTrue(self.app.export_loop_var.get())

    def test_empty_export_selection_reports_the_required_choice(self):
        for option in self.app.export_options.values():
            option.set(False)
        with patch("tkinter_coil_gui.messagebox.showerror") as error, \
             patch.object(self.app, "submit") as submit:
            self.app.export()
        error.assert_called_once()
        submit.assert_not_called()
        self.assertEqual(self.app.notebook.select(), str(self.app.export_frame))


if __name__ == "__main__":
    unittest.main()
