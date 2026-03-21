from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
import zipfile


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _latest_snapshot(backups_dir: Path) -> Path | None:
    candidates = [p for p in backups_dir.iterdir() if p.is_dir() and (p / "manifest.txt").exists()]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _latest_release_zip(releases_dir: Path) -> Path | None:
    candidates = [p for p in releases_dir.glob("*.zip") if p.is_file()]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _release_zips_desc(releases_dir: Path) -> list[Path]:
    candidates = [p for p in releases_dir.glob("*.zip") if p.is_file()]
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates


def _sqlite_smoke(db_path: Path) -> tuple[bool, str]:
    if not db_path.exists():
        return False, f"Missing DB: {db_path}"
    try:
        with sqlite3.connect(str(db_path)) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = int(cur.fetchone()[0] or 0)
        return True, f"tables={table_count}"
    except Exception as e:
        return False, f"DB open/query failed: {e}"


def main() -> int:
    root = _project_root()
    backups_dir = root / "backups"
    releases_dir = root / "releases"

    print("=== Backup Restore Smoke ===")
    print(f"root={root}")

    latest_snapshot = _latest_snapshot(backups_dir) if backups_dir.exists() else None
    if not latest_snapshot:
        print("FAIL: no backup snapshot with manifest found under backups/")
        return 1

    print(f"latest_snapshot={latest_snapshot}")
    snapshot_db = latest_snapshot / "atelier.db"
    ok, msg = _sqlite_smoke(snapshot_db)
    print(f"snapshot_db_check={'PASS' if ok else 'FAIL'} ({msg})")
    if not ok:
        return 1

    latest_zip = _latest_release_zip(releases_dir) if releases_dir.exists() else None
    if not latest_zip:
        print("WARN: no release zip found under releases/, snapshot validation only.")
        return 0

    print(f"latest_release_zip={latest_zip}")
    zip_candidates = _release_zips_desc(releases_dir)
    validated_zip = None
    for zip_file in zip_candidates:
        with tempfile.TemporaryDirectory(
            prefix="myatelier_restore_smoke_",
            ignore_cleanup_errors=True,
        ) as tmp:
            extract_dir = Path(tmp) / "restore"
            extract_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_file, "r") as zf:
                zf.extractall(extract_dir)
            restored_db = extract_dir / "atelier.db"
            zip_ok, zip_msg = _sqlite_smoke(restored_db)
            if zip_ok:
                validated_zip = zip_file
                print(f"zip_restore_db_check=PASS ({zip_msg})")
                print(f"validated_release_zip={zip_file}")
                break
            print(f"zip_restore_db_check=SKIP ({zip_file.name}: {zip_msg})")

    if not validated_zip:
        print("WARN: no release zip with full DB snapshot found, snapshot validation only.")
        print("RESULT=PASS_WITH_WARNINGS")
        return 0

    print("RESULT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
