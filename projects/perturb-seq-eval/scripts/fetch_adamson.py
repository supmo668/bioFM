"""Fetch the real Adamson 2016 pilot subset from Zenodo scPerturb mirror.

Usage:
    python3 scripts/fetch_adamson.py [--subset pilot] [--out data/]
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

SUBSETS = {
    # Filename on Zenodo → local filename
    "pilot":   ("AdamsonWeissman2016_GSM2406675_10X001.h5ad", "Adamson2016_pilot.h5ad"),
    "10X005":  ("AdamsonWeissman2016_GSM2406677_10X005.h5ad", "Adamson2016_10X005.h5ad"),
    "10X010":  ("AdamsonWeissman2016_GSM2406681_10X010.h5ad", "Adamson2016_10X010.h5ad"),
}
ZENODO_RECORD = 13350497


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subset", choices=list(SUBSETS), default="pilot",
                    help="which Adamson subset to fetch (default: smallest, ~34 MB)")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "data")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    remote_name, local_name = SUBSETS[args.subset]
    url = f"https://zenodo.org/api/records/{ZENODO_RECORD}/files/{remote_name}/content"
    dest = args.out / local_name
    if dest.exists():
        print(f"already present: {dest} ({dest.stat().st_size} bytes) — skipping")
        return 0

    print(f"downloading {url}\n  -> {dest}")
    try:
        urllib.request.urlretrieve(url, dest)
    except Exception as e:
        print(f"download failed: {e}", file=sys.stderr)
        return 1
    print(f"wrote {dest} ({dest.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
