# File Integrity Checker

A small Python CLI tool that uses SHA-256 hashes to detect whether files have changed.

## What it does

- Calculates a SHA-256 hash for a file.
- Creates a JSON manifest for one or more files.
- Verifies files later against the saved manifest.
- Reports unchanged, modified, and missing files.
- Uses only the Python standard library.
- Includes unit tests and GitHub Actions CI.

## Why this project?

File integrity checking is useful for backups, configuration files, downloads, logs, and engineering project assets. A cryptographic hash acts like a compact fingerprint: if the file content changes, its SHA-256 value changes too.

## Usage

Python 3.10+ is recommended.

### Hash one file

```bash
python file_integrity.py hash example.txt
```

### Create a manifest

```bash
python file_integrity.py create integrity.json file1.txt file2.txt
```

### Verify files

```bash
python file_integrity.py verify integrity.json
```

Example output:

```text
OK       file1.txt
MODIFIED file2.txt
MISSING  file3.txt
```

## Run tests

```bash
python -m unittest discover -v
```

## Files

- `file_integrity.py` — CLI and integrity-checking logic
- `test_file_integrity.py` — unit tests
- `.github/workflows/tests.yml` — GitHub Actions test workflow
- `.gitignore` — Python exclusions

## Concepts practiced

- `hashlib` and SHA-256
- `pathlib`
- Reading files in binary mode
- JSON serialization
- CLI design with `argparse`
- Functions and error handling
- Unit testing with `unittest`
- CI with GitHub Actions
