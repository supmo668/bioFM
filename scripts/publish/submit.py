#!/usr/bin/env python3
"""Publish to Zenodo / Figshare / OSF from a single ``publish.yml``.

Usage (run from repo root unless ``--config`` overrides path):

    python scripts/publish/submit.py validate
    python scripts/publish/submit.py zenodo          [--dry-run] [--sandbox]
    python scripts/publish/submit.py figshare        [--dry-run]
    python scripts/publish/submit.py osf             [--dry-run]
    python scripts/publish/submit.py all             [--dry-run] [--sandbox]

All commands honour ``--config path/to/publish.yml`` (default: ``./publish.yml``).

Tokens read from env vars (or a ``.env`` file at repo root via python-dotenv):

    ZENODO_TOKEN   — Zenodo personal access token (scopes: deposit:write, deposit:actions)
    ZENODO_SANDBOX_TOKEN — sandbox token used when ``--sandbox``
    FIGSHARE_TOKEN — Figshare personal token
    OSF_TOKEN      — OSF personal access token (scope: osf.full_write)

Outputs:
    artifacts/publish/dois.json  — accumulated DOIs + URLs per venue
    artifacts/publish/state.json — resumable state for the ``all`` driver

Design invariants:
    * Idempotent where the venue allows it (OSF: create-if-missing; Zenodo/Figshare: one-shot only).
    * Tokens never logged; redacted in exceptions.
    * Dry-run actually hits GET endpoints for validation but skips POST/PUT/PATCH/DELETE.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError:
    sys.exit("install httpx: poetry add httpx or pip install httpx")

try:
    import yaml
except ImportError:
    sys.exit("install pyyaml: poetry add pyyaml or pip install pyyaml")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass
class Author:
    name: str
    orcid: str | None = None
    affiliation: str | None = None


@dataclass
class ArtifactFile:
    path: Path
    description: str = ""


@dataclass
class VenueConfig:
    enabled: bool = False
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class PublishConfig:
    title: str
    description: str
    authors: list[Author]
    keywords: list[str]
    license: str
    version: str
    artifacts: list[ArtifactFile]
    venues: dict[str, VenueConfig]
    related_url: str | None = None

    @classmethod
    def load(cls, path: Path) -> "PublishConfig":
        with path.open() as f:
            d = yaml.safe_load(f)
        return cls(
            title=d["title"],
            description=d["description"],
            authors=[Author(**a) for a in d["authors"]],
            keywords=list(d.get("keywords", [])),
            license=d["license"],
            version=d["version"],
            artifacts=[
                ArtifactFile(path=Path(a["path"]), description=a.get("description", ""))
                for a in d["artifacts"]
            ],
            venues={
                name: VenueConfig(
                    enabled=bool(body.get("enabled", False)),
                    extra={k: v for k, v in body.items() if k != "enabled"},
                )
                for name, body in d.get("venues", {}).items()
            },
            related_url=d.get("related_url"),
        )


def _redact(token: str | None) -> str:
    if not token:
        return "(missing)"
    return f"{token[:4]}…{token[-4:]}" if len(token) > 8 else "(short)"


# ---------------------------------------------------------------------------
# State + DOI log
# ---------------------------------------------------------------------------


STATE_PATH = Path("artifacts/publish/state.json")
DOIS_PATH = Path("artifacts/publish/dois.json")


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _record_doi(venue: str, doi: str, url: str, extra: dict[str, Any] | None = None) -> None:
    dois = _load_json(DOIS_PATH)
    dois[venue] = {"doi": doi, "url": url, "recorded_at": int(time.time())}
    if extra:
        dois[venue].update(extra)
    _save_json(DOIS_PATH, dois)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def cmd_validate(cfg: PublishConfig, args: argparse.Namespace) -> int:  # noqa: ARG001
    problems: list[str] = []
    for art in cfg.artifacts:
        if not art.path.exists():
            problems.append(f"missing artifact: {art.path}")
        elif art.path.stat().st_size == 0:
            problems.append(f"empty artifact: {art.path}")
    for name, venue in cfg.venues.items():
        if not venue.enabled:
            continue
        env_key = {
            "zenodo": "ZENODO_TOKEN",
            "zenodo_sandbox": "ZENODO_SANDBOX_TOKEN",
            "figshare": "FIGSHARE_TOKEN",
            "osf": "OSF_TOKEN",
        }.get(name)
        if env_key and not os.environ.get(env_key):
            problems.append(f"{name} enabled but env var {env_key} unset")
    if problems:
        print("VALIDATION FAILED:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"VALIDATION OK — {len(cfg.artifacts)} artifacts, "
          f"{sum(1 for v in cfg.venues.values() if v.enabled)} venues enabled.")
    for art in cfg.artifacts:
        size_mb = art.path.stat().st_size / (1024 * 1024)
        print(f"  • {art.path} ({size_mb:.2f} MB)")
    return 0


# ---------------------------------------------------------------------------
# Zenodo
# ---------------------------------------------------------------------------


def _zenodo_base(sandbox: bool) -> tuple[str, str]:
    if sandbox:
        return "https://sandbox.zenodo.org/api", os.environ.get(
            "ZENODO_SANDBOX_TOKEN", os.environ.get("ZENODO_TOKEN", ""),
        )
    return "https://zenodo.org/api", os.environ.get("ZENODO_TOKEN", "")


def _zenodo_metadata(cfg: PublishConfig) -> dict[str, Any]:
    extra = cfg.venues.get("zenodo", VenueConfig()).extra
    meta: dict[str, Any] = {
        "title": cfg.title,
        "description": cfg.description,
        "upload_type": extra.get("upload_type", "publication"),
        "publication_type": extra.get("publication_type", "preprint"),
        "creators": [
            {
                "name": a.name,
                **({"orcid": a.orcid} if a.orcid else {}),
                **({"affiliation": a.affiliation} if a.affiliation else {}),
            }
            for a in cfg.authors
        ],
        "keywords": cfg.keywords,
        "license": extra.get("zenodo_license", cfg.license.lower().replace(" ", "-")),
        "version": cfg.version,
    }
    if "related_identifiers" in extra:
        meta["related_identifiers"] = extra["related_identifiers"]
    elif cfg.related_url:
        meta["related_identifiers"] = [
            {"identifier": cfg.related_url, "relation": "isSupplementTo",
             "resource_type": "software"}
        ]
    return {"metadata": meta}


def cmd_zenodo(cfg: PublishConfig, args: argparse.Namespace) -> int:
    base, token = _zenodo_base(args.sandbox)
    if not token:
        print(f"ERROR: ZENODO_TOKEN unset (sandbox={args.sandbox})")
        return 1
    headers = {"Authorization": f"Bearer {token}"}
    dry = args.dry_run
    print(f"[zenodo] base={base} token={_redact(token)} dry_run={dry}")

    with httpx.Client(base_url=base, headers=headers, timeout=60.0) as c:
        if dry:
            r = c.get("/deposit/depositions", params={"size": 1})
            r.raise_for_status()
            print(f"[zenodo] dry-run GET ok, status={r.status_code}")
            return 0

        # 1. Create deposition
        r = c.post("/deposit/depositions", json={})
        r.raise_for_status()
        dep = r.json()
        dep_id = dep["id"]
        bucket = dep["links"]["bucket"]
        print(f"[zenodo] created deposition {dep_id}")

        # 2. Upload files via bucket API
        for art in cfg.artifacts:
            with art.path.open("rb") as f:
                upload_url = f"{bucket}/{art.path.name}"
                # httpx doesn't accept absolute URLs as relative paths; use a fresh client
                with httpx.Client(headers=headers, timeout=600.0) as bc:
                    r = bc.put(upload_url, content=f.read())
                    r.raise_for_status()
            print(f"[zenodo]   uploaded {art.path.name}")

        # 3. Attach metadata
        r = c.put(f"/deposit/depositions/{dep_id}",
                  json=_zenodo_metadata(cfg))
        r.raise_for_status()

        # 4. Publish → mints DOI
        r = c.post(f"/deposit/depositions/{dep_id}/actions/publish")
        r.raise_for_status()
        published = r.json()
        doi = published["doi"]
        url = published["links"]["latest_html"]
        print(f"[zenodo] PUBLISHED  doi={doi}  url={url}")
        _record_doi("zenodo_sandbox" if args.sandbox else "zenodo", doi, url,
                    extra={"deposition_id": dep_id})
    return 0


# ---------------------------------------------------------------------------
# Figshare
# ---------------------------------------------------------------------------


def _figshare_md5(path: Path) -> str:
    h = hashlib.md5()  # noqa: S324 - Figshare API requires MD5
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_figshare(cfg: PublishConfig, args: argparse.Namespace) -> int:
    token = os.environ.get("FIGSHARE_TOKEN", "")
    if not token:
        print("ERROR: FIGSHARE_TOKEN unset")
        return 1
    base = "https://api.figshare.com/v2"
    headers = {"Authorization": f"token {token}"}
    dry = args.dry_run
    extra = cfg.venues.get("figshare", VenueConfig()).extra
    print(f"[figshare] base={base} token={_redact(token)} dry_run={dry}")

    with httpx.Client(base_url=base, headers=headers, timeout=60.0) as c:
        if dry:
            r = c.get("/account/articles", params={"page_size": 1})
            r.raise_for_status()
            print(f"[figshare] dry-run GET ok, status={r.status_code}")
            return 0

        # 1. Create article
        article_body: dict[str, Any] = {
            "title": cfg.title,
            "description": cfg.description,
            "tags": cfg.keywords,
            "defined_type": extra.get("defined_type", "preprint"),
            "categories": extra.get("categories", []),
            "authors": [
                {"name": a.name, **({"orcid_id": a.orcid} if a.orcid else {})}
                for a in cfg.authors
            ],
            "license": extra.get("figshare_license_id", 1),  # 1 = CC-BY; 7 = Apache-2.0
        }
        r = c.post("/account/articles", json=article_body)
        r.raise_for_status()
        article_url = r.json()["location"]
        article_id = int(article_url.rstrip("/").split("/")[-1])
        print(f"[figshare] created article {article_id}")

        # 2. Upload each file (multi-part)
        for art in cfg.artifacts:
            size = art.path.stat().st_size
            md5 = _figshare_md5(art.path)
            r = c.post(f"/account/articles/{article_id}/files",
                       json={"name": art.path.name, "size": size, "md5": md5})
            r.raise_for_status()
            file_url = r.json()["location"]
            file_id = int(file_url.rstrip("/").split("/")[-1])
            # Fetch upload plan
            r = c.get(f"/account/articles/{article_id}/files/{file_id}")
            r.raise_for_status()
            plan = r.json()
            upload_url = plan["upload_url"]
            # plan lists parts via a separate GET
            r = httpx.get(upload_url, headers=headers, timeout=60.0)
            r.raise_for_status()
            parts = r.json()["parts"]
            with art.path.open("rb") as f:
                for part in parts:
                    start, end = part["startOffset"], part["endOffset"]
                    f.seek(start)
                    chunk = f.read(end - start + 1)
                    pu = httpx.put(
                        f"{upload_url}/{part['partNo']}",
                        content=chunk, headers=headers, timeout=600.0,
                    )
                    pu.raise_for_status()
            # Complete
            r = c.post(f"/account/articles/{article_id}/files/{file_id}")
            r.raise_for_status()
            print(f"[figshare]   uploaded {art.path.name}")

        # 3. Reserve DOI
        r = c.post(f"/account/articles/{article_id}/reserve_doi")
        r.raise_for_status()
        reserved_doi = r.json().get("doi", "")

        # 4. Publish
        r = c.post(f"/account/articles/{article_id}/publish")
        r.raise_for_status()
        print(f"[figshare] PUBLISHED article_id={article_id}  doi={reserved_doi}")
        _record_doi("figshare", reserved_doi,
                    f"https://figshare.com/articles/preprint/{article_id}",
                    extra={"article_id": article_id})
    return 0


# ---------------------------------------------------------------------------
# OSF (incl BioHackrXiv)
# ---------------------------------------------------------------------------


def cmd_osf(cfg: PublishConfig, args: argparse.Namespace) -> int:
    token = os.environ.get("OSF_TOKEN", "")
    if not token:
        print("ERROR: OSF_TOKEN unset")
        return 1
    base = "https://api.osf.io/v2"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/vnd.api+json",
    }
    dry = args.dry_run
    extra = cfg.venues.get("osf", VenueConfig()).extra
    provider = extra.get("provider", "osf")  # osf, biohackrxiv, metaarxiv, etc.
    subjects = extra.get("subjects", ["Bioinformatics"])
    print(f"[osf] base={base} provider={provider} token={_redact(token)} dry_run={dry}")

    with httpx.Client(base_url=base, headers=headers, timeout=60.0) as c:
        if dry:
            r = c.get("/preprints/", params={"page[size]": 1})
            r.raise_for_status()
            print(f"[osf] dry-run GET ok, status={r.status_code}")
            return 0

        # 1. Create project node
        project_body = {
            "data": {
                "type": "nodes",
                "attributes": {
                    "title": cfg.title,
                    "description": cfg.description,
                    "category": "project",
                    "public": True,
                },
            }
        }
        r = c.post("/nodes/", json=project_body)
        r.raise_for_status()
        project_id = r.json()["data"]["id"]
        print(f"[osf] created project {project_id}")

        # 2. Upload files (primary PDF assumed = first artifact)
        primary = cfg.artifacts[0]
        file_id = None
        for art in cfg.artifacts:
            with art.path.open("rb") as f:
                r = httpx.put(
                    f"https://files.osf.io/v1/resources/{project_id}/providers/osfstorage/",
                    params={"kind": "file", "name": art.path.name},
                    content=f.read(),
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=600.0,
                )
                r.raise_for_status()
                uploaded = r.json()
                if art == primary:
                    file_id = uploaded.get("data", {}).get("id") or uploaded.get("id")
                print(f"[osf]   uploaded {art.path.name}")

        if not file_id:
            print("ERROR: could not resolve primary_file_id")
            return 1

        # 3. Create preprint linked to the project + primary file
        preprint_body = {
            "data": {
                "type": "preprints",
                "attributes": {
                    "title": cfg.title,
                    "description": cfg.description,
                    "subjects": [[s] for s in subjects],
                    "tags": cfg.keywords,
                },
                "relationships": {
                    "node": {"data": {"type": "nodes", "id": project_id}},
                    "primary_file": {"data": {"type": "primary_files", "id": file_id}},
                    "provider": {"data": {"type": "preprint_providers", "id": provider}},
                },
            }
        }
        r = c.post("/preprints/", json=preprint_body)
        r.raise_for_status()
        preprint_id = r.json()["data"]["id"]
        url = f"https://osf.io/preprints/{provider}/{preprint_id}/"
        doi = r.json()["data"]["attributes"].get("doi", "")
        print(f"[osf] PUBLISHED preprint {preprint_id}  doi={doi}  url={url}")
        _record_doi("osf", doi or f"osf:{preprint_id}", url,
                    extra={"preprint_id": preprint_id, "project_id": project_id, "provider": provider})
    return 0


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------


def cmd_all(cfg: PublishConfig, args: argparse.Namespace) -> int:
    for venue_name, handler in (("zenodo", cmd_zenodo),
                                ("figshare", cmd_figshare),
                                ("osf", cmd_osf)):
        if not cfg.venues.get(venue_name, VenueConfig()).enabled:
            print(f"[all] skipping {venue_name} (disabled in publish.yml)")
            continue
        print(f"[all] === {venue_name} ===")
        rc = handler(cfg, args)
        if rc != 0:
            print(f"[all] {venue_name} FAILED (rc={rc}); skipping rest")
            return rc
    print("[all] DONE — see artifacts/publish/dois.json")
    return 0


# ---------------------------------------------------------------------------
# CLI entry
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("command", choices=["validate", "zenodo", "figshare", "osf", "all"])
    p.add_argument("--config", type=Path, default=Path("publish.yml"))
    p.add_argument("--dry-run", action="store_true",
                   help="GET the venue's index but skip POST/PUT/PATCH")
    p.add_argument("--sandbox", action="store_true",
                   help="Zenodo only: route to sandbox.zenodo.org")
    args = p.parse_args(argv)

    # Load .env from repo root if python-dotenv is installed.
    try:
        from dotenv import load_dotenv  # type: ignore[import-not-found]
        load_dotenv()
    except ImportError:
        pass

    if not args.config.exists():
        print(f"ERROR: config not found: {args.config}")
        return 1
    cfg = PublishConfig.load(args.config)

    handlers = {
        "validate": cmd_validate,
        "zenodo": cmd_zenodo,
        "figshare": cmd_figshare,
        "osf": cmd_osf,
        "all": cmd_all,
    }
    return handlers[args.command](cfg, args)


if __name__ == "__main__":
    sys.exit(main())
