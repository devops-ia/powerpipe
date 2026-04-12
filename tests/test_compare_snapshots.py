"""Unit tests for scripts/compare_snapshots.py — powerpipe fixtures."""

import json
import sys
from pathlib import Path

import pytest

from compare_snapshots import compare, diff_lists, render_markdown


# ---------------------------------------------------------------------------
# Fixtures — powerpipe-specific
# ---------------------------------------------------------------------------

@pytest.fixture
def powerpipe_snapshot_v1():
    return {
        "version": "1.5.1",
        "snapshot_date": "2026-01-01",
        "subcommands": ["benchmark", "completion", "mod", "server"],
        "server_flags": ["--help", "--listen", "--port"],
        "benchmark_run_flags": ["--dry-run", "--export", "--help", "--output"],
        "mod_flags": ["--help", "--pull"],
        "env_vars": [
            "POWERPIPE_LISTEN",
            "POWERPIPE_MOD_LOCATION",
            "POWERPIPE_PORT",
            "POWERPIPE_TELEMETRY",
            "POWERPIPE_UPDATE_CHECK",
        ],
        "help_text_hash": "pp_abc123",
        "server_help_hash": "pp_def456",
        "benchmark_help_hash": "pp_ghi789",
    }


@pytest.fixture
def powerpipe_snapshot_v2_no_changes(powerpipe_snapshot_v1):
    return {**powerpipe_snapshot_v1, "version": "1.6.0"}


@pytest.fixture
def powerpipe_snapshot_v2_with_changes():
    return {
        "version": "1.6.0",
        "snapshot_date": "2026-02-01",
        "subcommands": ["benchmark", "completion", "mod", "server", "variable"],
        "server_flags": ["--help", "--listen", "--port", "--workspace"],
        "benchmark_run_flags": ["--dry-run", "--export", "--help", "--output"],
        "mod_flags": ["--help"],
        "env_vars": [
            "POWERPIPE_LISTEN",
            "POWERPIPE_MOD_LOCATION",
            "POWERPIPE_NEW_VAR",
            "POWERPIPE_PORT",
            "POWERPIPE_UPDATE_CHECK",
        ],
        "help_text_hash": "pp_changed",
        "server_help_hash": "pp_def456",
        "benchmark_help_hash": "pp_ghi789",
    }


# ---------------------------------------------------------------------------
# diff_lists
# ---------------------------------------------------------------------------

class TestDiffLists:
    def test_added_items(self):
        d = diff_lists(["a", "b"], ["a", "b", "c"])
        assert d["added"] == ["c"]
        assert d["removed"] == []

    def test_removed_items(self):
        d = diff_lists(["a", "b", "c"], ["a", "b"])
        assert d["added"] == []
        assert d["removed"] == ["c"]

    def test_both_added_and_removed(self):
        d = diff_lists(["a", "b"], ["b", "c"])
        assert d["added"] == ["c"]
        assert d["removed"] == ["a"]

    def test_no_changes(self):
        d = diff_lists(["a", "b"], ["a", "b"])
        assert d["added"] == []
        assert d["removed"] == []

    def test_empty_lists(self):
        d = diff_lists([], [])
        assert d["added"] == []
        assert d["removed"] == []

    def test_result_is_sorted(self):
        d = diff_lists(["z", "a"], ["z", "b", "c"])
        assert d["added"] == ["b", "c"]
        assert d["removed"] == ["a"]


# ---------------------------------------------------------------------------
# compare — no changes
# ---------------------------------------------------------------------------

class TestCompareNoChanges:
    def test_identical_snapshots_has_no_changes(self, powerpipe_snapshot_v1):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v1)
        assert result["has_changes"] is False

    def test_version_label_only_has_no_changes(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_no_changes):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_no_changes)
        assert result["has_changes"] is False

    def test_version_change_is_reported(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_no_changes):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_no_changes)
        assert "1.5.1" in result["version_change"]
        assert "1.6.0" in result["version_change"]

    def test_no_hash_changes_when_identical(self, powerpipe_snapshot_v1):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v1)
        assert result["hash_changes"] == []


# ---------------------------------------------------------------------------
# compare — with behavioral changes
# ---------------------------------------------------------------------------

class TestCompareWithChanges:
    def test_has_changes_true(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes)
        assert result["has_changes"] is True

    def test_added_subcommand_detected(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes)
        assert "variable" in result["categories"]["subcommands"]["added"]

    def test_added_server_flag_detected(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes)
        assert "--workspace" in result["categories"]["server_flags"]["added"]

    def test_removed_mod_flag_detected(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes)
        assert "--pull" in result["categories"]["mod_flags"]["removed"]

    def test_added_env_var_detected(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes)
        assert "POWERPIPE_NEW_VAR" in result["categories"]["env_vars"]["added"]

    def test_removed_env_var_detected(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes)
        assert "POWERPIPE_TELEMETRY" in result["categories"]["env_vars"]["removed"]

    def test_hash_change_detected(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes)
        assert len(result["hash_changes"]) > 0


# ---------------------------------------------------------------------------
# compare — dynamic key detection
# ---------------------------------------------------------------------------

class TestCompareDynamicKeys:
    def test_powerpipe_specific_keys_detected(self, powerpipe_snapshot_v1):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v1)
        assert "server_flags" in result["categories"]
        assert "benchmark_run_flags" in result["categories"]
        assert "mod_flags" in result["categories"]

    def test_no_steampipe_keys_appear(self, powerpipe_snapshot_v1):
        result = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v1)
        assert "service_start_flags" not in result["categories"]
        assert "query_flags" not in result["categories"]

    def test_new_category_in_new_snapshot_detected(self, powerpipe_snapshot_v1):
        old = {**powerpipe_snapshot_v1}
        new = {**powerpipe_snapshot_v1, "pipeline_flags": ["--async", "--output"]}
        result = compare(old, new)
        assert "pipeline_flags" in result["categories"]
        assert result["categories"]["pipeline_flags"]["added"] == ["--async", "--output"]
        assert result["has_changes"] is True


# ---------------------------------------------------------------------------
# render_markdown
# ---------------------------------------------------------------------------

class TestRenderMarkdown:
    def test_no_changes_message(self, powerpipe_snapshot_v1):
        diff = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v1)
        md = render_markdown(diff)
        assert "No behavioral changes detected" in md
        assert "Action needed" not in md

    def test_changes_include_tables(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes):
        diff = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes)
        md = render_markdown(diff)
        assert "❌ Removed" in md
        assert "➕ Added" in md

    def test_changes_include_copilot_mention(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes):
        diff = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes)
        md = render_markdown(diff)
        assert "@copilot" in md

    def test_hash_change_section_present(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes):
        diff = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes)
        md = render_markdown(diff)
        assert "Help text changes" in md

    def test_version_in_header(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes):
        diff = compare(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes)
        md = render_markdown(diff)
        assert "1.5.1" in md
        assert "1.6.0" in md


# ---------------------------------------------------------------------------
# TestMain — in-process calls for coverage
# ---------------------------------------------------------------------------

class TestMain:
    def test_main_no_changes_exits_0(self, powerpipe_snapshot_v1, tmp_path, monkeypatch):
        import compare_snapshots as cs
        old_file = tmp_path / "old.json"
        new_file = tmp_path / "new.json"
        old_file.write_text(json.dumps(powerpipe_snapshot_v1))
        new_file.write_text(json.dumps(powerpipe_snapshot_v1))

        monkeypatch.setattr(sys, "argv", ["compare_snapshots.py", str(old_file), str(new_file)])
        with pytest.raises(SystemExit) as exc:
            cs.main()
        assert exc.value.code == 0

    def test_main_with_changes_exits_1(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes, tmp_path, monkeypatch):
        import compare_snapshots as cs
        old_file = tmp_path / "old.json"
        new_file = tmp_path / "new.json"
        old_file.write_text(json.dumps(powerpipe_snapshot_v1))
        new_file.write_text(json.dumps(powerpipe_snapshot_v2_with_changes))

        monkeypatch.setattr(sys, "argv", ["compare_snapshots.py", str(old_file), str(new_file)])
        with pytest.raises(SystemExit) as exc:
            cs.main()
        assert exc.value.code == 1

    def test_main_bad_json_exits_2(self, tmp_path, monkeypatch):
        import compare_snapshots as cs
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid {{{")
        good_file = tmp_path / "good.json"
        good_file.write_text("{}")

        monkeypatch.setattr(sys, "argv", ["compare_snapshots.py", str(bad_file), str(good_file)])
        with pytest.raises(SystemExit) as exc:
            cs.main()
        assert exc.value.code == 2

    def test_main_writes_output_files(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes, tmp_path, monkeypatch):
        import compare_snapshots as cs
        old_file = tmp_path / "old.json"
        new_file = tmp_path / "new.json"
        out_json = tmp_path / "diff.json"
        out_md = tmp_path / "diff.md"
        old_file.write_text(json.dumps(powerpipe_snapshot_v1))
        new_file.write_text(json.dumps(powerpipe_snapshot_v2_with_changes))

        monkeypatch.setattr(sys, "argv", [
            "compare_snapshots.py", str(old_file), str(new_file),
            "--output-json", str(out_json),
            "--output-md", str(out_md),
        ])
        with pytest.raises(SystemExit):
            cs.main()

        assert out_json.exists()
        assert out_md.exists()
        data = json.loads(out_json.read_text())
        assert data["has_changes"] is True
        assert "CLI Behavioral Changes" in out_md.read_text()


# ---------------------------------------------------------------------------
# CLI invocation via subprocess (exit codes)
# ---------------------------------------------------------------------------

class TestExitCodes:
    def _run(self, old_data, new_data, tmp_path):
        import subprocess
        old_file = tmp_path / "old.json"
        new_file = tmp_path / "new.json"
        old_file.write_text(json.dumps(old_data))
        new_file.write_text(json.dumps(new_data))
        script = Path(__file__).parent.parent / "scripts" / "compare_snapshots.py"
        return subprocess.run(
            [sys.executable, str(script), str(old_file), str(new_file)],
            capture_output=True,
        )

    def test_exit_0_when_no_changes(self, powerpipe_snapshot_v1, tmp_path):
        result = self._run(powerpipe_snapshot_v1, powerpipe_snapshot_v1, tmp_path)
        assert result.returncode == 0

    def test_exit_1_when_changes(self, powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes, tmp_path):
        result = self._run(powerpipe_snapshot_v1, powerpipe_snapshot_v2_with_changes, tmp_path)
        assert result.returncode == 1

    def test_exit_2_on_missing_file(self, tmp_path):
        import subprocess
        missing = tmp_path / "missing.json"
        good_file = tmp_path / "good.json"
        good_file.write_text("{}")
        script = Path(__file__).parent.parent / "scripts" / "compare_snapshots.py"
        result = subprocess.run(
            [sys.executable, str(script), str(missing), str(good_file)],
            capture_output=True,
        )
        assert result.returncode == 2
