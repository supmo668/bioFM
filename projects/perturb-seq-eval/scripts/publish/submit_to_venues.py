#!/usr/bin/env python3
"""Submit paper + supplement to preprint venues via their HTTP APIs.

Reads metadata from ``publish.yml`` and dispatches to Zenodo / Figshare /
OSF. Writes DOIs and deposition IDs back into ``publish.state.json`` so
partial failures are resumable.

Secrets are loaded from a ``.env`` file found by walking upwards from the
current working directory. A missing ``.env`` is a hard error; a missing
per-venue token yields a per-venue warning and skips that venue only.

Subcommands
-----------
    validate   — check config + tokens + files without making any API calls.
    zenodo     — submit only to Zenodo.
    figshare   — submit only to Figshare.
    osf        — submit only to OSF (BioHackrXiv by default).
    all        — submit to every enabled venue in publish.yml.

Flags
-----
    --dry-run  — create depositions but do not publish them (leaves drafts).
    --config   — path to publish.yml (default: ./publish.yml).
    --state    — path to the resumable state file (default: ./publish.state.json).
    --env      — path to .env (default: walk upward from cwd to find one).

Environment variables consumed from .env
---------------------------------------
    ZENODO_TOKEN      Zenodo personal access token with deposit scopes.
    FIGSHARE_TOKEN    Figshare personal token.
    OSF_TOKEN         OSF personal access token (osf.full_write scope).

See research/PUBLISHING_RUNBOOK.md for end-to-end operator instructions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
import yaml


# ---------------------------------------------------------------------------
# .env loader (no python-dotenv dep)
# ---------------------------------------------------------------------------


PLACEHOLDER_VALUES: frozenset[str] = frozenset({"", "REPLACE_ME", "sk-or-v1-REPLACE_ME"})


def _find_env_file(start: Path | None = None) -> Path | None:
    """Walk upward from ``start`` (default: cwd) looking for ``.env``."""
    here = (start or Path.cwd()).resolve()
    for d in (here, *here.parents):
        candidate = d / ".env"
        if candidate.is_file():
            return candidate
    return None


def _parse_dotenv_line(raw: str) -> tuple[str, str] | None:
    """Parse ``KEY=value`` lines; return None for blanks / comments."""
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        return None
    key, _, value = line.partition("=")
    key = key.strip()
    value = value.strip().strip('"').strip("'")
    if not key:
        return None
    return key, value


def load_dotenv(path: Path) -> dict[str, str]:
    """Load ``.env`` into os.environ (without overriding already-set vars)."""
    vals: dict[str, str] = {}
    for raw in path.read_text().splitlines():
        parsed = _parse_dotenv_line(raw)
        if parsed is None:
            continue
        key, value = parsed
        vals[key] = value
        os.environ.setdefault(key, value)
    return vals


def token_is_missing(name: str) -> bool:
    """True if ``name`` is unset or still holds a placeholder."""
    return os.environ.get(name, "") in PLACEHOLDER_VALUES


# ---------------------------------------------------------------------------
# Shared configuration + state
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PublishConfig:
    title: str
    description: str
    creators: list[dict]
    keywords: list[str]
    license: str
    files: list[dict]
    venues: dict
    root: Path

    @classmethod
    def load(cls, path: Path) -> "PublishConfig":
        with path.open() as f:
            raw = yaml.safe_load(f)
        root = path.resolve().parent
        return cls(
            title=raw["title"].strip(),
            description=raw["description"].strip(),
            creators=raw.get("creators", []),
            keywords=raw.get("keywords", []),
            license=raw.get("license", "cc-by-4.0"),
            files=raw.get("files", []),
            venues=raw.get("venues", {}),
            root=root,
        )


class State:
    """Small JSON file holding deposition IDs + DOIs across venues."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._data: dict[str, Any] = {}
        if path.exists():
            self._data = json.loads(path.read_text())

    def get(self, venue: str, key: str, default: Any = None) -> Any:
        return self._data.get(venue, {}).get(key, default)

    def set(self, venue: str, key: str, value: Any) -> None:
        self._data.setdefault(venue, {})[key] = value
        self.path.write_text(json.dumps(self._data, indent=2))

    def all(self) -> dict[str, Any]:
        return dict(self._data)


# ---------------------------------------------------------------------------
# File preparation (zip directories, compute md5)
# ---------------------------------------------------------------------------


def prepare_files(cfg: PublishConfig, workdir: Path) -> list[dict]:
    """Resolve each ``files[*].path`` to a concrete file on disk.

    Directories are zipped on the fly into ``workdir``. Returns a list of
    dicts with keys: ``name``, ``path``, ``md5``, ``size``.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    resolved = []
    for entry in cfg.files:
        src = (cfg.root / entry["path"]).resolve()
        if not src.exists():
            raise FileNotFoundError(f"configured file missing: {src}")
        name = entry.get("name") or src.name
        if src.is_dir():
            if not name.endswith(".zip"):
                name = f"{name}.zip"
            archive = workdir / name
            if archive.exists():
                archive.unlink()
            _zip_directory(src, archive)
            src = archive
        md5 = _md5(src)
        resolved.append(
            {
                "name": name,
                "path": src,
                "md5": md5,
                "size": src.stat().st_size,
                "description": entry.get("description", ""),
            }
        )
    return resolved


def _zip_directory(src: Path, dst: Path) -> None:
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src.rglob("*"):
            if p.is_file():
                z.write(p, arcname=p.relative_to(src.parent))


def _md5(path: Path) -> str:
    h = hashlib.md5()  # noqa: S324 — required by Figshare, not for security
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Zenodo
# ---------------------------------------------------------------------------


class ZenodoSubmitter:
    name = "zenodo"

    def __init__(self, cfg: PublishConfig, state: State, dry_run: bool = False) -> None:
        self.cfg = cfg
        self.state = state
        self.dry_run = dry_run
        vcfg = cfg.venues.get("zenodo", {})
        sandbox = vcfg.get("sandbox", False)
        self.base = (
            "https://sandbox.zenodo.org/api" if sandbox else "https://zenodo.org/api"
        )
        if token_is_missing("ZENODO_TOKEN"):
            raise RuntimeError(
                "ZENODO_TOKEN missing or placeholder — fill it in .env "
                "(see .env.example at repo root)"
            )
        self.headers = {"Authorization": f"Bearer {os.environ['ZENODO_TOKEN']}"}
        self.vcfg = vcfg

    def submit(self, files: list[dict]) -> str:
        dep_id = self.state.get("zenodo", "deposit_id")
        if dep_id is None:
            r = requests.post(
                f"{self.base}/deposit/depositions",
                headers={**self.headers, "Content-Type": "application/json"},
                json={},
                timeout=30,
            )
            _raise_on(r)
            body = r.json()
            dep_id = body["id"]
            bucket = body["links"]["bucket"]
            self.state.set("zenodo", "deposit_id", dep_id)
            self.state.set("zenodo", "bucket", bucket)
        else:
            bucket = self.state.get("zenodo", "bucket")

        for f in files:
            r = requests.put(
                f"{bucket}/{f['name']}",
                headers=self.headers,
                data=f["path"].read_bytes(),  # <100 MB typical; for larger, stream in chunks
                timeout=300,
            )
            _raise_on(r)

        metadata = {
            "metadata": {
                "title": self.cfg.title,
                "description": self.cfg.description,
                "upload_type": self.vcfg.get("upload_type", "publication"),
                "publication_type": self.vcfg.get("publication_type", "preprint"),
                "creators": [
                    {
                        "name": c["name"],
                        **({"affiliation": c["affiliation"]} if c.get("affiliation") else {}),
                        **({"orcid": c["orcid"]} if c.get("orcid") and _valid_orcid(c["orcid"]) else {}),
                    }
                    for c in self.cfg.creators
                ],
                "keywords": self.cfg.keywords,
                "license": self.cfg.license.replace("_", "-"),
                "access_right": "open",
                "related_identifiers": self.vcfg.get("related_identifiers", []),
                "communities": [
                    {"identifier": c} for c in self.vcfg.get("communities", [])
                ],
            }
        }
        r = requests.put(
            f"{self.base}/deposit/depositions/{dep_id}",
            headers={**self.headers, "Content-Type": "application/json"},
            json=metadata,
            timeout=30,
        )
        _raise_on(r)
        reserved_doi = r.json().get("metadata", {}).get("prereserve_doi", {}).get("doi")
        if reserved_doi:
            self.state.set("zenodo", "doi", reserved_doi)

        if self.dry_run:
            print(f"[zenodo] DRY-RUN — deposit {dep_id} left in draft state")
            return reserved_doi or ""

        r = requests.post(
            f"{self.base}/deposit/depositions/{dep_id}/actions/publish",
            headers=self.headers,
            timeout=60,
        )
        _raise_on(r)
        doi = r.json()["doi"]
        self.state.set("zenodo", "doi", doi)
        self.state.set("zenodo", "published", True)
        print(f"[zenodo] published: https://doi.org/{doi}")
        return doi


# ---------------------------------------------------------------------------
# Figshare
# ---------------------------------------------------------------------------


class FigshareSubmitter:
    name = "figshare"

    def __init__(self, cfg: PublishConfig, state: State, dry_run: bool = False) -> None:
        self.cfg = cfg
        self.state = state
        self.dry_run = dry_run
        if token_is_missing("FIGSHARE_TOKEN"):
            raise RuntimeError(
                "FIGSHARE_TOKEN missing or placeholder — fill it in .env "
                "(see .env.example at repo root)"
            )
        self.headers = {"Authorization": f"token {os.environ['FIGSHARE_TOKEN']}"}
        self.vcfg = cfg.venues.get("figshare", {})
        self.base = "https://api.figshare.com/v2"

    def submit(self, files: list[dict]) -> str:
        art_id = self.state.get("figshare", "article_id")
        if art_id is None:
            payload = {
                "title": self.cfg.title,
                "description": self.cfg.description,
                "tags": self.cfg.keywords,
                "categories": self.vcfg.get("categories", []),
                "defined_type": self.vcfg.get("defined_type", "preprint"),
                "license": _figshare_license(self.cfg.license),
                "authors": [
                    {"name": c["name"], **({"orcid_id": c["orcid"]} if c.get("orcid") and _valid_orcid(c["orcid"]) else {})}
                    for c in self.cfg.creators
                ],
            }
            r = requests.post(
                f"{self.base}/account/articles",
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            _raise_on(r)
            art_id = int(r.json()["location"].rsplit("/", 1)[-1])
            self.state.set("figshare", "article_id", art_id)

        for f in files:
            self._upload_file(art_id, f)

        r = requests.post(
            f"{self.base}/account/articles/{art_id}/reserve_doi",
            headers=self.headers, timeout=30,
        )
        _raise_on(r)
        reserved_doi = r.json().get("doi")
        self.state.set("figshare", "doi", reserved_doi)

        if self.dry_run:
            print(f"[figshare] DRY-RUN — article {art_id} left in draft")
            return reserved_doi or ""

        r = requests.post(
            f"{self.base}/account/articles/{art_id}/publish",
            headers=self.headers, timeout=60,
        )
        _raise_on(r)
        self.state.set("figshare", "published", True)
        print(f"[figshare] published: https://doi.org/{reserved_doi}")
        return reserved_doi

    def _upload_file(self, art_id: int, f: dict) -> None:
        # 1. Register the file
        r = requests.post(
            f"{self.base}/account/articles/{art_id}/files",
            headers={**self.headers, "Content-Type": "application/json"},
            json={"name": f["name"], "size": f["size"], "md5": f["md5"]},
            timeout=30,
        )
        _raise_on(r)
        file_id = int(r.json()["location"].rsplit("/", 1)[-1])

        # 2. Retrieve upload part info
        r = requests.get(
            f"{self.base}/account/articles/{art_id}/files/{file_id}",
            headers=self.headers, timeout=30,
        )
        _raise_on(r)
        upload_url = r.json()["upload_url"]

        r = requests.get(upload_url, headers=self.headers, timeout=30)
        _raise_on(r)
        parts = r.json()["parts"]

        # 3. Upload each chunk
        with f["path"].open("rb") as fh:
            for part in parts:
                fh.seek(part["startOffset"])
                data = fh.read(part["endOffset"] - part["startOffset"] + 1)
                part_url = f"{upload_url}/{part['partNo']}"
                r = requests.put(part_url, data=data, headers=self.headers, timeout=300)
                _raise_on(r)

        # 4. Complete upload
        r = requests.post(
            f"{self.base}/account/articles/{art_id}/files/{file_id}",
            headers=self.headers, timeout=60,
        )
        _raise_on(r)


# ---------------------------------------------------------------------------
# OSF Preprints (BioHackrXiv by default)
# ---------------------------------------------------------------------------


class OSFSubmitter:
    name = "osf"

    def __init__(self, cfg: PublishConfig, state: State, dry_run: bool = False) -> None:
        self.cfg = cfg
        self.state = state
        self.dry_run = dry_run
        if token_is_missing("OSF_TOKEN"):
            raise RuntimeError(
                "OSF_TOKEN missing or placeholder — fill it in .env "
                "(see .env.example at repo root)"
            )
        self.headers = {
            "Authorization": f"Bearer {os.environ['OSF_TOKEN']}",
            "Content-Type": "application/vnd.api+json",
        }
        self.vcfg = cfg.venues.get("osf", {})
        self.provider = self.vcfg.get("provider", "biohackrxiv")
        self.api = "https://api.osf.io/v2"
        self.files_api = "https://files.osf.io/v1"

    def submit(self, files: list[dict]) -> str:
        proj_id = self.state.get("osf", "project_id")
        if proj_id is None:
            payload = {
                "data": {
                    "type": "nodes",
                    "attributes": {
                        "title": self.cfg.title,
                        "description": self.cfg.description,
                        "category": "project",
                        "tags": self.cfg.keywords,
                        "public": False,
                    },
                }
            }
            r = requests.post(f"{self.api}/nodes/", headers=self.headers, json=payload, timeout=30)
            _raise_on(r)
            proj_id = r.json()["data"]["id"]
            self.state.set("osf", "project_id", proj_id)

        # Upload the first file as the "primary" preprint file.
        primary = files[0]
        primary_id = self.state.get("osf", "primary_file_id")
        if primary_id is None:
            up_url = (
                f"{self.files_api}/resources/{proj_id}/providers/osfstorage/"
                f"?kind=file&name={primary['name']}"
            )
            # Upload uses the bearer token but plain octet-stream body.
            up_headers = {"Authorization": self.headers["Authorization"]}
            with primary["path"].open("rb") as fh:
                r = requests.put(up_url, headers=up_headers, data=fh, timeout=600)
            _raise_on(r)
            primary_id = r.json()["data"]["attributes"]["resource"]
            # Some OSF releases use 'id' or 'path' instead — try a few keys.
            for k in ("resource", "id", "path"):
                if k in r.json()["data"]["attributes"]:
                    primary_id = r.json()["data"]["attributes"][k]
                    break
            self.state.set("osf", "primary_file_id", primary_id)

        # Additional files (supplement) uploaded same way.
        for f in files[1:]:
            r = requests.put(
                f"{self.files_api}/resources/{proj_id}/providers/osfstorage/"
                f"?kind=file&name={f['name']}",
                headers={"Authorization": self.headers["Authorization"]},
                data=f["path"].read_bytes(),
                timeout=600,
            )
            _raise_on(r)

        # Create the preprint record.
        pp_id = self.state.get("osf", "preprint_id")
        if pp_id is None:
            payload = {
                "data": {
                    "type": "preprints",
                    "attributes": {
                        "title": self.cfg.title,
                        "description": self.cfg.description,
                        "tags": self.cfg.keywords,
                    },
                    "relationships": {
                        "node": {"data": {"type": "nodes", "id": proj_id}},
                        "primary_file": {
                            "data": {"type": "files", "id": primary_id}
                        },
                        "provider": {
                            "data": {"type": "providers", "id": self.provider}
                        },
                        "subjects": {
                            "data": [
                                {"type": "subjects", "id": s}
                                for s in self.vcfg.get("subjects", [])
                            ]
                        },
                    },
                }
            }
            r = requests.post(f"{self.api}/preprints/", headers=self.headers, json=payload, timeout=30)
            _raise_on(r)
            pp_id = r.json()["data"]["id"]
            self.state.set("osf", "preprint_id", pp_id)

        if self.dry_run:
            print(f"[osf] DRY-RUN — preprint {pp_id} left unpublished")
            return ""

        # Mark public and published.
        r = requests.patch(
            f"{self.api}/preprints/{pp_id}/",
            headers=self.headers,
            json={
                "data": {
                    "id": pp_id,
                    "type": "preprints",
                    "attributes": {"is_published": True},
                }
            },
            timeout=30,
        )
        _raise_on(r)
        doi_candidate = r.json()["data"]["attributes"].get("preprint_doi_created") or f"10.17605/OSF.IO/{pp_id.upper()}"
        self.state.set("osf", "doi", doi_candidate)
        self.state.set("osf", "published", True)
        print(f"[osf] published: https://osf.io/preprints/{self.provider}/{pp_id}")
        return doi_candidate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _raise_on(r: requests.Response) -> None:
    if r.status_code >= 400:
        sys.stderr.write(f"HTTP {r.status_code} on {r.request.method} {r.request.url}\n")
        sys.stderr.write(r.text[:2000] + "\n")
        r.raise_for_status()


def _valid_orcid(orcid: str | None) -> bool:
    return bool(orcid) and orcid != "0000-0000-0000-0000"


def _figshare_license(key: str) -> int:
    """Map a licence slug to Figshare's integer license ID. Defaults to CC-BY 4."""
    table = {"cc-by-4.0": 1, "cc0": 2, "apache-2.0": 10, "mit": 4}
    return table.get(key, 1)


# ---------------------------------------------------------------------------
# Validate command
# ---------------------------------------------------------------------------


def cmd_validate(cfg: PublishConfig, files: list[dict], env_path: Path | None) -> int:
    ok = True
    print(f".env file   : {env_path if env_path else 'NOT FOUND'}")
    if env_path is None:
        print("  ✗ no .env found — copy .env.example to .env at the repo root and fill in")
        ok = False
    print(f"config title: {cfg.title!r}")
    print(f"config root : {cfg.root}")
    print(f"creators    : {len(cfg.creators)}")
    for c in cfg.creators:
        if not c.get("name") or c["name"].startswith("Last, First"):
            print("  ⚠ placeholder creator name — update publish.yml")
            ok = False
        if not _valid_orcid(c.get("orcid", "")):
            print(f"  ℹ creator {c.get('name')} has no real ORCID (optional)")
    print(f"files       : {len(files)}")
    for f in files:
        size_mb = f["size"] / 1e6
        print(f"  {f['name']:<30} {size_mb:>7.2f} MB  md5={f['md5']}")
    print("venues:")
    for v, conf in cfg.venues.items():
        env_var = {"zenodo": "ZENODO_TOKEN", "figshare": "FIGSHARE_TOKEN", "osf": "OSF_TOKEN"}[v]
        enabled = conf.get("enabled", False)
        missing = token_is_missing(env_var)
        status = "enabled" if enabled else "disabled"
        token_status = "placeholder/missing" if missing else "set"
        glyph = "✗" if enabled and missing else "✓"
        print(f"  {glyph} {v:<8} {status:<9} {env_var:<16} {token_status}")
        if enabled and missing:
            print(
                f"    → will be skipped: fill {env_var} in .env "
                "or set `enabled: false` in publish.yml"
            )
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("subcommand", choices=["validate", "zenodo", "figshare", "osf", "all"])
    p.add_argument("--config", type=Path, default=Path("publish.yml"))
    p.add_argument("--dry-run", action="store_true", help="skip the final publish step")
    p.add_argument("--state", type=Path, default=Path("publish.state.json"))
    p.add_argument(
        "--env", type=Path, default=None,
        help="Path to .env (default: walk upward from cwd)",
    )
    args = p.parse_args()

    env_path = args.env if args.env else _find_env_file()
    if env_path and env_path.is_file():
        load_dotenv(env_path)
        print(f"loaded env: {env_path}")
    else:
        print(
            "⚠ no .env file found — copy .env.example to .env at the repo root, "
            "fill in the tokens you have, then re-run.",
            file=sys.stderr,
        )
        # For `validate` we still want to run (it reports exactly what's missing).
        # For every other subcommand the per-venue token check will fail loudly.
        if args.subcommand != "validate":
            return 2

    if not args.config.exists():
        print(f"config not found: {args.config}", file=sys.stderr)
        return 2
    cfg = PublishConfig.load(args.config)
    state = State(args.state)

    workdir = Path(".publish_work")
    files = prepare_files(cfg, workdir)

    if args.subcommand == "validate":
        return cmd_validate(cfg, files, env_path)

    submitters = {
        "zenodo": ZenodoSubmitter,
        "figshare": FigshareSubmitter,
        "osf": OSFSubmitter,
    }
    targets = (
        [args.subcommand] if args.subcommand != "all"
        else [v for v in ("zenodo", "figshare", "osf") if cfg.venues.get(v, {}).get("enabled")]
    )

    errors = 0
    for venue in targets:
        if not cfg.venues.get(venue, {}).get("enabled", False):
            print(f"[{venue}] disabled in publish.yml — skipping")
            continue
        env_var = {"zenodo": "ZENODO_TOKEN", "figshare": "FIGSHARE_TOKEN", "osf": "OSF_TOKEN"}[venue]
        if token_is_missing(env_var):
            print(
                f"[{venue}] ⚠ skipped: {env_var} is placeholder/missing in .env — "
                f"fill it in or set `venues.{venue}.enabled: false` in publish.yml"
            )
            continue
        submitter = submitters[venue](cfg, state, dry_run=args.dry_run)
        try:
            submitter.submit(files)
        except requests.HTTPError as exc:
            print(f"[{venue}] FAILED: {exc}", file=sys.stderr)
            errors += 1

    # Tidy up the zipped working directory (keep the state file).
    shutil.rmtree(workdir, ignore_errors=True)
    print("final state:")
    print(json.dumps(state.all(), indent=2))
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
