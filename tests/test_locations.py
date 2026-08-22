import os
import json
import unittest
import tempfile
from src.core.locations import (
    load_locations, save_locations, add_custom_location,
    select_best_default_drive, export_location_env_vars,
    DEFAULT_LOCATIONS
)

class TestLocations(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_file = os.path.join(self.temp_dir.name, "locations.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_default_locations(self):
        locs = load_locations(self.config_file)
        self.assertEqual(len(locs), 3)
        ids = [l["id"] for l in locs]
        self.assertIn("apps", ids)
        self.assertIn("games", ids)
        self.assertIn("data", ids)

    def test_save_and_add_custom_location(self):
        success = add_custom_location(
            loc_id="vms",
            name="Máquinas Virtuales y Contenedores",
            description="Discos para WSL2, VMware y VirtualBox",
            env_var="DRIVE_VMS",
            preferred_drive="D:",
            fallback_drive="C:",
            target_subpath="VMs",
            config_path=self.config_file
        )
        self.assertTrue(success)
        
        reloaded = load_locations(self.config_file)
        self.assertEqual(len(reloaded), 4)
        vms_loc = next(l for l in reloaded if l["id"] == "vms")
        self.assertEqual(vms_loc["env_var"], "DRIVE_VMS")
        self.assertEqual(vms_loc["preferred_drive"], "D:")

    def test_select_best_default_drive(self):
        mock_drives = [
            {"letter": "C:", "free_gb": 50.0},
            {"letter": "D:", "free_gb": 100.0}
        ]
        # Preferred J: not present -> should fallback to C:
        best_games = select_best_default_drive("J:", "C:", mock_drives)
        self.assertEqual(best_games, "C:")
        
        # Preferred D: present -> should pick D:
        best_vms = select_best_default_drive("D:", "C:", mock_drives)
        self.assertEqual(best_vms, "D:")

    def test_export_location_env_vars(self):
        selected = {
            "apps": "A:",
            "games": "J:",
            "data": "A:"
        }
        export_location_env_vars(selected, config_path=self.config_file)
        
        self.assertEqual(os.environ.get("DRIVE_APPS"), "A:")
        self.assertEqual(os.environ.get("DRIVE_GAMES"), "J:")
        self.assertEqual(os.environ.get("DRIVE_DATA"), "A:")
        self.assertEqual(os.environ.get("TARGET_DRIVE"), "A:")
        self.assertEqual(os.environ.get("TARGET_DRIVE_APPS"), "A:")

if __name__ == "__main__":
    unittest.main()
