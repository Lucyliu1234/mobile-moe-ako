#!/usr/bin/env python3
"""Compatibility wrapper for the renamed boundary template tool.

Use `harness/boundary_template.py` for new runs.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path)
    parser.add_argument("--profile-report", type=Path, required=True)
    parser.add_argument("--label")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    script = Path(__file__).with_name("boundary_template.py")
    cmd = [sys.executable, str(script), "--profile-report", str(args.profile_report)]
    if args.label:
        cmd.extend(["--label", args.label])
    if args.out:
        cmd.extend(["--out", str(args.out)])
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
