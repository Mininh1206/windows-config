"""
Tests unitarios para el motor TUI y la lógica de Viewport / Scroll dinámico.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.core.tui import calculate_viewport, C_RESET

class TestTUIViewport(unittest.TestCase):
    def test_calculate_viewport_small_list(self):
        # When total items fit in visible height, no scroll offset is needed
        total_items = 10
        current_idx = 4
        visible_height = 15

        start_idx, end_idx = calculate_viewport(current_idx, total_items, visible_height, previous_start=0)
        self.assertEqual(start_idx, 0)
        self.assertEqual(end_idx, 10)

    def test_calculate_viewport_scroll_down(self):
        # When moving down past the visible window, start_idx scrolls down
        total_items = 100
        current_idx = 25
        visible_height = 20

        start_idx, end_idx = calculate_viewport(current_idx, total_items, visible_height, previous_start=0)
        # Cursor is at 25, window height is 20, so start_idx must be at least 6
        self.assertTrue(start_idx <= current_idx < end_idx)
        self.assertEqual(end_idx - start_idx, visible_height)
        self.assertEqual(start_idx, 6)
        self.assertEqual(end_idx, 26)

    def test_calculate_viewport_scroll_up(self):
        # When moving up above the current window, start_idx scrolls up
        total_items = 100
        current_idx = 5
        visible_height = 20

        start_idx, end_idx = calculate_viewport(current_idx, total_items, visible_height, previous_start=15)
        self.assertEqual(start_idx, 5)
        self.assertEqual(end_idx, 25)

    def test_calculate_viewport_boundary_top_and_bottom(self):
        total_items = 50
        visible_height = 10

        # Top
        start, end = calculate_viewport(0, total_items, visible_height, previous_start=0)
        self.assertEqual(start, 0)
        self.assertEqual(end, 10)

        # Bottom
        start, end = calculate_viewport(49, total_items, visible_height, previous_start=30)
        self.assertEqual(start, 40)
        self.assertEqual(end, 50)

class TestTUIAppSelector(unittest.TestCase):
    def setUp(self):
        self.mock_apps = [
            {
                "folder_path": "apps/ux_ui/active_app",
                "manifest": {
                    "id": "active_app",
                    "name": "Active App",
                    "category": "ux_ui",
                    "priority": 0
                }
            },
            {
                "folder_path": "apps/vms/disabled_app",
                "manifest": {
                    "id": "disabled_app",
                    "name": "Disabled App",
                    "category": "vms",
                    "priority": 2,
                    "disabled": True,
                    "disabled_reason": "Requiere instalador manual"
                }
            }
        ]

    @patch("src.core.tui.read_key")
    @patch("src.core.tui.clear_screen")
    @patch("builtins.print")
    def test_disabled_app_not_selected_by_default(self, mock_print, mock_clear, mock_key):
        """Verifica que las apps deshabilitadas no se seleccionen por defecto al presionar ENTER."""
        from src.core.tui import run_tui_app_selector
        mock_key.side_effect = ["ENTER"]

        selected = run_tui_app_selector(self.mock_apps)
        selected_ids = [item["manifest"]["id"] for item in selected]
        self.assertIn("active_app", selected_ids)
        self.assertNotIn("disabled_app", selected_ids)

    @patch("src.core.tui.read_key")
    @patch("src.core.tui.clear_screen")
    @patch("builtins.print")
    def test_select_all_ignores_disabled_apps(self, mock_print, mock_clear, mock_key):
        """Verifica que 'A' (Seleccionar todas) ignore las apps deshabilitadas."""
        from src.core.tui import run_tui_app_selector
        mock_key.side_effect = ["A", "ENTER"]

        selected = run_tui_app_selector(self.mock_apps)
        selected_ids = [item["manifest"]["id"] for item in selected]
        self.assertIn("active_app", selected_ids)
        self.assertNotIn("disabled_app", selected_ids)

    @patch("src.core.tui.read_key")
    @patch("src.core.tui.clear_screen")
    @patch("builtins.print")
    def test_space_on_disabled_app_does_not_toggle(self, mock_print, mock_clear, mock_key):
        """Verifica que presionar ESPACIO sobre una app deshabilitada no la marque."""
        from src.core.tui import run_tui_app_selector
        # flat_items: 0=HEADER(ux_ui), 1=APP(active_app), 2=HEADER(vms), 3=APP(disabled_app)
        mock_key.side_effect = ["DOWN", "DOWN", "DOWN", "SPACE", "ENTER"]

        selected = run_tui_app_selector(self.mock_apps)
        selected_ids = [item["manifest"]["id"] for item in selected]
        self.assertNotIn("disabled_app", selected_ids)

if __name__ == "__main__":
    unittest.main()
