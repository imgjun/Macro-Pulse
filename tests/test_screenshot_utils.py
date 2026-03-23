import os
import sys
import tempfile
import unittest


sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from artifact_utils import cleanup_files, resolve_output_path


class ScreenshotUtilsTests(unittest.TestCase):
    def test_resolve_output_path_creates_temp_png_when_missing(self):
        path = resolve_output_path(None, "finviz_map")

        try:
            self.assertEqual(os.path.dirname(path), tempfile.gettempdir())
            self.assertTrue(
                os.path.basename(path).startswith("macro_pulse_finviz_map_")
            )
            self.assertTrue(path.endswith(".png"))
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_resolve_output_path_preserves_explicit_path(self):
        self.assertEqual(resolve_output_path("custom.png", "finviz_map"), "custom.png")

    def test_cleanup_files_removes_existing_temp_file(self):
        path = resolve_output_path(None, "finviz_map")
        self.assertTrue(os.path.exists(path))

        cleanup_files([path, None, "missing-file.png"])

        self.assertFalse(os.path.exists(path))


if __name__ == "__main__":
    unittest.main()
