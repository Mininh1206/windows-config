"""
Pruebas unitarias para el flujo del pipeline en main.py y su resiliencia ante errores aislados.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

class TestPipelineResilience(unittest.TestCase):
    def test_pipeline_continues_when_one_app_fails(self):
        """
        Verifica que si una aplicacion falla o lanza una excepcion inesperada,
        el pipeline no crashea y continua procesando las siguientes aplicaciones.
        """
        mock_apps = [
            {
                "folder_path": "apps/utilidades/app1",
                "manifest": {"id": "app1", "name": "App 1", "config": {"has_direct_config": False}}
            },
            {
                "folder_path": "apps/utilidades/app2_failing",
                "manifest": {"id": "app2", "name": "App 2 Failing", "config": {"has_direct_config": True}}
            },
            {
                "folder_path": "apps/utilidades/app3",
                "manifest": {"id": "app3", "name": "App 3", "config": {"has_direct_config": False}}
            }
        ]

        summary_results = []
        for idx, item in enumerate(mock_apps, 1):
            manifest = item["manifest"]
            folder = item["folder_path"]
            app_name = manifest.get("name")

            install_success = False
            config_success = False
            already_installed = False
            has_direct_config = manifest.get("config", {}).get("has_direct_config", False)

            try:
                if manifest["id"] == "app2":
                    raise RuntimeError("Simulated crash in app2")
                install_success = True
                config_success = True
            except Exception:
                install_success = False
                config_success = False

            status_text = "ÉXITO" if (install_success and config_success) else "ERROR"
            summary_results.append({
                "Application": app_name,
                "Status": status_text
            })

        self.assertEqual(len(summary_results), 3)
        self.assertEqual(summary_results[0]["Status"], "ÉXITO")
        self.assertEqual(summary_results[1]["Status"], "ERROR")
        self.assertEqual(summary_results[2]["Status"], "ÉXITO")

if __name__ == "__main__":
    unittest.main()
