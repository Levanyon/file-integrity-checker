from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable


BUFFER_SIZE = 64 * 1024


def calculate_sha256(path: str | Path) -> str:
    """Return the SHA-256 hex digest for a file."""
    file_path = Path(path)
    digest = hashlib.sha256()

    with file_path.open("rb") as handle:
        while chunk := handle.read(BUFFER_SIZE):
            digest.update(chunk)

    return digest.hexdigest()


def create_manifest(
    files: Iterable[str | Path],
    manifest_path: str | Path,
) -> dict[str, str]:
    """Create and save a JSON manifest mapping file paths to SHA-256 hashes."""
    manifest_file = Path(manifest_path)
    manifest: dict[str, str] = {}

    for item in files:
        file_path = Path(item)
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
        manifest[str(file_path)] = calculate_sha256(file_path)

    manifest_file.write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return manifest


def load_manifest(manifest_path: str | Path) -> dict[str, str]:
    """Load a manifest from JSON and validate its basic structure."""
    manifest_file = Path(manifest_path)
    data = json.loads(manifest_file.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError("Manifest must contain a JSON object.")

    for path, digest in data.items():
        if not isinstance(path, str) or not isinstance(digest, str):
            raise ValueError("Manifest entries must map strings to strings.")

    return data


def verify_manifest(
    manifest_path: str | Path,
) -> dict[str, str]:
    """Verify each manifest file and return status values."""
    manifest = load_manifest(manifest_path)
    results: dict[str, str] = {}

    for file_name, expected_hash in manifest.items():
        file_path = Path(file_name)

        if not file_path.is_file():
            results[file_name] = "MISSING"
            continue

        current_hash = calculate_sha256(file_path)
        results[file_name] = (
            "OK" if current_hash == expected_hash else "MODIFIED"
        )

    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect file changes using SHA-256 hashes."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    hash_parser = subparsers.add_parser(
        "hash",
        help="Calculate the SHA-256 hash of one file.",
    )
    hash_parser.add_argument("file")

    create_parser = subparsers.add_parser(
        "create",
        help="Create a JSON integrity manifest.",
    )
    create_parser.add_argument("manifest")
    create_parser.add_argument("files", nargs="+")

    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify files against a saved manifest.",
    )
    verify_parser.add_argument("manifest")

    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        if args.command == "hash":
            print(calculate_sha256(args.file))
            return 0

        if args.command == "create":
            manifest = create_manifest(args.files, args.manifest)
            print(f"Saved {len(manifest)} file(s) to {args.manifest}")
            return 0

        results = verify_manifest(args.manifest)
        exit_code = 0

        for file_name, status in results.items():
            print(f"{status:<8} {file_name}")
            if status != "OK":
                exit_code = 1

        return exit_code

    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
