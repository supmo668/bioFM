#!/usr/bin/env python3
"""Submit paper + supplement to preprint venues via their HTTP APIs.

Reads metadata from ``publish.yml`` and dispatches to Zenodo / Figshare /
OSF. Writes DOIs and deposition IDs into the release's state file
(``publish.yml`` ``state_file``, anchored to publish.yml's directory) so a
run can be resumed. Records of superseded releases (SUPERSEDED_RECORDS) and
published records are never written to (PublishedRecordError), with exactly
two named exceptions (ALLOWED_REVISIONS): a Zenodo new version from 20074427
and the next version of Figshare article 32086920, selected by
``venues.<venue>.revision_of`` in publish.yml.

Two-step deposit: ``--dry-run`` CREATES a new draft (or prepares the revision,
unpublished), uploads the files and sets the metadata, without publishing. A
later run without ``--dry-run``
only publishes a draft recorded in the state file (DraftRequiredError
otherwise), and refuses if a recorded file's content changed
(DraftMismatchError).

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
    --state    — path to the resumable state file (default: publish.yml state_file).
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
    version: str = ""
    state_file: str = ""

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
            version=str(raw.get("version") or ""),
            state_file=str(raw.get("state_file") or ""),
        )


def resolve_state_path(cli_state: Path | None, cfg: "PublishConfig") -> Path:
    """--state if given, else the release's own state file from publish.yml, else the legacy one.

    A path from publish.yml is anchored to publish.yml's directory, not the current working
    directory, so the two principal gos (create, then publish) always share one state file
    whichever directory they are run from. It must stay inside that directory and must not be
    a symlink.
    """
    if cli_state is not None:
        return cli_state
    path = Path(cfg.state_file or "publish.state.json")
    if not path.is_absolute():
        path = cfg.root / path
    root = cfg.root.resolve()
    if path.is_symlink() or root not in path.resolve().parents:
        raise ValueError(f"state_file must be a regular file inside {root}: {cfg.state_file!r}")
    return path


# Published records of earlier releases. They are never written to, whatever a state file says,
# with EXACTLY the two exceptions in ALLOWED_REVISIONS.
SUPERSEDED_RECORDS: dict[str, frozenset] = {
    # 20074427 = v0.5.2, the newest published v0.5.x record (found by the read-only GETs).
    "zenodo": frozenset({19716140, 19716141, 19721470, 19748260, 20060974, 20074427}),
    "figshare": frozenset({32086920}),
    "osf": frozenset({"wmeuy", "dhu4z_v1"}),
}

# The only two operations permitted on a published record (principal D-1 = B, CTO #647): v0.6.0
# supersedes the v0.5.x record as a NEW VERSION, so no duplicate record exists.
#   zenodo:   POST actions/newversion on 20074427 (latest under concept 19716140) -- nothing else
#             is ever sent to 20074427; files are replaced on the NEW draft only.
#   figshare: metadata update + file replacement on article 32086920, published as its next
#             version; the public version must not change during a dry run.
# Any other id, venue or verb on a superseded record still raises PublishedRecordError.
ALLOWED_REVISIONS: dict[str, int] = {"zenodo": 20074427, "figshare": 32086920}
# The Zenodo concept record the permitted new version must belong to.
ZENODO_CONCEPT = 19716140
# The Figshare public version the permitted revision starts from (the .v5 relation in publish.yml).
FIGSHARE_BASE_VERSION = 5


def _revision_target(venue: str, vcfg: dict) -> int | None:
    """publish.yml venues.<venue>.revision_of, which must name exactly the allowed record."""
    rev = vcfg.get("revision_of")
    if rev is None:
        return None
    if venue not in ALLOWED_REVISIONS or type(rev) is not int or rev != ALLOWED_REVISIONS[venue]:
        raise PublishedRecordError(
            f"{venue}: revision_of {rev!r} is not the one permitted revision "
            f"({ALLOWED_REVISIONS.get(venue)!r}); published records are never mutated otherwise."
        )
    return rev


class PublishedRecordError(RuntimeError):
    """A venue's record is already published (or superseded) and is never mutated."""


class DraftRequiredError(RuntimeError):
    """A publish run found no recorded draft: create and review it with --dry-run first."""


class DraftMismatchError(RuntimeError):
    """The recorded draft already holds a same-name file with different content."""


def _refuse_superseded(venue: str, *ids: Any, allow: int | None = None) -> None:
    """Refuse any superseded record id, except ``allow`` when it is the venue's permitted
    revision target (ALLOWED_REVISIONS) -- never a wider exception."""
    if allow is not None and allow != ALLOWED_REVISIONS.get(venue):
        raise PublishedRecordError(f"{venue}: {allow!r} is not a permitted revision target")
    superseded = {str(x) for x in SUPERSEDED_RECORDS[venue]}
    for i in ids:
        # Compared as strings, so a hand-edited "32086920" (str) is refused like 32086920 (int).
        if i is not None and str(i) in superseded and str(i) != str(allow):
            raise PublishedRecordError(
                f"{venue} record {i} is already published (a superseded release) and is never "
                "mutated; the only permitted change is the named revision in ALLOWED_REVISIONS."
            )


def _state_id(venue: str, key: str, value: Any) -> int | None:
    """Record ids in a state file must be real integers (not str/float/bool), so no comparison
    against SUPERSEDED_RECORDS or ALLOWED_REVISIONS can be dodged by a type change."""
    if value is None:
        return None
    if type(value) is not int:
        raise PublishedRecordError(f"{venue}: state {key} {value!r} is not an integer id")
    return value


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
    """Byte-reproducible zip: sorted entries, fixed timestamps and permissions.

    The create run and the later publish run re-zip the same directories; identical bytes give
    identical md5s, so the publish run recognises the files it already uploaded.
    """
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(q for q in src.rglob("*") if q.is_file()):
            info = zipfile.ZipInfo(p.relative_to(src.parent).as_posix(), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())


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
        self.base = "https://sandbox.zenodo.org/api" if sandbox else "https://zenodo.org/api"
        if token_is_missing("ZENODO_TOKEN"):
            raise RuntimeError(
                "ZENODO_TOKEN missing or placeholder — fill it in .env "
                "(see .env.example at repo root)"
            )
        self.headers = {"Authorization": f"Bearer {os.environ['ZENODO_TOKEN']}"}
        self.vcfg = vcfg

    def _new_version_of(self, rev: int) -> tuple[int, str]:
        """The one permitted Zenodo operation on a published record: POST actions/newversion on
        ``rev``. Everything after that acts on the NEW draft (its own id), never on ``rev``."""
        if rev != ALLOWED_REVISIONS["zenodo"]:
            raise PublishedRecordError(f"zenodo: newversion on {rev} is not permitted")
        r = requests.post(
            f"{self.base}/deposit/depositions/{rev}/actions/newversion",
            headers=self.headers,
            timeout=60,
        )
        _raise_on(r)
        draft_url = r.json()["links"]["latest_draft"]
        prefix = f"{self.base}/deposit/depositions/"
        if not isinstance(draft_url, str) or not draft_url.startswith(prefix):
            raise PublishedRecordError(
                f"zenodo: newversion returned an unexpected draft URL {draft_url!r}"
            )
        r = requests.get(draft_url, headers=self.headers, timeout=30)
        _raise_on(r)
        draft = r.json()
        new_id = _state_id("zenodo", "draft id", draft.get("id"))
        _refuse_superseded("zenodo", new_id)  # the new version is never a superseded record
        bucket = draft.get("links", {}).get("bucket")
        if (
            new_id is None
            or draft_url != f"{prefix}{new_id}"
            or new_id <= rev
            or str(draft.get("conceptrecid")) != str(ZENODO_CONCEPT)
            or not isinstance(bucket, str)
            or not bucket.startswith(f"{self.base}/files/")
        ):
            raise PublishedRecordError(
                f"zenodo: the new-version draft does not belong to concept "
                f"{ZENODO_CONCEPT} as expected (id {new_id}, url {draft_url})"
            )
        if draft.get("submitted") or draft.get("state") != "unsubmitted":
            raise PublishedRecordError(f"zenodo: new-version draft {new_id} is not an open draft")
        self.state.set("zenodo", "deposit_id", new_id)
        self.state.set("zenodo", "bucket", bucket)
        self.state.set("zenodo", "revision_of", rev)
        self._remove_draft_files(new_id, [f["id"] for f in draft.get("files", [])])
        return new_id, bucket

    def _remove_draft_files(self, dep_id: int, file_ids: list) -> None:
        """Delete files on the (unpublished) new-version draft only, then record that the
        inherited files are gone; a run interrupted before that resumes the removal."""
        _refuse_superseded("zenodo", dep_id)
        for fid in file_ids:
            r = requests.delete(
                f"{self.base}/deposit/depositions/{dep_id}/files/{fid}",
                headers=self.headers,
                timeout=30,
            )
            _raise_on(r)
        self.state.set("zenodo", "inherited_files_removed", True)

    def _draft_files(self, dep_id: int) -> list:
        r = requests.get(
            f"{self.base}/deposit/depositions/{dep_id}/files", headers=self.headers, timeout=30
        )
        _raise_on(r)
        return r.json() or []

    def submit(self, files: list[dict]) -> str:
        dep_id = _state_id("zenodo", "deposit_id", self.state.get("zenodo", "deposit_id"))
        rev = _revision_target("zenodo", self.vcfg)
        _refuse_superseded("zenodo", dep_id)
        if (
            rev is not None
            and dep_id is not None
            and self.state.get("zenodo", "revision_of") != rev
        ):
            raise PublishedRecordError(
                f"zenodo: the state file records draft {dep_id}, which is not the new version of "
                f"{rev}; discard that draft and clear the state before preparing the revision."
            )
        if dep_id is not None and self.state.get("zenodo", "published"):
            # A published Zenodo deposit is locked: uploading into its bucket fails, and a
            # new release must be a NEW VERSION created from the latest version
            # (POST .../actions/newversion) under the same concept DOI. Fail closed rather
            # than PUT into a locked bucket or overwrite the published record's metadata.
            raise PublishedRecordError(
                f"zenodo deposit {dep_id} is already published and is never mutated. A new "
                "release is a new version from the permitted revision target (publish.yml "
                "venues.zenodo.revision_of; see 'Deposit-time sequence')."
            )
        existing: dict[str, str] = {}
        if dep_id is None:
            if not self.dry_run:
                # Creating and publishing are two separate principal gos: a publish run only
                # publishes a draft that a --dry-run created and that was reviewed.
                raise DraftRequiredError(
                    "zenodo: no recorded draft in the state file; create it with --dry-run "
                    "first and review it before publishing."
                )
            if rev is not None:
                dep_id, bucket = self._new_version_of(rev)
            else:
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
            if not self.dry_run and not self.state.get("zenodo", "prepared"):
                raise DraftRequiredError(
                    f"zenodo: draft {dep_id} was not fully prepared by a completed --dry-run; "
                    "run --dry-run again and review it before publishing."
                )
            # The bucket is re-read from the venue, never trusted from the state file alone.
            r = requests.get(
                f"{self.base}/deposit/depositions/{dep_id}", headers=self.headers, timeout=30
            )
            _raise_on(r)
            bucket = (r.json().get("links") or {}).get("bucket")
            if bucket != self.state.get("zenodo", "bucket"):
                raise DraftMismatchError(
                    f"zenodo: draft {dep_id}'s bucket differs from the state file's; stop."
                )
            if rev is not None and not self.state.get("zenodo", "inherited_files_removed"):
                if not self.dry_run:
                    raise DraftRequiredError(
                        "zenodo: inherited files were not removed; dry-run again"
                    )
                self._remove_draft_files(dep_id, [f["id"] for f in self._draft_files(dep_id)])
            existing = {e["filename"]: e.get("checksum", "") for e in self._draft_files(dep_id)}

        for f in files:
            if f["name"] in existing:
                if existing[f["name"]] == f["md5"]:
                    print(f"[zenodo] skip existing file {f['name']} (md5 match)")
                    continue
                raise DraftMismatchError(
                    f"zenodo draft {dep_id} already holds {f['name']} with different content; "
                    "the files changed since the draft was created and reviewed."
                )
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
                        **(
                            {"orcid": c["orcid"]}
                            if c.get("orcid") and _valid_orcid(c["orcid"])
                            else {}
                        ),
                    }
                    for c in self.cfg.creators
                ],
                "keywords": self.cfg.keywords,
                "license": self.cfg.license.replace("_", "-"),
                "access_right": "open",
                "related_identifiers": self.vcfg.get("related_identifiers", []),
                **({"version": self.cfg.version} if self.cfg.version else {}),
                # Version note (publish.yml venues.zenodo.notes): the record's place in the chain.
                **({"notes": self.vcfg["notes"].strip()} if self.vcfg.get("notes") else {}),
                "communities": [{"identifier": c} for c in self.vcfg.get("communities", [])],
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

        # The draft must hold exactly the release's files (no inherited leftovers, none missing).
        names = sorted(e.get("filename") for e in self._draft_files(dep_id))
        if names != sorted(f["name"] for f in files):
            raise DraftMismatchError(
                f"zenodo draft {dep_id} holds {names}, not the release's files"
            )
        if self.dry_run:
            self.state.set("zenodo", "prepared", True)
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

    def _public_snapshot(self, art_id: int) -> tuple:
        """The PUBLIC view of an article (no auth): its version and file md5s."""
        r = requests.get(f"{self.base}/articles/{art_id}", timeout=30)
        _raise_on(r)
        b = r.json()
        files = sorted(
            (f.get("name"), f.get("computed_md5") or f.get("supplied_md5"))
            for f in b.get("files", [])
        )
        return b.get("version"), files

    def _remove_inherited_files(self, art_id: int) -> None:
        """Remove the published version's files from the article's draft state, so the next
        version carries only the new files. Only for the permitted revision target."""
        if art_id != ALLOWED_REVISIONS["figshare"]:
            raise PublishedRecordError(f"figshare: file replacement on {art_id} is not permitted")
        r = requests.get(
            f"{self.base}/account/articles/{art_id}/files", headers=self.headers, timeout=30
        )
        _raise_on(r)
        for f in r.json() or []:
            r = requests.delete(
                f"{self.base}/account/articles/{art_id}/files/{f['id']}",
                headers=self.headers,
                timeout=30,
            )
            _raise_on(r)
        self.state.set("figshare", "inherited_files_removed", True)

    def _check_public(self, art_id: int) -> None:
        """The PUBLIC view must still equal the baseline recorded when the revision started (the
        base version and its files) on every run that touches the article, up to the publish."""
        base = self.state.get("figshare", "public_baseline")
        if not base:
            raise PublishedRecordError(
                f"figshare article {art_id}: no recorded public baseline; prepare with --dry-run"
            )
        version, files = self._public_snapshot(art_id)
        if [version, [list(x) for x in files]] != base:
            raise PublishedRecordError(
                f"figshare article {art_id}: its PUBLIC version changed (now v{version}); stop "
                "and inspect before anything else (the revision must stay unpublished)."
            )

    def submit(self, files: list[dict]) -> str:
        art_id = _state_id("figshare", "article_id", self.state.get("figshare", "article_id"))
        rev = _revision_target("figshare", self.vcfg)
        _refuse_superseded("figshare", art_id, allow=rev)
        if (
            rev is not None
            and art_id is not None
            and (art_id != rev or self.state.get("figshare", "revision_of") != rev)
        ):
            raise PublishedRecordError(
                f"figshare: the state file records article {art_id}, which is not the revision of "
                f"{rev}; discard that draft and clear the state before preparing the revision."
            )
        if art_id is not None and self.state.get("figshare", "published"):
            # Uploading into a published article adds the new files BESIDE the old ones and
            # republishes the article in place without updating its title, description or
            # authors -- the new release would carry the previous version's metadata. Fail
            # closed until the deposit-time sequence (publish.yml) is followed.
            raise PublishedRecordError(
                f"figshare article {art_id} was already published by this release and is never "
                "mutated again (see publish.yml, 'Deposit-time sequence')."
            )
        payload = {
            "title": self.cfg.title,
            "description": self.cfg.description,
            "tags": self.cfg.keywords,
            "categories": self.vcfg.get("categories", []),
            "defined_type": self.vcfg.get("defined_type", "preprint"),
            "license": _figshare_license(self.cfg.license),
            # No "authors": Figshare adds the token holder (the account owner, named by their
            # profile) as an author automatically, so sending the creator by name listed the
            # same person twice on the v0.6.0 draft (2026-10-16). The author is the profile
            # name; it differs ON PURPOSE in form from publish.yml's "Family, Given" creator,
            # and a publish run checks it against venues.figshare.expected_author.
            # Lineage links (publish.yml venues.figshare.references).
            **(
                {"references": list(self.vcfg["references"])} if self.vcfg.get("references") else {}
            ),
        }
        if art_id is None and rev is not None:
            # Start the one permitted revision: the published article's next version. Its
            # public version must not change until the separate publish go.
            if not self.dry_run:
                raise DraftRequiredError(
                    "figshare: no recorded revision in the state file; prepare it with "
                    "--dry-run first and review it before publishing."
                )
            version, pub_files = self._public_snapshot(rev)
            if version != FIGSHARE_BASE_VERSION or not pub_files:
                raise PublishedRecordError(
                    f"figshare article {rev}: public version is v{version} with "
                    f"{len(pub_files)} files; the revision starts only from "
                    f"v{FIGSHARE_BASE_VERSION} (publish.yml relations assume it)."
                )
            art_id = rev
            self.state.set("figshare", "article_id", rev)
            self.state.set("figshare", "revision_of", rev)
            self.state.set("figshare", "doi", f"10.6084/m9.figshare.{rev}")
            self.state.set("figshare", "public_baseline", [version, [list(x) for x in pub_files]])
            r = requests.put(
                f"{self.base}/account/articles/{rev}",
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            _raise_on(r)
            self._check_public(rev)  # a metadata edit must not reach the public version
            self._remove_inherited_files(rev)
            self._check_public(rev)
        elif art_id is not None:
            if not self.dry_run and not self.state.get("figshare", "prepared"):
                raise DraftRequiredError(
                    f"figshare: article {art_id} was not fully prepared by a completed --dry-run; "
                    "run --dry-run again and review it before publishing."
                )
            if rev is not None:
                self._check_public(rev)  # before any write on a resumed revision
            # Resuming the recorded (unpublished) draft: send the current publish.yml metadata
            # again, so a fix made after the review is what gets published.
            r = requests.put(
                f"{self.base}/account/articles/{art_id}",
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            _raise_on(r)
            if rev is not None and not self.state.get("figshare", "inherited_files_removed"):
                if not self.dry_run:
                    raise DraftRequiredError(
                        "figshare: inherited files were not removed; dry-run again"
                    )
                self._remove_inherited_files(rev)
        else:
            if not self.dry_run:
                raise DraftRequiredError(
                    "figshare: no recorded draft in the state file; create it with --dry-run "
                    "first and review it before publishing."
                )
            r = requests.post(
                f"{self.base}/account/articles",
                headers={**self.headers, "Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            _raise_on(r)
            art_id = int(r.json()["location"].rsplit("/", 1)[-1])
            self.state.set("figshare", "article_id", art_id)

        # Idempotency: Figshare accepts multiple files with the same name
        # and does not return a 4xx on duplicate upload, so resume runs
        # would silently accumulate copies. Query current files first and
        # skip any name that already exists (compare on MD5 for safety).
        existing_resp = requests.get(
            f"{self.base}/account/articles/{art_id}",
            headers=self.headers,
            timeout=30,
        )
        _raise_on(existing_resp)
        if not self.dry_run:
            # The author comes from the account profile, which the repository cannot set; a
            # minted DOI cannot be corrected, so the publish run checks it and stops if wrong
            # (fix the profile, never the payload).
            expected = self.vcfg.get("expected_author")
            names = [a.get("full_name") for a in existing_resp.json().get("authors", [])]
            if not expected or names != [expected]:
                raise DraftMismatchError(
                    f"figshare draft {art_id} authors are {names}; publishing needs exactly "
                    f"[{expected!r}] (publish.yml venues.figshare.expected_author). Fix the "
                    "account profile name; do not add authors to the payload."
                )
        existing_by_name: dict[str, str] = {}
        for existing in existing_resp.json().get("files", []):
            name = existing.get("name")
            md5 = existing.get("computed_md5") or existing.get("supplied_md5")
            if name:
                existing_by_name[name] = md5 or ""
        for f in files:
            if f["name"] in existing_by_name:
                if existing_by_name[f["name"]] == f["md5"]:
                    print(f"[figshare] skip existing file {f['name']} (md5 match)")
                    continue
                # Figshare would accept a second same-name file; a published record could not
                # be cleaned up afterwards, so refuse instead.
                raise DraftMismatchError(
                    f"figshare draft {art_id} already holds {f['name']} with different content; "
                    "the files changed since the draft was created and reviewed."
                )
            self._upload_file(art_id, f)

        reserved_doi = self.state.get("figshare", "doi")
        if not reserved_doi:
            r = requests.post(
                f"{self.base}/account/articles/{art_id}/reserve_doi",
                headers=self.headers,
                timeout=30,
            )
            _raise_on(r)
            reserved_doi = r.json().get("doi")
            self.state.set("figshare", "doi", reserved_doi)

        # The article must hold exactly the release's files (no inherited leftovers, none missing).
        r = requests.get(f"{self.base}/account/articles/{art_id}", headers=self.headers, timeout=30)
        _raise_on(r)
        held = sorted(f.get("name") for f in r.json().get("files", []))
        if held != sorted(f["name"] for f in files):
            raise DraftMismatchError(
                f"figshare article {art_id} holds {held}, not the release's files"
            )
        if not self.dry_run:
            # Every file must have finished processing: a published DOI cannot be fixed by
            # replacing a file, so publishing waits until all read "available" (CTO #651).
            pending = sorted(
                (f.get("name"), f.get("status"))
                for f in r.json().get("files", [])
                if f.get("status") != "available"
            )
            if pending:
                raise DraftMismatchError(
                    f"figshare article {art_id}: files still processing {pending}; publish waits "
                    "until every file reads 'available'."
                )
        if rev is not None:
            self._check_public(rev)  # still the base version, right before the publish go
        if self.dry_run:
            self.state.set("figshare", "prepared", True)
            print(f"[figshare] DRY-RUN — article {art_id} left in draft")
            return reserved_doi or ""

        r = requests.post(
            f"{self.base}/account/articles/{art_id}/publish",
            headers=self.headers,
            timeout=60,
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
            headers=self.headers,
            timeout=30,
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
            headers=self.headers,
            timeout=60,
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
                "OSF_TOKEN missing or placeholder — fill it in .env (see .env.example at repo root)"
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
        _revision_target("osf", self.vcfg)  # OSF has no permitted revision: any revision_of raises
        _refuse_superseded("osf", proj_id, self.state.get("osf", "preprint_id"))
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

        # Upload the first file as the "primary" preprint file. OSF's
        # preprint ``primary_file`` relationship wants the 5-char file
        # GUID (not the waterbutler path, not the project id). The
        # waterbutler response exposes a ``resource`` field that is the
        # project id — easy to confuse. Resolve the real GUID via the
        # v2 API after upload.
        primary = files[0]
        primary_id = self.state.get("osf", "primary_file_id")
        if primary_id is None:
            # Idempotency: if this file already exists on the project,
            # skip the upload and go straight to GUID resolution.
            existing_resp = requests.get(
                f"{self.files_api}/resources/{proj_id}/providers/osfstorage/",
                headers={"Authorization": self.headers["Authorization"]},
                timeout=60,
            )
            needs_upload = True
            if existing_resp.status_code < 400:
                for entry in existing_resp.json().get("data", []):
                    if entry.get("attributes", {}).get("name") == primary["name"]:
                        needs_upload = False
                        break
            if needs_upload:
                up_url = (
                    f"{self.files_api}/resources/{proj_id}/providers/osfstorage/"
                    f"?kind=file&name={primary['name']}"
                )
                up_headers = {"Authorization": self.headers["Authorization"]}
                with primary["path"].open("rb") as fh:
                    r = requests.put(up_url, headers=up_headers, data=fh, timeout=600)
                _raise_on(r)

            # Resolve the 5-char OSF file GUID via v2.
            files_resp = requests.get(
                f"{self.api}/nodes/{proj_id}/files/osfstorage/",
                headers={"Authorization": self.headers["Authorization"]},
                timeout=60,
            )
            _raise_on(files_resp)
            for entry in files_resp.json().get("data", []):
                if entry.get("attributes", {}).get("name") == primary["name"]:
                    primary_id = entry["id"]
                    break
            if not primary_id:
                raise RuntimeError(f"could not resolve OSF file GUID for {primary['name']}")
            self.state.set("osf", "primary_file_id", primary_id)

        # Additional files (supplement) uploaded same way. Skip if a file
        # with the same name already exists on the project — OSF's Waterbutler
        # rejects overwrite uploads with 409 and there is no stable
        # "replace" query parameter, so we list existing files and only
        # push the missing ones. This is also what keeps resumed runs
        # idempotent.
        existing_resp = requests.get(
            f"{self.files_api}/resources/{proj_id}/providers/osfstorage/",
            headers={"Authorization": self.headers["Authorization"]},
            timeout=60,
        )
        existing_names: set[str] = set()
        if existing_resp.status_code < 400:
            try:
                for entry in existing_resp.json().get("data", []):
                    name = (entry.get("attributes", {}) or {}).get("name")
                    if name:
                        existing_names.add(str(name))
            except ValueError:
                pass
        for f in files[1:]:
            if f["name"] in existing_names:
                print(f"[osf] skip existing file {f['name']}")
                continue
            r = requests.put(
                f"{self.files_api}/resources/{proj_id}/providers/osfstorage/"
                f"?kind=file&name={f['name']}",
                headers={"Authorization": self.headers["Authorization"]},
                data=f["path"].read_bytes(),
                timeout=600,
            )
            _raise_on(r)

        # Create the preprint record. **Keep the create payload minimal**
        # — OSF's gateway returns 502 when ``subjects`` and ``primary_file``
        # are included in the initial POST. Both go on follow-up PATCH.
        pp_id = self.state.get("osf", "preprint_id")
        if pp_id is None:
            payload = {
                "data": {
                    "type": "preprints",
                    "attributes": {
                        "title": self.cfg.title,
                        "description": self.cfg.description,
                        "tags": self.cfg.keywords,
                        "has_coi": False,
                        "conflict_of_interest_statement": "",
                    },
                    "relationships": {
                        "node": {"data": {"type": "nodes", "id": proj_id}},
                        "provider": {"data": {"type": "providers", "id": self.provider}},
                    },
                }
            }
            r = requests.post(
                f"{self.api}/preprints/",
                headers=self.headers,
                json=payload,
                timeout=60,
            )
            _raise_on(r)
            pp_id = r.json()["data"]["id"]
            self.state.set("osf", "preprint_id", pp_id)

        # PATCH subjects onto the created preprint (hierarchical-path shape).
        if not self.state.get("osf", "subjects_set"):
            subjects = self.vcfg.get("subjects", [])
            if subjects:
                patch = {
                    "data": {
                        "id": pp_id,
                        "type": "preprints",
                        "relationships": {
                            "subjects": {
                                "data": [[{"type": "subjects", "id": s}] for s in subjects]
                            }
                        },
                    }
                }
                r = requests.patch(
                    f"{self.api}/preprints/{pp_id}/",
                    headers=self.headers,
                    json=patch,
                    timeout=60,
                )
                _raise_on(r)
            self.state.set("osf", "subjects_set", True)

        # PATCH primary_file relationship once the preprint exists.
        if not self.state.get("osf", "primary_file_set"):
            r = requests.patch(
                f"{self.api}/preprints/{pp_id}/relationships/primary_file/",
                headers=self.headers,
                json={"data": {"type": "files", "id": primary_id}},
                timeout=60,
            )
            _raise_on(r)
            self.state.set("osf", "primary_file_set", True)

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
        doi_candidate = (
            r.json()["data"]["attributes"].get("preprint_doi_created")
            or f"10.17605/OSF.IO/{pp_id.upper()}"
        )
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
    p.add_argument(
        "--state",
        type=Path,
        default=None,
        help="state file (default: publish.yml state_file, else publish.state.json)",
    )
    p.add_argument(
        "--env",
        type=Path,
        default=None,
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
    state_path = resolve_state_path(args.state, cfg)
    print(f"state file : {state_path}")
    state = State(state_path)

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
        [args.subcommand]
        if args.subcommand != "all"
        else [v for v in ("zenodo", "figshare", "osf") if cfg.venues.get(v, {}).get("enabled")]
    )

    errors = 0
    for venue in targets:
        if not cfg.venues.get(venue, {}).get("enabled", False):
            print(f"[{venue}] disabled in publish.yml — skipping")
            continue
        env_var = {"zenodo": "ZENODO_TOKEN", "figshare": "FIGSHARE_TOKEN", "osf": "OSF_TOKEN"}[
            venue
        ]
        if token_is_missing(env_var):
            print(
                f"[{venue}] ⚠ skipped: {env_var} is placeholder/missing in .env — "
                f"fill it in or set `venues.{venue}.enabled: false` in publish.yml"
            )
            continue
        submitter = submitters[venue](cfg, state, dry_run=args.dry_run)
        try:
            submitter.submit(files)
        except (
            requests.HTTPError,
            PublishedRecordError,
            DraftRequiredError,
            DraftMismatchError,
        ) as exc:
            print(f"[{venue}] FAILED: {exc}", file=sys.stderr)
            errors += 1

    # Tidy up the zipped working directory (keep the state file).
    shutil.rmtree(workdir, ignore_errors=True)
    print("final state:")
    print(json.dumps(state.all(), indent=2))
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
