"""Tests for fetcher.py — all HTTP calls are mocked."""

import pytest
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fetcher import (
    fetch_username,
    fetch_recent_accepted,
    fetch_submission_code,
    fetch_problem_details,
    fetch_editorial_analysis,
    _parse_complexity_from_editorial,
    timestamp_to_date,
)


SESSION = "fake_session"
CSRF = "fake_csrf"


def _mock_response(json_data: dict, status: int = 200) -> MagicMock:
    mock = MagicMock()
    mock.status_code = status
    mock.json.return_value = json_data
    mock.raise_for_status = MagicMock()
    return mock


class TestFetchUsername:
    @patch("fetcher.requests.post")
    def test_returns_username_on_success(self, mock_post):
        mock_post.return_value = _mock_response(
            {"data": {"userStatus": {"username": "testuser"}}}
        )
        result = fetch_username(SESSION, CSRF)
        assert result == "testuser"

    @patch("fetcher.requests.post")
    def test_returns_none_on_network_error(self, mock_post):
        mock_post.side_effect = Exception("timeout")
        result = fetch_username(SESSION, CSRF)
        assert result is None

    @patch("fetcher.requests.post")
    def test_sends_correct_cookies(self, mock_post):
        mock_post.return_value = _mock_response(
            {"data": {"userStatus": {"username": "testuser"}}}
        )
        fetch_username(SESSION, CSRF)
        call_kwargs = mock_post.call_args
        headers = call_kwargs.kwargs["headers"]
        assert "LEETCODE_SESSION=fake_session" in headers["Cookie"]
        assert "csrftoken=fake_csrf" in headers["Cookie"]


class TestFetchRecentAccepted:
    @patch("fetcher.requests.post")
    def test_returns_list_on_success(self, mock_post):
        mock_post.return_value = _mock_response({
            "data": {
                "recentAcSubmissionList": [
                    {"id": "1", "title": "Two Sum", "titleSlug": "two-sum", "timestamp": "1700000000", "lang": "python3"}
                ]
            }
        })
        result = fetch_recent_accepted(SESSION, CSRF, "testuser", limit=1)
        assert len(result) == 1
        assert result[0]["title"] == "Two Sum"

    @patch("fetcher.requests.post")
    def test_returns_empty_list_on_error(self, mock_post):
        mock_post.side_effect = Exception("network error")
        result = fetch_recent_accepted(SESSION, CSRF, "testuser")
        assert result == []

    @patch("fetcher.requests.post")
    def test_returns_empty_list_when_none_in_response(self, mock_post):
        mock_post.return_value = _mock_response(
            {"data": {"recentAcSubmissionList": None}}
        )
        result = fetch_recent_accepted(SESSION, CSRF, "testuser")
        assert result == []


class TestFetchSubmissionCode:
    @patch("fetcher.requests.post")
    def test_returns_code_on_success(self, mock_post):
        mock_post.return_value = _mock_response({
            "data": {
                "submissionDetails": {
                    "code": "def twoSum(nums, target): pass",
                    "lang": {"name": "python3"},
                }
            }
        })
        result = fetch_submission_code(SESSION, CSRF, "123")
        assert result == "def twoSum(nums, target): pass"

    @patch("fetcher.requests.post")
    def test_returns_none_when_details_missing(self, mock_post):
        mock_post.return_value = _mock_response(
            {"data": {"submissionDetails": None}}
        )
        result = fetch_submission_code(SESSION, CSRF, "123")
        assert result is None

    @patch("fetcher.requests.post")
    def test_returns_none_on_error(self, mock_post):
        mock_post.side_effect = Exception("timeout")
        result = fetch_submission_code(SESSION, CSRF, "123")
        assert result is None


class TestFetchProblemDetails:
    @patch("fetcher.requests.post")
    def test_returns_details_on_success(self, mock_post):
        mock_post.return_value = _mock_response({
            "data": {
                "question": {
                    "questionId": "1",
                    "title": "Two Sum",
                    "difficulty": "Easy",
                    "topicTags": [{"name": "Array", "slug": "array"}],
                    "content": "<p>Given an array...</p>",
                }
            }
        })
        result = fetch_problem_details(SESSION, CSRF, "two-sum")
        assert result["questionId"] == "1"
        assert result["difficulty"] == "Easy"
        assert result["topicTags"][0]["name"] == "Array"

    @patch("fetcher.requests.post")
    def test_returns_none_on_error(self, mock_post):
        mock_post.side_effect = Exception("network error")
        result = fetch_problem_details(SESSION, CSRF, "two-sum")
        assert result is None


class TestParseComplexityFromEditorial:
    def test_extracts_time_and_space(self):
        html = "<p>Time complexity: O(n log n)</p><p>Space complexity: O(n)</p>"
        result = _parse_complexity_from_editorial(html)
        assert result == {"time_complexity": "O(n log n)", "space_complexity": "O(n)"}

    def test_strips_html_tags(self):
        html = "<li><b>Time complexity:</b> O(1)</li><li><b>Space complexity:</b> O(1)</li>"
        result = _parse_complexity_from_editorial(html)
        assert result["time_complexity"] == "O(1)"
        assert result["space_complexity"] == "O(1)"

    def test_returns_none_when_no_complexity_found(self):
        result = _parse_complexity_from_editorial("<p>This problem is easy.</p>")
        assert result is None

    def test_handles_latex_dollar_signs(self):
        html = "<p>Time complexity: $O(n^2)$</p><p>Space complexity: $O(1)$</p>"
        result = _parse_complexity_from_editorial(html)
        assert result["time_complexity"] == "O(n^2)"
        assert result["space_complexity"] == "O(1)"

    def test_case_insensitive(self):
        html = "<p>time complexity: O(n)</p><p>space complexity: O(n)</p>"
        result = _parse_complexity_from_editorial(html)
        assert result is not None
        assert result["time_complexity"] == "O(n)"


class TestFetchEditorialAnalysis:
    @patch("fetcher.requests.post")
    def test_returns_complexity_when_premium(self, mock_post):
        mock_post.return_value = _mock_response({
            "data": {
                "question": {
                    "solution": {
                        "canSeeDetail": True,
                        "content": "<p>Time complexity: O(n)</p><p>Space complexity: O(1)</p>",
                    }
                }
            }
        })
        result = fetch_editorial_analysis(SESSION, CSRF, "two-sum")
        assert result == {"time_complexity": "O(n)", "space_complexity": "O(1)"}

    @patch("fetcher.requests.post")
    def test_returns_none_when_cannot_see_detail(self, mock_post):
        mock_post.return_value = _mock_response({
            "data": {
                "question": {
                    "solution": {"canSeeDetail": False, "content": ""}
                }
            }
        })
        result = fetch_editorial_analysis(SESSION, CSRF, "two-sum")
        assert result is None

    @patch("fetcher.requests.post")
    def test_returns_none_when_no_solution(self, mock_post):
        mock_post.return_value = _mock_response({
            "data": {"question": {"solution": None}}
        })
        result = fetch_editorial_analysis(SESSION, CSRF, "two-sum")
        assert result is None

    @patch("fetcher.requests.post")
    def test_returns_none_on_error(self, mock_post):
        mock_post.side_effect = Exception("network error")
        result = fetch_editorial_analysis(SESSION, CSRF, "two-sum")
        assert result is None


class TestTimestampToDate:
    def test_converts_unix_timestamp(self):
        # 2023-11-14 22:13:20 UTC
        result = timestamp_to_date("1700000000")
        assert result == "2023-11-14"

    def test_accepts_int(self):
        result = timestamp_to_date(1700000000)
        assert result == "2023-11-14"
