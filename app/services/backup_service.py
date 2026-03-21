from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import shutil
import sqlite3
import os

from app.constants import BACKUP_FOLDER


CORE_BACKUP_ITEMS = [
    "app_dash.py",
    "logic.py",
    "models.py",
    "README.md",
    "requirements_dash.txt",
    "atelier.db",
    "assets",
    "scripts",
    "dress_images",
    "app",
]


RETENTION_BACKUPS_ENV = "APP_BACKUP_RETENTION_COUNT"
RETENTION_RELEASES_ENV = "APP_RELEASE_RETENTION_COUNT"


def _project_root() -> Path:
    # app/services/backup_service.py -> project root
    return Path(__file__).resolve().parents[2]


def _safe_label(value: str | None) -> str:
    raw = (value or "manual").strip().lower()
    clean = re.sub(r"[^a-z0-9_-]+", "_", raw)
    clean = clean.strip("_")
    return clean or "manual"


def _copy_item(src: Path, dst: Path) -> None:
    if src.is_dir():
        shutil.copytree(src, dst)
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _copy_sqlite_db_safe(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(src)) as src_conn:
        with sqlite3.connect(str(dst)) as dst_conn:
            src_conn.backup(dst_conn)


def _read_keep_count(env_name: str) -> int | None:
    raw = (os.environ.get(env_name, "") or "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if value > 0 else None


def _prune_snapshot_dirs(backups_dir: Path, keep_count: int) -> list[str]:
    candidates = []
    for p in backups_dir.iterdir():
        if p.is_dir() and (p / "manifest.txt").exists():
            candidates.append(p)
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    removed: list[str] = []
    for old in candidates[keep_count:]:
        shutil.rmtree(old, ignore_errors=True)
        removed.append(str(old))
    return removed


def _prune_release_archives(releases_dir: Path, keep_count: int) -> list[str]:
    candidates = [p for p in releases_dir.glob("*.zip") if p.is_file()]
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    removed: list[str] = []
    for old in candidates[keep_count:]:
        try:
            old.unlink(missing_ok=True)
            removed.append(str(old))
        except OSError:
            continue
    return removed


def create_backup_snapshot(
    label: str = "manual",
    include_zip: bool = True,
) -> dict:
    root = _project_root()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_label = _safe_label(label)

    backups_dir = root / BACKUP_FOLDER
    backups_dir.mkdir(parents=True, exist_ok=True)
    snapshot_dir = backups_dir / f"{safe_label}_{ts}"
    snapshot_dir.mkdir(parents=True, exist_ok=False)

    copied: list[str] = []
    missing: list[str] = []
    warnings: list[str] = []
    for rel in CORE_BACKUP_ITEMS:
        src = root / rel
        if not src.exists():
            missing.append(rel)
            continue
        dst = snapshot_dir / rel
        if rel == "atelier.db":
            try:
                _copy_sqlite_db_safe(src, dst)
            except Exception as e:
                # Fallback keeps backup flow operational on non-sqlite or locked-edge cases.
                _copy_item(src, dst)
                warnings.append(f"sqlite_backup_fallback:{e}")
        else:
            _copy_item(src, dst)
        copied.append(rel)

    manifest_path = snapshot_dir / "manifest.txt"
    manifest_lines = [
        f"timestamp={ts}",
        f"label={safe_label}",
        f"snapshot_dir={snapshot_dir}",
        f"copied_count={len(copied)}",
        "copied_items=" + ",".join(copied),
        f"missing_count={len(missing)}",
        "missing_items=" + ",".join(missing),
        f"warning_count={len(warnings)}",
        "warnings=" + "|".join(warnings),
    ]
    manifest_path.write_text("\n".join(manifest_lines), encoding="utf-8")

    zip_path = None
    releases_dir = root / "releases"
    if include_zip:
        releases_dir.mkdir(parents=True, exist_ok=True)
        zip_base = releases_dir / f"{safe_label}_{ts}"
        zip_file = Path(shutil.make_archive(str(zip_base), "zip", root_dir=snapshot_dir))
        zip_path = str(zip_file)

    pruned_backups: list[str] = []
    pruned_releases: list[str] = []
    keep_backups = _read_keep_count(RETENTION_BACKUPS_ENV)
    keep_releases = _read_keep_count(RETENTION_RELEASES_ENV)
    if keep_backups:
        pruned_backups = _prune_snapshot_dirs(backups_dir, keep_backups)
    if keep_releases and releases_dir.exists():
        pruned_releases = _prune_release_archives(releases_dir, keep_releases)

    if pruned_backups or pruned_releases:
        with manifest_path.open("a", encoding="utf-8") as mf:
            mf.write("\n")
            mf.write(f"pruned_backups_count={len(pruned_backups)}\n")
            mf.write("pruned_backups=" + "|".join(pruned_backups) + "\n")
            mf.write(f"pruned_releases_count={len(pruned_releases)}\n")
            mf.write("pruned_releases=" + "|".join(pruned_releases) + "\n")

    return {
        "ok": True,
        "label": safe_label,
        "timestamp": ts,
        "snapshot_dir": str(snapshot_dir),
        "zip_path": zip_path,
        "copied_items": copied,
        "missing_items": missing,
        "warnings": warnings,
        "pruned_backups": pruned_backups,
        "pruned_releases": pruned_releases,
        "retention_backups_keep": keep_backups,
        "retention_releases_keep": keep_releases,
        "manifest_path": str(manifest_path),
    }
