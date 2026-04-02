#!/usr/bin/env python3
"""
GitLeetNotes setup script.

Usage:
    pip install -r requirements-setup.txt

    # First-time setup — creates repo, extracts cookies, sets secrets
    python setup.py

    # Refresh expired LeetCode cookies on an existing repo
    python setup.py --refresh

Requirements: gh CLI (authenticated), Python 3.10+, playwright
"""

import argparse
import subprocess
import sys
import getpass
import tempfile
import time
from pathlib import Path

RUNNER_REPO = "aqn96/gitleetnotes"
DEFAULT_REPO_NAME = "leetcode-notes"
LEETCODE_LOGIN_URL = "https://leetcode.com/accounts/login/"
GEMINI_KEY_URL = "https://aistudio.google.com/app/apikey"

# Minimal files written into the user's new notes repo
_SYNC_YML = f"""\
name: Sync LeetCode Solutions

on:
  schedule:
    - cron: "0 9 * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  sync:
    uses: {RUNNER_REPO}/.github/workflows/sync-runner.yml@main
    secrets:
      LEETCODE_SESSION: ${{{{ secrets.LEETCODE_SESSION }}}}
      LEETCODE_CSRF: ${{{{ secrets.LEETCODE_CSRF }}}}
      GEMINI_API_KEY: ${{{{ secrets.GEMINI_API_KEY }}}}
"""

_README = """\
# My LeetCode Study Notes

> Powered by [GitLeetNotes](https://github.com/aqn96/gitleetnotes).

This README will be replaced with your live progress dashboard after the first sync.

Go to **Actions → Sync LeetCode Solutions → Run workflow** to trigger it now.
"""

_GITIGNORE = """\
_runner/
__pycache__/
*.pyc
"""


# ─── Helpers ──────────────────────────────────────────────────────────────────

def run(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=capture, text=True, check=True)


def print_step(n: int, msg: str) -> None:
    print(f"\n\033[1m[{n}/5] {msg}\033[0m")


def print_ok(msg: str) -> None:
    print(f"  \033[32m✓\033[0m {msg}")


def print_info(msg: str) -> None:
    print(f"  \033[34m→\033[0m {msg}")


def print_error(msg: str) -> None:
    print(f"  \033[31m✗\033[0m {msg}")


# ─── Step 1: Check GitHub CLI ─────────────────────────────────────────────────

def check_gh_auth() -> str:
    """Returns the authenticated GitHub username or exits."""
    print_step(1, "Checking GitHub CLI authentication")
    try:
        result = run(["gh", "auth", "status"], capture=True)
        output = result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        output = (e.stdout or "") + (e.stderr or "")

    # Extract username from output
    for line in output.splitlines():
        if "Logged in to github.com account" in line:
            username = line.split("account")[-1].strip().split()[0]
            print_ok(f"Logged in as: {username}")
            return username

    print_error("Not logged in to GitHub CLI. Run: gh auth login")
    sys.exit(1)


# ─── Step 2: Create repo from template ────────────────────────────────────────

def repo_exists(full_name: str) -> bool:
    """Returns True if the repo already exists on GitHub."""
    try:
        run(["gh", "repo", "view", full_name], capture=True)
        return True
    except subprocess.CalledProcessError:
        return False


def scaffold_repo(full_name: str) -> None:
    """
    Pushes the minimal notes-repo skeleton (workflow + placeholder README)
    into the freshly created empty GitHub repo.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Wire up git in the temp dir
        run(["git", "-C", tmpdir, "init", "-b", "main"], capture=True)
        run(["git", "-C", tmpdir, "remote", "add", "origin",
             f"https://github.com/{full_name}.git"], capture=True)

        # Write skeleton files
        wf_dir = tmp / ".github" / "workflows"
        wf_dir.mkdir(parents=True)
        (wf_dir / "sync.yml").write_text(_SYNC_YML)
        (tmp / "README.md").write_text(_README)
        (tmp / ".gitignore").write_text(_GITIGNORE)

        # Commit and push
        run(["git", "-C", tmpdir, "add", "-A"], capture=True)
        run(["git", "-C", tmpdir, "commit", "-m",
             "chore: initialize GitLeetNotes"], capture=True)
        run(["git", "-C", tmpdir, "push", "-u", "origin", "main"],
            capture=True)


def create_repo(username: str) -> str:
    """
    Prompts for a repo name. If it already exists, asks the user whether to
    continue (which will update secrets) or abort. If it doesn't exist,
    creates an empty public repo and scaffolds it with minimal files.
    Returns the full repo identifier (owner/name).
    """
    print_step(2, "Creating your notes repo")

    name = input(f"  Repo name [{DEFAULT_REPO_NAME}]: ").strip() or DEFAULT_REPO_NAME
    full_name = f"{username}/{name}"

    if repo_exists(full_name):
        print_info(f"Repo {full_name} already exists.")
        print()
        print("  What would you like to do?")
        print("    [1] Keep it — just refresh secrets (default)")
        print("    [2] Delete and recreate — fresh start, all notes will be lost")
        print("    [3] Abort")
        choice = input("  Choice [1]: ").strip() or "1"

        if choice == "3":
            print_info("Aborted.")
            sys.exit(0)
        elif choice == "2":
            print_info(f"Deleting {full_name} ...")
            try:
                run(["gh", "repo", "delete", full_name, "--yes"], capture=True)
                print_ok("Deleted.")
            except subprocess.CalledProcessError as e:
                err = e.stderr or ""
                if "delete_repo" in err:
                    print_error("Missing 'delete_repo' permission. Run:")
                    print_info("  gh auth refresh -h github.com -s delete_repo")
                    print_info("Then re-run setup.py.")
                else:
                    print_error(f"Could not delete repo: {err or e}")
                sys.exit(1)
            # Fall through to create a fresh one below
        else:
            print_ok(f"Using existing repo: https://github.com/{full_name}")
            return full_name

    print_info(f"Creating {full_name} ...")
    try:
        run(["gh", "repo", "create", name, "--public"], capture=True)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create repo: {e.stderr or e}")
        sys.exit(1)

    print_info("Pushing initial files...")
    try:
        scaffold_repo(full_name)
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to push initial files: {e.stderr or e}")
        sys.exit(1)

    print_ok(f"Repo ready: https://github.com/{full_name}")
    return full_name


# ─── Step 3: Extract LeetCode cookies via Playwright ─────────────────────────

def get_leetcode_cookies() -> tuple[str, str]:
    """
    Opens a visible browser window, waits for the user to log in to LeetCode,
    then automatically extracts LEETCODE_SESSION and csrftoken.
    Returns (session, csrf).
    """
    print_step(3, "Extracting LeetCode session cookies")
    print_info("A browser window will open. Log in to LeetCode, then come back here.")
    print_info("The script will detect your login automatically.")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print_error("playwright not installed. Run: pip install -r requirements-setup.txt")
        sys.exit(1)

    # Install browser binaries if not already present — safe to run multiple times.
    # Don't capture output so download progress is visible (first run is ~130 MB).
    print_info("Ensuring Playwright browser is installed (first run downloads ~130 MB)...")
    try:
        run(["playwright", "install", "chromium"])
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install Playwright browser: {e}")
        sys.exit(1)

    session = None
    csrf = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context()
        page = context.new_page()

        page.goto(LEETCODE_LOGIN_URL)
        page.bring_to_front()

        print_info("Waiting for login (up to 3 minutes) — check your browser window...")

        # Poll for the LEETCODE_SESSION cookie rather than watching URLs.
        # URL-based detection breaks with Google/GitHub OAuth redirects.
        deadline = time.time() + 180
        while time.time() < deadline:
            cookies = context.cookies()
            for c in cookies:
                if c["name"] == "LEETCODE_SESSION":
                    session = c["value"]
                elif c["name"] == "csrftoken":
                    csrf = c["value"]
            if session and csrf:
                break
            page.wait_for_timeout(1500)

        browser.close()

    if not session or not csrf:
        print_error("Could not find LeetCode session cookies after login.")
        print_info("Try logging in again and make sure you land on the LeetCode homepage.")
        sys.exit(1)

    print_ok("LEETCODE_SESSION extracted")
    print_ok("csrftoken extracted")
    return session, csrf


# ─── Step 4: Prompt for Gemini API key ────────────────────────────────────────

def get_gemini_key() -> str:
    print_step(4, "Gemini API key")
    print_info(f"Get a free key at: {GEMINI_KEY_URL}")
    key = getpass.getpass("  Paste your Gemini API key (hidden): ").strip()
    if not key:
        print_error("Gemini API key cannot be empty.")
        sys.exit(1)
    print_ok("Key received")
    return key


# ─── Step 5: Set secrets + trigger workflow ───────────────────────────────────

def configure_repo(repo: str, session: str, csrf: str, gemini_key: str) -> None:
    print_step(5, "Configuring repo secrets and triggering first run")

    secrets = {
        "LEETCODE_SESSION": session,
        "LEETCODE_CSRF": csrf,
        "GEMINI_API_KEY": gemini_key,
    }

    for name, value in secrets.items():
        run(["gh", "secret", "set", name, "--body", value, "--repo", repo])
        print_ok(f"Secret set: {name}")

    # Trigger the workflow — retry a few times in case GitHub is still
    # indexing a freshly created repo.
    print_info("Triggering first workflow run...")
    triggered = False
    for attempt in range(1, 4):
        try:
            run(["gh", "workflow", "run", "sync.yml", "--repo", repo])
            triggered = True
            break
        except subprocess.CalledProcessError:
            if attempt < 3:
                print_info(f"  Not ready yet, retrying in 5 s... ({attempt}/3)")
                time.sleep(5)

    if triggered:
        print_ok("Workflow triggered — check progress at:")
        print_info(f"  https://github.com/{repo}/actions")
    else:
        print_info("Could not trigger automatically — trigger it manually:")
        print_info(f"  https://github.com/{repo}/actions")


def refresh_cookies(repo: str) -> None:
    """Re-extracts LeetCode cookies and updates secrets on an existing repo."""
    print("\033[1mGitLeetNotes — Refresh Cookies\033[0m")
    print("─" * 40)
    print_info(f"Refreshing cookies for repo: {repo}")

    session, csrf = get_leetcode_cookies()

    run(["gh", "secret", "set", "LEETCODE_SESSION", "--body", session, "--repo", repo])
    print_ok("Secret updated: LEETCODE_SESSION")

    run(["gh", "secret", "set", "LEETCODE_CSRF", "--body", csrf, "--repo", repo])
    print_ok("Secret updated: LEETCODE_CSRF")

    print(f"\n\033[1m\033[32mDone!\033[0m Cookies refreshed for {repo}.")
    print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="GitLeetNotes setup and maintenance tool."
    )
    parser.add_argument(
        "--refresh",
        metavar="OWNER/REPO",
        help="Refresh expired LeetCode cookies on an existing repo (e.g. octocat/leetcode-notes)",
    )
    args = parser.parse_args()

    if args.refresh:
        check_gh_auth()
        refresh_cookies(args.refresh)
        return

    print("\033[1mGitLeetNotes Setup\033[0m")
    print("─" * 40)

    username = check_gh_auth()
    repo = create_repo(username)
    session, csrf = get_leetcode_cookies()
    gemini_key = get_gemini_key()
    configure_repo(repo, session, csrf, gemini_key)

    print(f"\n\033[1m\033[32mAll done!\033[0m")
    print(f"  Your repo:  https://github.com/{repo}")
    print(f"  Actions:    https://github.com/{repo}/actions")
    print(f"\n  To refresh cookies later:")
    print(f"    python setup.py --refresh {repo}")
    print()


if __name__ == "__main__":
    main()
