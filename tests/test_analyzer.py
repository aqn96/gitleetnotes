"""Tests for analyzer.py — Gemini API calls are mocked."""

import pytest
from unittest.mock import patch, MagicMock
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analyzer import analyze_solution, infer_pattern_from_tags, _fallback

API_KEY = "fake_gemini_key"
SAMPLE_CODE = "def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i"

SAMPLE_ANALYSIS = {
    "pattern": "Hash Map",
    "time_complexity": "O(n)",
    "space_complexity": "O(n)",
    "key_insight": "Use a hash map to track complements in one pass.",
    "review_tip": "Remember the complement check: target - current number.",
}


def _mock_gemini_response(content: str) -> MagicMock:
    mock = MagicMock()
    mock.status_code = 200
    mock.raise_for_status = MagicMock()
    mock.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": content}]}}]
    }
    return mock


class TestAnalyzeSolution:
    @patch("analyzer.requests.post")
    def test_returns_structured_analysis(self, mock_post):
        mock_post.return_value = _mock_gemini_response(json.dumps(SAMPLE_ANALYSIS))
        result = analyze_solution("Two Sum", "Easy", "python3", SAMPLE_CODE, API_KEY)
        assert result["pattern"] == "Hash Map"
        assert result["time_complexity"] == "O(n)"
        assert result["space_complexity"] == "O(n)"
        assert "key_insight" in result
        assert "review_tip" in result

    @patch("analyzer.requests.post")
    def test_strips_markdown_fences(self, mock_post):
        wrapped = f"```json\n{json.dumps(SAMPLE_ANALYSIS)}\n```"
        mock_post.return_value = _mock_gemini_response(wrapped)
        result = analyze_solution("Two Sum", "Easy", "python3", SAMPLE_CODE, API_KEY)
        assert result["pattern"] == "Hash Map"

    @patch("analyzer.requests.post")
    def test_falls_back_on_invalid_json(self, mock_post):
        mock_post.return_value = _mock_gemini_response("not valid json at all")
        result = analyze_solution("Two Sum", "Easy", "python3", SAMPLE_CODE, API_KEY)
        assert result == _fallback()

    @patch("analyzer.requests.post")
    def test_falls_back_on_network_error(self, mock_post):
        mock_post.side_effect = Exception("connection refused")
        result = analyze_solution("Two Sum", "Easy", "python3", SAMPLE_CODE, API_KEY)
        assert result == _fallback()

    @patch("analyzer.requests.post")
    def test_api_key_in_url(self, mock_post):
        mock_post.return_value = _mock_gemini_response(json.dumps(SAMPLE_ANALYSIS))
        analyze_solution("Two Sum", "Easy", "python3", SAMPLE_CODE, API_KEY)
        call_url = mock_post.call_args.args[0]
        assert "fake_gemini_key" in call_url

    def test_fallback_has_all_keys(self):
        fb = _fallback()
        for key in ["pattern", "time_complexity", "space_complexity", "key_insight", "review_tip"]:
            assert key in fb

    @patch("analyzer.requests.post")
    def test_prefill_overrides_fallback_on_error(self, mock_post):
        mock_post.side_effect = Exception("429 rate limit")
        prefill = {"pattern": "Hash Map", "time_complexity": "O(n)", "space_complexity": "O(n)"}
        result = analyze_solution("Two Sum", "Easy", "python3", SAMPLE_CODE, API_KEY, prefill=prefill)
        assert result["pattern"] == "Hash Map"
        assert result["time_complexity"] == "O(n)"
        assert result["space_complexity"] == "O(n)"
        # Gemini-only fields remain as fallback text
        assert result["key_insight"] == "Analysis unavailable."

    @patch("analyzer.requests.post")
    def test_prefill_not_used_when_gemini_succeeds(self, mock_post):
        mock_post.return_value = _mock_gemini_response(json.dumps(SAMPLE_ANALYSIS))
        prefill = {"pattern": "Array"}  # tag-inferred, should be overridden
        result = analyze_solution("Two Sum", "Easy", "python3", SAMPLE_CODE, API_KEY, prefill=prefill)
        assert result["pattern"] == "Hash Map"  # Gemini wins


class TestInferPatternFromTags:
    def test_maps_hash_table_to_hash_map(self):
        assert infer_pattern_from_tags(["Hash Table"]) == "Hash Map"

    def test_maps_breadth_first_search_to_bfs(self):
        assert infer_pattern_from_tags(["Breadth-First Search"]) == "BFS"

    def test_returns_first_match(self):
        # Array comes before Two Pointers in the input
        result = infer_pattern_from_tags(["Array", "Two Pointers"])
        assert result == "Array"

    def test_returns_none_for_unknown_tags(self):
        assert infer_pattern_from_tags(["Database", "Shell"]) is None

    def test_case_insensitive(self):
        assert infer_pattern_from_tags(["DYNAMIC PROGRAMMING"]) == "Dynamic Programming"

    def test_empty_list_returns_none(self):
        assert infer_pattern_from_tags([]) is None
