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

class TestRepoExists:
    @patch("setup.run")
    def test_returns_true_when_repo_found(self, mock_run):
        mock_run.return_value = MagicMock()
        assert s.repo_exists("octocat/repo") is True

    @patch("setup.run")
    def test_returns_false_when_repo_not_found(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="")
        assert s.repo_exists("octocat/nonexistent") is False


class TestScaffoldRepo:
    @patch("setup.tempfile.TemporaryDirectory")
    @patch("setup.run")
    def test_creates_workflow_file(self, mock_run, mock_tmpdir, tmp_path):
        mock_tmpdir.return_value.__enter__ = lambda s: str(tmp_path)
        mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
        s.scaffold_repo("octocat/repo")
        wf = tmp_path / ".github" / "workflows" / "sync.yml"
        assert wf.exists()

    @patch("setup.tempfile.TemporaryDirectory")
    @patch("setup.run")
    def test_workflow_references_runner_repo(self, mock_run, mock_tmpdir, tmp_path):
        mock_tmpdir.return_value.__enter__ = lambda s: str(tmp_path)
        mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
        s.scaffold_repo("octocat/repo")
        content = (tmp_path / ".github" / "workflows" / "sync.yml").read_text()
        assert s.RUNNER_REPO in content
        assert "python _runner/src/main.py" in content

    @patch("setup.tempfile.TemporaryDirectory")
    @patch("setup.run")
    def test_creates_readme(self, mock_run, mock_tmpdir, tmp_path):
        mock_tmpdir.return_value.__enter__ = lambda s: str(tmp_path)
        mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
        s.scaffold_repo("octocat/repo")
        assert (tmp_path / "README.md").exists()

    @patch("setup.tempfile.TemporaryDirectory")
    @patch("setup.run")
    def test_pushes_to_correct_remote(self, mock_run, mock_tmpdir, tmp_path):
        mock_tmpdir.return_value.__enter__ = lambda s: str(tmp_path)
        mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)
        s.scaffold_repo("octocat/my-notes")
        all_cmds = [c.args[0] for c in mock_run.call_args_list]
        remote_cmd = next(c for c in all_cmds if "remote" in c and "add" in c)
        assert "https://github.com/octocat/my-notes.git" in remote_cmd


class TestCreateRepo:
    @patch("setup.repo_exists", return_value=False)
    @patch("setup.run")
    @patch("builtins.input", return_value="")
    def test_uses_default_name_on_empty_input(self, mock_input, mock_run, mock_exists):
        repo, is_new = s.create_repo("octocat")
        assert repo == f"octocat/{s.DEFAULT_REPO_NAME}"
        assert is_new is True

    @patch("setup.repo_exists", return_value=False)
    @patch("setup.run")
    @patch("builtins.input", return_value="my-leet-notes")
    def test_uses_provided_name(self, mock_input, mock_run, mock_exists):
        repo, _ = s.create_repo("octocat")
        assert repo == "octocat/my-leet-notes"

    @patch("setup.repo_exists", return_value=False)
    @patch("setup.run")
    @patch("builtins.input", return_value="")
    def test_calls_gh_repo_create(self, mock_input, mock_run, mock_exists):
        s.create_repo("octocat")
        args = mock_run.call_args.args[0]
        assert args[:3] == ["gh", "repo", "create"]
        assert "--public" in args
        assert "--template" not in args

    @patch("setup.repo_exists", return_value=False)
    @patch("setup.run")
    @patch("builtins.input", return_value="")
    def test_does_not_scaffold_on_create(self, mock_input, mock_run, mock_exists):
        # scaffold_repo is now called from main() after secrets are set, not here
        with patch("setup.scaffold_repo") as mock_scaffold:
            s.create_repo("octocat")
            mock_scaffold.assert_not_called()

    @patch("setup.repo_exists", return_value=False)
    @patch("setup.run")
    @patch("builtins.input", return_value="")
    def test_exits_on_create_error(self, mock_input, mock_run, mock_exists):
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="error")
        with pytest.raises(SystemExit):
            s.create_repo("octocat")

    @patch("setup.repo_exists", return_value=True)
    @patch("builtins.input", side_effect=["", "1"])
    def test_existing_repo_choice1_returns_is_new_false(self, mock_input, mock_exists):
        repo, is_new = s.create_repo("octocat")
        assert repo == f"octocat/{s.DEFAULT_REPO_NAME}"
        assert is_new is False

    @patch("setup.repo_exists", return_value=True)
    @patch("builtins.input", side_effect=["", ""])
    def test_existing_repo_empty_choice_keeps_it(self, mock_input, mock_exists):
        repo, is_new = s.create_repo("octocat")
        assert "octocat" in repo
        assert is_new is False

    @patch("setup.repo_exists", return_value=True)
    @patch("builtins.input", side_effect=["", "3"])
    def test_existing_repo_choice3_aborts(self, mock_input, mock_exists):
        with pytest.raises(SystemExit):
            s.create_repo("octocat")

    @patch("setup.run")
    @patch("setup.repo_exists", return_value=True)
    @patch("builtins.input", side_effect=["", "2"])
    def test_existing_repo_choice2_deletes_and_recreates(self, mock_input, mock_exists, mock_run):
        repo, is_new = s.create_repo("octocat")
        cmds = [c.args[0] for c in mock_run.call_args_list]
        assert any("delete" in cmd for cmd in cmds)
        assert any("create" in cmd for cmd in cmds)
        assert is_new is True

    @patch("setup.run")
    @patch("setup.repo_exists", return_value=True)
    @patch("builtins.input", side_effect=["", "2"])
    def test_delete_missing_scope_shows_helpful_error(self, mock_input, mock_exists, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="delete_repo scope required")
        with pytest.raises(SystemExit):
            s.create_repo("octocat")

    @patch("setup.repo_exists", return_value=True)
    @patch("builtins.input", side_effect=["", "1"])
    def test_existing_repo_keep_returns_is_new_false(self, mock_input, mock_exists):
        _, is_new = s.create_repo("octocat")
        assert is_new is False


# ─── configure_repo ───────────────────────────────────────────────────────────

class TestRefreshCookies:
    @patch("setup.get_leetcode_cookies", return_value=("new_session", "new_csrf"))
    @patch("setup.run")
    def test_updates_both_cookie_secrets(self, mock_run, mock_cookies):
        s.refresh_cookies("octocat/repo")
        calls = mock_run.call_args_list
        secret_names = [c.args[0][3] for c in calls]
        assert "LEETCODE_SESSION" in secret_names
        assert "LEETCODE_CSRF" in secret_names

    @patch("setup.get_leetcode_cookies", return_value=("new_session", "new_csrf"))
    @patch("setup.run")
    def test_passes_new_cookie_values(self, mock_run, mock_cookies):
        s.refresh_cookies("octocat/repo")
        calls = mock_run.call_args_list
        bodies = {c.args[0][3]: c.args[0][5] for c in calls if len(c.args[0]) > 5}
        assert bodies.get("LEETCODE_SESSION") == "new_session"
        assert bodies.get("LEETCODE_CSRF") == "new_csrf"


class TestConfigureRepo:
    @patch("setup.run")
    def test_sets_both_secrets(self, mock_run):
        s.configure_repo("octocat/repo", "sess123", "csrf456")
        calls = mock_run.call_args_list
        secret_names = [c.args[0][3] for c in calls if "secret" in c.args[0]]
        assert "LEETCODE_SESSION" in secret_names
        assert "LEETCODE_CSRF" in secret_names

    @patch("setup.run")
    def test_passes_correct_secret_values(self, mock_run):
        s.configure_repo("octocat/repo", "my_session", "my_csrf")
        calls = mock_run.call_args_list
        bodies = {
            c.args[0][3]: c.args[0][5]
            for c in calls
            if len(c.args[0]) > 5 and c.args[0][2] == "set"
        }
        assert bodies.get("LEETCODE_SESSION") == "my_session"
        assert bodies.get("LEETCODE_CSRF") == "my_csrf"

    @patch("setup.run")
    def test_handles_secret_failure_gracefully(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "gh", stderr="")
        with pytest.raises(subprocess.CalledProcessError):
            s.configure_repo("octocat/repo", "s", "c")
