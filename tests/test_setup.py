"""Tests for setup.py — subprocess calls and browser are mocked."""

import pytest
import subprocess
import sys
from unittest.mock import patch, MagicMock, call
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import setup as s


# ─── check_gh_auth ────────────────────────────────────────────────────────────

class TestCheckGhAuth:
    @patch("setup.run")
    def test_returns_username_on_success(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="  ✓ Logged in to github.com account octocat (keyring)\n",
            stderr="",
        )
        result = s.check_gh_auth()
        assert result == "octocat"

    @patch("setup.run")
    def test_exits_when_not_logged_in(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "gh", stderr="You are not logged in"
        )
        with pytest.raises(SystemExit):
            s.check_gh_auth()

    @patch("setup.run")
    def test_exits_when_gh_not_installed(self, mock_run):
        mock_run.side_effect = FileNotFoundError("gh not found")
        with pytest.raises((SystemExit, FileNotFoundError)):
            s.check_gh_auth()


# ─── create_repo ──────────────────────────────────────────────────────────────

class TestCreateRepo:
    @patch("setup.run")
    @patch("builtins.input", return_value="")
    def test_uses_default_name_on_empty_input(self, mock_input, mock_run):
        result = s.create_repo("octocat")
        assert result == f"octocat/{s.DEFAULT_REPO_NAME}"

    @patch("setup.run")
    @patch("builtins.input", return_value="my-leet-notes")
    def test_uses_provided_name(self, mock_input, mock_run):
        result = s.create_repo("octocat")
        assert result == "octocat/my-leet-notes"

    @patch("setup.run")
    @patch("builtins.input", return_value="")
    def test_calls_gh_repo_create(self, mock_input, mock_run):
        s.create_repo("octocat")
        mock_run.assert_called_once()
        args = mock_run.call_args.args[0]
        assert "gh" in args
        assert "repo" in args
        assert "create" in args
        assert "--template" in args

    @patch("setup.run")
    @patch("builtins.input", return_value="")
    def test_continues_if_repo_already_exists(self, mock_input, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "gh", stderr="already exists"
        )
        # Should not raise
        result = s.create_repo("octocat")
        assert "octocat" in result

    @patch("setup.run")
    @patch("builtins.input", return_value="")
    def test_exits_on_unexpected_error(self, mock_input, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "gh", stderr="some unexpected error"
        )
        with pytest.raises(SystemExit):
            s.create_repo("octocat")


# ─── get_gemini_key ───────────────────────────────────────────────────────────

class TestGetGeminiKey:
    @patch("getpass.getpass", return_value="AIzaSy_fake_key_12345")
    def test_returns_key_on_valid_input(self, mock_getpass):
        result = s.get_gemini_key()
        assert result == "AIzaSy_fake_key_12345"

    @patch("getpass.getpass", return_value="")
    def test_exits_on_empty_key(self, mock_getpass):
        with pytest.raises(SystemExit):
            s.get_gemini_key()


# ─── configure_repo ───────────────────────────────────────────────────────────

class TestConfigureRepo:
    @patch("setup.run")
    def test_sets_all_three_secrets(self, mock_run):
        s.configure_repo("octocat/repo", "sess123", "csrf456", "gemini789")
        calls = mock_run.call_args_list
        secret_names = [c.args[0][3] for c in calls if "secret" in c.args[0]]
        assert "LEETCODE_SESSION" in secret_names
        assert "LEETCODE_CSRF" in secret_names
        assert "GEMINI_API_KEY" in secret_names

    @patch("setup.run")
    def test_triggers_workflow(self, mock_run):
        s.configure_repo("octocat/repo", "sess", "csrf", "key")
        calls = [c.args[0] for c in mock_run.call_args_list]
        assert any("workflow" in cmd and "run" in cmd for cmd in calls)

    @patch("setup.run")
    def test_passes_correct_secret_values(self, mock_run):
        s.configure_repo("octocat/repo", "my_session", "my_csrf", "my_gemini")
        calls = mock_run.call_args_list
        bodies = {
            c.args[0][3]: c.args[0][5]
            for c in calls
            if len(c.args[0]) > 5 and c.args[0][2] == "set"
        }
        assert bodies.get("LEETCODE_SESSION") == "my_session"
        assert bodies.get("LEETCODE_CSRF") == "my_csrf"
        assert bodies.get("GEMINI_API_KEY") == "my_gemini"

    @patch("setup.run")
    def test_handles_workflow_trigger_failure_gracefully(self, mock_run):
        # First 3 calls (secrets) succeed, 4th (workflow) fails
        mock_run.side_effect = [None, None, None,
                                subprocess.CalledProcessError(1, "gh", stderr="")]
        # Should not raise
        s.configure_repo("octocat/repo", "s", "c", "g")
