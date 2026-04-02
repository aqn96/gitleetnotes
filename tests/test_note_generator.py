"""Tests for note_generator.py — file I/O uses tmp_path fixture."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from note_generator import generate_note, save_note, LANG_SLUG_MAP

ANALYSIS = {
    "pattern": "Hash Map",
    "time_complexity": "O(n)",
    "space_complexity": "O(n)",
    "key_insight": "Use a hash map to track complements.",
    "review_tip": "Remember complement check.",
}

CODE = "def twoSum(nums, target): pass"


class TestGenerateNote:
    def test_contains_title(self):
        note = generate_note("1", "Two Sum", "two-sum", "Easy", ["Array"], "python3", CODE, ANALYSIS, "2024-01-01")
        assert "Two Sum" in note

    def test_contains_complexity(self):
        note = generate_note("1", "Two Sum", "two-sum", "Easy", ["Array"], "python3", CODE, ANALYSIS, "2024-01-01")
        assert "O(n)" in note

    def test_contains_pattern(self):
        note = generate_note("1", "Two Sum", "two-sum", "Easy", ["Array"], "python3", CODE, ANALYSIS, "2024-01-01")
        assert "Hash Map" in note

    def test_contains_code(self):
        note = generate_note("1", "Two Sum", "two-sum", "Easy", ["Array"], "python3", CODE, ANALYSIS, "2024-01-01")
        assert CODE in note

    def test_contains_solved_date(self):
        note = generate_note("1", "Two Sum", "two-sum", "Easy", ["Array"], "python3", CODE, ANALYSIS, "2024-01-15")
        assert "2024-01-15" in note

    def test_empty_tags_shows_none(self):
        note = generate_note("1", "Two Sum", "two-sum", "Easy", [], "python3", CODE, ANALYSIS, "2024-01-01")
        assert "None" in note

    def test_multiple_tags_joined(self):
        note = generate_note("1", "Two Sum", "two-sum", "Easy", ["Array", "Hash Table"], "python3", CODE, ANALYSIS, "2024-01-01")
        assert "Array, Hash Table" in note

    def test_uses_correct_lang_slug_for_code_fence(self):
        note = generate_note("1", "Two Sum", "two-sum", "Easy", [], "python3", CODE, ANALYSIS, "2024-01-01")
        assert "```python" in note

    def test_unknown_lang_uses_raw_lang(self):
        note = generate_note("1", "Two Sum", "two-sum", "Easy", [], "scala", CODE, ANALYSIS, "2024-01-01")
        assert "```scala" in note


class TestSaveNote:
    def test_creates_file(self, tmp_path):
        path = save_note(tmp_path, "Hash Map", "1", "two-sum", "# content")
        assert path.exists()

    def test_file_content_matches(self, tmp_path):
        path = save_note(tmp_path, "Hash Map", "1", "two-sum", "# content here")
        assert path.read_text() == "# content here"

    def test_filename_zero_pads_problem_id(self, tmp_path):
        path = save_note(tmp_path, "Hash Map", "1", "two-sum", "content")
        assert path.name == "0001_two-sum.md"

    def test_pattern_becomes_directory(self, tmp_path):
        path = save_note(tmp_path, "Hash Map", "1", "two-sum", "content")
        assert path.parent.name == "hash_map"

    def test_creates_nested_dirs(self, tmp_path):
        path = save_note(tmp_path, "Dynamic Programming", "42", "climbing-stairs", "content")
        assert (tmp_path / "dynamic_programming").is_dir()

    def test_spaces_in_pattern_become_underscores(self, tmp_path):
        path = save_note(tmp_path, "Two Pointers", "11", "container-with-most-water", "content")
        assert "two_pointers" in str(path)


class TestLangSlugMap:
    def test_python3_maps_to_python(self):
        assert LANG_SLUG_MAP["python3"] == "python"

    def test_cpp_maps_correctly(self):
        assert LANG_SLUG_MAP["cpp"] == "cpp"
