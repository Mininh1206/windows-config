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

if __name__ == "__main__":
    unittest.main()
