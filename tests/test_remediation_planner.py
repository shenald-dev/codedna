"""Unit tests for Intelligent Remediation Planner.

Tests pattern detection, unified diff generation, dry-run, and autofix application.
"""

import json
from pathlib import Path

from codedna.remediation.planner import RemediationPlanner


def test_remediation_plan_bare_except(tmp_path: Path):
    py_file = tmp_path / "module.py"
    py_file.write_text("""
def calculate(val):
    try:
        return 100 / val
    except:
        return 0
""", encoding="utf-8")

    planner = RemediationPlanner(tmp_path)
    actions = planner.plan()

    assert len(actions) == 1
    act = actions[0]
    assert act.rule_id == "SMELL-BARE-EXCEPT"
    assert act.autofixable is True
    assert "except Exception:" in act.proposed_text
    assert "--- a/module.py" in act.unified_diff or "module.py" in act.unified_diff


def test_remediation_plan_secret_extraction(tmp_path: Path):
    py_file = tmp_path / "client.py"
    py_file.write_text("""
def connect():
    api_key = "dummy_mock_secret_token_1234567890abcdef"
    return api_key
""", encoding="utf-8")

    planner = RemediationPlanner(tmp_path)
    actions = planner.plan()

    assert any(a.rule_id == "SEC-HARDCODED-SECRET" for a in actions)
    sec_act = next(a for a in actions if a.rule_id == "SEC-HARDCODED-SECRET")
    assert sec_act.autofixable is True
    assert "os.getenv('API_KEY'" in sec_act.proposed_text


def test_remediation_plan_wildcard_pin(tmp_path: Path):
    pkg_file = tmp_path / "package.json"
    pkg_file.write_text(json.dumps({
        "dependencies": {
            "lodash": "*"
        }
    }), encoding="utf-8")

    planner = RemediationPlanner(tmp_path)
    actions = planner.plan()

    assert any(a.rule_id == "DEP-WILDCARD-PIN" for a in actions)
    pin_act = next(a for a in actions if a.rule_id == "DEP-WILDCARD-PIN")
    assert pin_act.autofixable is True
    assert '"^1.0.0"' in pin_act.proposed_text


def test_remediation_apply_dry_run_vs_live(tmp_path: Path):
    py_file = tmp_path / "worker.py"
    original_code = "try:\n    pass\nexcept:\n    pass\n"
    py_file.write_text(original_code, encoding="utf-8")

    planner = RemediationPlanner(tmp_path)
    actions = planner.plan()
    assert len(actions) == 1

    # 1. Dry run
    res_dry = planner.apply(actions, dry_run=True)
    assert res_dry["dry_run"] is True
    assert res_dry["applied_count"] == 1
    assert py_file.read_text(encoding="utf-8") == original_code  # File untouched

    # 2. Live apply
    res_live = planner.apply(actions, dry_run=False)
    assert res_live["dry_run"] is False
    assert res_live["applied_count"] == 1
    modified_code = py_file.read_text(encoding="utf-8")
    assert "except Exception:" in modified_code
    assert "except:" not in modified_code


def test_remediation_rule_filter(tmp_path: Path):
    py_file = tmp_path / "test.py"
    py_file.write_text("try:\n    pass\nexcept:\n    pass\napi_key = 'abcdef1234567890abcdef123456'\n", encoding="utf-8")

    planner = RemediationPlanner(tmp_path)
    # Filter only SMELL-BARE-EXCEPT
    actions = planner.plan(rule_filter=["SMELL-BARE-EXCEPT"])
    assert len(actions) == 1
    assert actions[0].rule_id == "SMELL-BARE-EXCEPT"
