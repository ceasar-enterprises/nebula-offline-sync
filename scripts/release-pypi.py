"""Release a package to PyPI.

Usage (from repo root):
    python scripts\release-pypi.py [--test]

- Builds sdist + wheel with `build`.
- Uploads with `twine`.
- `--test` uses TestPyPI (requires TWINE_TEST_USERNAME/PASSWORD or the token).
- Registered tokens live in environment variables, never in the repo:
      TWINE_USERNAME  = __token__
      TWINE_PASSWORD  = pypi-...-token
      TWINE_TEST_USERNAME / TWINE_TEST_PASSWORD for TestPyPI.
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def _run(cmd):
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description="Build + upload NEBULA Offline Sync to PyPI")
    parser.add_argument("--test", action="store_true", help="publish to TestPyPI instead")
    args = parser.parse_args()

    _run([sys.executable, "-m", "pip", "install", "--quiet", "build", "twine"])

    if DIST.exists():
        print(f"cleaning old build artefacts: {DIST}")
        for p in DIST.iterdir():
            p.unlink()

    _run([sys.executable, "-m", "build", "--sdist", "--wheel"])

    repo = "testpypi" if args.test else "pypi"
    upload = [
        sys.executable,
        "-m",
        "twine",
        "upload",
        "--repository",
        repo,
        *(str(p) for p in sorted(DIST.glob("*"))),
    ]
    _run(upload)

    print(f"\nDONE. Published to {repo}. ~60s for index visibility.")


if __name__ == "__main__":
    main()