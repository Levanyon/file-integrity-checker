import json
import tempfile
import unittest
from pathlib import Path

from file_integrity import (
    calculate_sha256,
    create_manifest,
    load_manifest,
    verify_manifest,
)


class FileIntegrityTests(unittest.TestCase):
    def test_calculate_sha256_known_value(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "sample.txt"
            file_path.write_text("hello", encoding="utf-8")

            digest = calculate_sha256(file_path)

        self.assertEqual(
            digest,
            "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
        )

    def test_create_and_load_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            file_path = root / "data.txt"
            manifest_path = root / "integrity.json"
            file_path.write_text("sensor-data", encoding="utf-8")

            created = create_manifest([file_path], manifest_path)
            loaded = load_manifest(manifest_path)

        self.assertEqual(created, loaded)
        self.assertIn(str(file_path), created)

    def test_verify_unchanged_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            file_path = root / "config.txt"
            manifest_path = root / "integrity.json"
            file_path.write_text("version=1", encoding="utf-8")
            create_manifest([file_path], manifest_path)

            results = verify_manifest(manifest_path)

        self.assertEqual(results[str(file_path)], "OK")

    def test_verify_modified_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            file_path = root / "config.txt"
            manifest_path = root / "integrity.json"
            file_path.write_text("version=1", encoding="utf-8")
            create_manifest([file_path], manifest_path)

            file_path.write_text("version=2", encoding="utf-8")
            results = verify_manifest(manifest_path)

        self.assertEqual(results[str(file_path)], "MODIFIED")

    def test_verify_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            file_path = root / "temporary.txt"
            manifest_path = root / "integrity.json"
            file_path.write_text("temporary", encoding="utf-8")
            create_manifest([file_path], manifest_path)

            file_path.unlink()
            results = verify_manifest(manifest_path)

        self.assertEqual(results[str(file_path)], "MISSING")

    def test_invalid_manifest_structure_raises(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest_path = Path(temp_dir) / "integrity.json"
            manifest_path.write_text(
                json.dumps(["not", "an", "object"]),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_manifest(manifest_path)


if __name__ == "__main__":
    unittest.main()
