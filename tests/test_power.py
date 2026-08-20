"""
Tests unitarios para el módulo de prevención de suspensión (Keep-Awake).
"""

import unittest
from unittest.mock import patch
from src.core.power import keep_awake, ES_CONTINUOUS, ES_SYSTEM_REQUIRED, ES_DISPLAY_REQUIRED

class TestPowerManagement(unittest.TestCase):
    @patch("sys.platform", "win32")
    @patch("ctypes.windll.kernel32.SetThreadExecutionState")
    def test_keep_awake_calls_windows_api(self, mock_set_state):
        mock_set_state.return_value = 0x80000003

        with keep_awake():
            mock_set_state.assert_called_with(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)

        # After exiting context manager, state should be restored to ES_CONTINUOUS
        self.assertEqual(mock_set_state.call_count, 2)
        mock_set_state.assert_called_with(ES_CONTINUOUS)

    @patch("sys.platform", "win32")
    @patch("ctypes.windll.kernel32.SetThreadExecutionState")
    def test_keep_awake_restores_on_exception(self, mock_set_state):
        mock_set_state.return_value = 0x80000003

        try:
            with keep_awake():
                raise ValueError("Simulated failure during installation")
        except ValueError:
            pass

        # Verify restoration was called in finally
        self.assertEqual(mock_set_state.call_count, 2)
        mock_set_state.assert_called_with(ES_CONTINUOUS)

    @patch("sys.platform", "linux")
    def test_keep_awake_non_windows_safe(self):
        # On non-Windows platform it should gracefully not crash
        with keep_awake():
            pass

if __name__ == "__main__":
    unittest.main()
