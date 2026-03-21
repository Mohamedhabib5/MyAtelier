import argparse
import json
from pathlib import Path


REQUIRED_TOP_LEVEL_KEYS = [
    "schema_version",
    "project",
    "generated_at",
    "critical_component_ids",
    "invariants",
]

REQUIRED_INVARIANT_KEYS = [
    "id",
    "title",
    "expected",
    "verification",
]

MOJIBAKE_MARKERS = [
    "ط§ظ",
    "ط¥ط",
    "â€",
    "âڑ",
    "â‌",
    "�",
]


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_critical_string_ids(critical_component_ids):
    ids = []
    for group_value in critical_component_ids.values():
        if not isinstance(group_value, list):
            continue
        for item in group_value:
            if isinstance(item, str):
                ids.append(item)
    return ids


def _scan_python_sources(root: Path):
    files = []
    files.extend((root / "app").rglob("*.py"))
    for rel in ["app_dash.py", "logic.py", "models.py"]:
        p = root / rel
        if p.exists():
            files.append(p)
    return files


def _find_mojibake_hits(text: str):
    hits = []
    for marker in MOJIBAKE_MARKERS:
        if marker in text:
            hits.append(marker)
    return hits


def run_lint(constitution_path: Path, project_root: Path):
    report = {
        "ok": True,
        "errors": [],
        "warnings": [],
    }

    try:
        data = _load_json(constitution_path)
    except Exception as exc:
        report["ok"] = False
        report["errors"].append(f"Invalid JSON: {exc}")
        return report

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            report["ok"] = False
            report["errors"].append(f"Missing top-level key: {key}")

    invariants = data.get("invariants", [])
    if not isinstance(invariants, list):
        report["ok"] = False
        report["errors"].append("`invariants` must be a list")
        invariants = []

    seen_ids = set()
    for idx, inv in enumerate(invariants):
        if not isinstance(inv, dict):
            report["ok"] = False
            report["errors"].append(f"Invariant at index {idx} must be an object")
            continue
        for key in REQUIRED_INVARIANT_KEYS:
            if key not in inv:
                report["ok"] = False
                report["errors"].append(f"Invariant {inv.get('id', idx)} missing key: {key}")
        if "trigger" not in inv and "context" not in inv:
            report["ok"] = False
            report["errors"].append(
                f"Invariant {inv.get('id', idx)} must include `trigger` or `context`"
            )
        inv_id = inv.get("id")
        if isinstance(inv_id, str):
            if inv_id in seen_ids:
                report["ok"] = False
                report["errors"].append(f"Duplicate invariant id: {inv_id}")
            seen_ids.add(inv_id)
        verification = inv.get("verification")
        if not isinstance(verification, list) or len(verification) == 0:
            report["ok"] = False
            report["errors"].append(f"Invariant {inv.get('id', idx)} must have non-empty verification list")

    critical_component_ids = data.get("critical_component_ids", {})
    critical_ids = _collect_critical_string_ids(critical_component_ids)

    source_files = _scan_python_sources(project_root)
    source_blob_parts = []
    mojibake_hits_in_code = []
    for src in source_files:
        txt = src.read_text(encoding="utf-8", errors="replace")
        source_blob_parts.append(txt)
        hits = _find_mojibake_hits(txt)
        if hits:
            mojibake_hits_in_code.append({"file": str(src), "markers": sorted(set(hits))})
    source_blob = "\n".join(source_blob_parts)

    missing_ids = [cid for cid in critical_ids if cid not in source_blob]
    if missing_ids:
        report["ok"] = False
        report["errors"].append(f"Missing critical component IDs in source: {len(missing_ids)}")
        report["missing_critical_ids"] = missing_ids

    constitution_text = constitution_path.read_text(encoding="utf-8", errors="replace")
    mojibake_in_constitution = _find_mojibake_hits(constitution_text)
    if mojibake_in_constitution:
        report["ok"] = False
        report["errors"].append("Mojibake markers found in constitution file")
        report["mojibake_in_constitution"] = sorted(set(mojibake_in_constitution))

    if mojibake_hits_in_code:
        report["ok"] = False
        report["errors"].append("Mojibake markers found in source code")
        report["mojibake_in_code"] = mojibake_hits_in_code

    report["summary"] = {
        "invariants_count": len(invariants),
        "critical_string_ids_count": len(critical_ids),
        "missing_critical_ids_count": len(missing_ids),
        "source_files_scanned": len(source_files),
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="Lint constitution invariants against source code.")
    parser.add_argument(
        "--file",
        default="codex_app_invariants_myatelier_full.json",
        help="Path to constitution JSON file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON report.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    constitution_path = (root / args.file).resolve()
    report = run_lint(constitution_path, root)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        if report["ok"]:
            print("constitution_lint: PASS")
        else:
            print("constitution_lint: FAIL")
            for err in report["errors"]:
                print(f"- {err}")

    raise SystemExit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
