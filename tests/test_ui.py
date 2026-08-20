"""
Tests unitarios para la renderización de la interfaz visual y la doble barra de progreso.
"""

import unittest
from unittest.mock import patch
import io
from src.core.ui import render_dual_progress, finish_progress_item, print_summary_table

class TestUIProgress(unittest.TestCase):
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_render_dual_progress_output(self, mock_stdout):
        render_dual_progress(
            global_current=5,
            global_total=10,
            app_name="Git for Windows",
            local_step=2,
            total_local_steps=4,
            step_desc="Descargando paquete...",
            phase_name="Fase 1: Herramientas"
        )
        output = mock_stdout.getvalue()
        self.assertIn("50%", output)
        self.assertIn("(5/10 Apps)", output)
        self.assertIn("Git for Windows", output)
        self.assertIn("Descargando paquete...", output)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_finish_progress_item_badges(self, mock_stdout):
        # 1. New install + config success
        finish_progress_item("App1", success=True, already_installed=False, was_configured=True)
        self.assertIn("OK", mock_stdout.getvalue())

        # 2. Existing app + config applied
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        finish_progress_item("App2", success=True, already_installed=True, was_configured=True)
        self.assertIn("CONFIGURADA", mock_stdout.getvalue())

        # 3. Existing app + no config needed
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        finish_progress_item("App3", success=True, already_installed=True, was_configured=False)
        self.assertIn("YA INSTALADA", mock_stdout.getvalue())

        # 4. Error
        mock_stdout.truncate(0)
        mock_stdout.seek(0)
        finish_progress_item("App4", success=False, already_installed=False, was_configured=False)
        self.assertIn("ERROR", mock_stdout.getvalue())

if __name__ == "__main__":
    unittest.main()
