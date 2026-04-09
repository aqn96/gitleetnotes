"""Tests for progress_tracker.py."""

import pytest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from progress_tracker import (
    load_progress,
    save_progress,
    record_solution,
    generate_readme,
    _progress_bar,
)


def _sample_progress():
    return {"solved": {}, "by_difficulty": {}, "by_pattern": {}}


def _add_solution(progress, sub_id="1", problem_id="1", title="Two Sum", slug="two-sum",
                  difficulty="Easy", pattern="Hash Map", solved_on="2024-01-01"):
    return record_solution(
        progress, sub_id, problem_id, title, slug, difficulty, pattern,
        f"solutions/hash_map/0001_{slug}.md", solved_on
    )


class TestLoadProgress:
    def test_returns_empty_structure_when_file_missing(self, tmp_path):
        result = load_progress(tmp_path / "nonexistent.json")
        assert "solved" in result
        assert "by_difficulty" in result
        assert "by_pattern" in result
        assert "seen_submission_ids" in result
        assert "seen_problem_keys" in result

    def test_loads_existing_file(self, tmp_path):
        data = {"solved": {"42": {"title": "Foo"}}, "by_difficulty": {}, "by_pattern": {}}
        p = tmp_path / "progress.json"
        p.write_text(json.dumps(data))
        result = load_progress(p)
        assert "42" in result["solved"]
        assert "42" in result["seen_submission_ids"]

    def test_backfills_seen_problem_keys_from_existing_solved(self, tmp_path):
        data = {
            "solved": {
                "42": {
                    "problem_id": "1",
                    "slug": "two-sum",
                    "title": "Two Sum",
                }
            },
            "by_difficulty": {},
            "by_pattern": {},
        }
        p = tmp_path / "progress.json"
        p.write_text(json.dumps(data))
        result = load_progress(p)
        assert "slug:two-sum" in result["seen_problem_keys"]


class TestSaveProgress:
    def test_writes_json_file(self, tmp_path):
        data = {"solved": {}, "by_difficulty": {"Easy": 1}, "by_pattern": {}}
        p = tmp_path / "progress.json"
        save_progress(data, p)
        loaded = json.loads(p.read_text())
        assert loaded["by_difficulty"]["Easy"] == 1


class TestRecordSolution:
    def test_returns_true_for_new_solution(self):
        progress = _sample_progress()
        result = _add_solution(progress)
        assert result is True

    def test_returns_false_for_duplicate(self):
        progress = _sample_progress()
        _add_solution(progress, sub_id="1")
        result = _add_solution(progress, sub_id="1")
        assert result is False

    def test_increments_difficulty_count(self):
        progress = _sample_progress()
        _add_solution(progress, sub_id="1", problem_id="1", slug="two-sum", difficulty="Easy")
        _add_solution(progress, sub_id="2", problem_id="2", slug="add-two-numbers", difficulty="Easy")
        assert progress["by_difficulty"]["Easy"] == 2

    def test_increments_pattern_count(self):
        progress = _sample_progress()
        _add_solution(progress, sub_id="1", problem_id="1", slug="two-sum", pattern="Hash Map")
        _add_solution(progress, sub_id="2", problem_id="2", slug="add-two-numbers", pattern="Hash Map")
        assert progress["by_pattern"]["Hash Map"] == 2

    def test_stores_solution_metadata(self):
        progress = _sample_progress()
        _add_solution(progress, sub_id="99", title="Median of Two Sorted Arrays", difficulty="Hard")
        assert progress["solved"]["99"]["title"] == "Median of Two Sorted Arrays"
        assert progress["solved"]["99"]["difficulty"] == "Hard"

    def test_different_sub_ids_both_recorded(self):
        progress = _sample_progress()
        _add_solution(progress, sub_id="1", problem_id="1", title="Two Sum", slug="two-sum")
        _add_solution(progress, sub_id="2", problem_id="2", title="Add Two Numbers", slug="add-two-numbers")
        assert len(progress["solved"]) == 2

    def test_returns_false_for_same_problem_with_new_submission(self):
        progress = _sample_progress()
        _add_solution(progress, sub_id="1", problem_id="1", slug="two-sum")
        result = _add_solution(progress, sub_id="2", problem_id="1", slug="two-sum")
        assert result is False

    def test_updates_seen_sets_when_new_solution_added(self):
        progress = _sample_progress()
        _add_solution(progress, sub_id="9", problem_id="9", slug="palindrome-number")
        assert "9" in progress["seen_submission_ids"]
        assert "slug:palindrome-number" in progress["seen_problem_keys"]


class TestGenerateReadme:
    def test_contains_total_count(self):
        progress = _sample_progress()
        _add_solution(progress, sub_id="1", problem_id="1", slug="two-sum", difficulty="Easy")
        _add_solution(progress, sub_id="2", problem_id="2", slug="add-two-numbers", difficulty="Medium")
        readme = generate_readme(progress)
        assert "Total: 2 problems solved" in readme

    def test_contains_pattern_name(self):
        progress = _sample_progress()
        _add_solution(progress, sub_id="1", pattern="Hash Map")
        readme = generate_readme(progress)
        assert "Hash Map" in readme

    def test_contains_recent_solution_title(self):
        progress = _sample_progress()
        _add_solution(progress, sub_id="1", title="Two Sum")
        readme = generate_readme(progress)
        assert "Two Sum" in readme

    def test_empty_progress_renders_without_error(self):
        progress = _sample_progress()
        readme = generate_readme(progress)
        assert "Total: 0 problems solved" in readme

    def test_contains_last_updated(self):
        progress = _sample_progress()
        readme = generate_readme(progress)
        assert "Last updated:" in readme

    def test_shows_all_three_difficulties(self):
        progress = _sample_progress()
        readme = generate_readme(progress)
        assert "Easy" in readme
        assert "Medium" in readme
        assert "Hard" in readme


class TestProgressBar:
    def test_full_bar_when_count_equals_total(self):
        bar = _progress_bar(20, 20)
        assert "░" not in bar

    def test_empty_bar_when_count_is_zero(self):
        bar = _progress_bar(0, 20)
        assert "█" not in bar

    def test_handles_zero_total_without_error(self):
        bar = _progress_bar(0, 0)
        assert len(bar) == 20

    def test_bar_length_is_always_width(self):
        for count in [0, 5, 10, 15, 20]:
            bar = _progress_bar(count, 20, width=20)
            assert len(bar) == 20
