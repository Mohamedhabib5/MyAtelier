import importlib.util
import json
from pathlib import Path


def _load_constitution_lint_module():
    project_root = Path(__file__).resolve().parent.parent
    module_path = project_root / "scripts" / "constitution_lint.py"
    spec = importlib.util.spec_from_file_location("constitution_lint", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_constitution_lint_passes_for_current_project():
    module = _load_constitution_lint_module()
    project_root = Path(__file__).resolve().parent.parent
    constitution_path = project_root / "codex_app_invariants_myatelier_full.json"

    report = module.run_lint(constitution_path, project_root)

    assert report["ok"], report


def test_success_feedback_invariants_use_global_toast():
    project_root = Path(__file__).resolve().parent.parent
    constitution_path = project_root / "codex_app_invariants_myatelier_full.json"

    data = json.loads(constitution_path.read_text(encoding="utf-8"))
    invariants = {inv["id"]: inv for inv in data.get("invariants", [])}

    for inv_id in ("INV-BOOK-004", "INV-PAY-003", "INV-DRESS-004", "INV-SVC-003"):
        inv = invariants[inv_id]
        success_block = inv["expected"]["if_success"]
        assert "success_toast" in success_block
        assert "app-success-toast" in success_block["success_toast"]
