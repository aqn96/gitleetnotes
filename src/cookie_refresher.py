#!/usr/bin/env python3
"""
Headless LeetCode login — extracts fresh session cookies and updates
the repo's LEETCODE_SESSION and LEETCODE_CSRF secrets via GitHub CLI.

Used by the auto-refresh workflow in the user's notes repo.

Required env vars:
  LEETCODE_EMAIL    — LeetCode account email
  LEETCODE_PASSWORD — LeetCode account password
  GH_PAT            — GitHub PAT with Secrets: write for the repo
  REPO              — GitHub repo in owner/name format
"""

import os
import subprocess
import sys
import time

LEETCODE_LOGIN_URL = "https://leetcode.com/accounts/login/"


def headless_login(email: str, password: str, headless: bool = True) -> tuple[str, str]:
    """
    Logs into LeetCode and returns (LEETCODE_SESSION, csrftoken).
    Use headless=False for local runs to bypass bot detection.
    Raises RuntimeError if login fails.
    """
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    except ImportError:
        raise RuntimeError(
            "playwright not installed — run: pip install playwright && playwright install chromium"
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        print("  Loading LeetCode login page...")
        page.goto(LEETCODE_LOGIN_URL, wait_until="domcontentloaded", timeout=30000)

        # Wait for password field — most reliable indicator the form is ready
        try:
            page.wait_for_selector('input[type="password"]', timeout=15000)
        except PlaywrightTimeout:
            browser.close()
            raise RuntimeError(
                "Login form not found. LeetCode may have changed their page structure."
            )

        # Fill email/username
        for selector in ['input[name="login"]', 'input[autocomplete="username"]', 'input[type="text"]']:
            try:
                page.fill(selector, email, timeout=3000)
                break
            except Exception:
                continue

        page.wait_for_timeout(500)

        # Fill password
        page.fill('input[type="password"]', password)

        page.wait_for_timeout(500)

        # Submit — press Enter on the password field (works regardless of button markup)
        page.press('input[type="password"]', 'Enter')

        # Poll for LEETCODE_SESSION cookie — up to 30 seconds
        print("  Waiting for login to complete...")
        deadline = time.time() + 30
        while time.time() < deadline:
            cookies = context.cookies()
            session = next((c["value"] for c in cookies if c["name"] == "LEETCODE_SESSION"), None)
            csrf = next((c["value"] for c in cookies if c["name"] == "csrftoken"), None)
            if session and csrf:
                browser.close()
                return session, csrf
            page.wait_for_timeout(1000)

        browser.close()
        raise RuntimeError(
            "Login timed out — credentials may be wrong, or LeetCode showed a CAPTCHA.\n"
            "Run `python setup.py --refresh <repo>` to log in manually instead."
        )


def refresh_cookies() -> None:
    email = os.environ.get("LEETCODE_EMAIL", "").strip()
    password = os.environ.get("LEETCODE_PASSWORD", "").strip()
    pat = os.environ.get("GH_PAT", "").strip()
    repo = os.environ.get("REPO", "").strip()

    if not all([email, password, pat, repo]):
        print("ERROR: LEETCODE_EMAIL, LEETCODE_PASSWORD, GH_PAT, and REPO must all be set.")
        sys.exit(1)

    print("Refreshing LeetCode cookies...")
    try:
        session, csrf = headless_login(email, password)
    except RuntimeError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print("  Login successful. Updating GitHub secrets...")
    gh_env = os.environ.copy()
    gh_env["GH_TOKEN"] = pat

    subprocess.run(
        ["gh", "secret", "set", "LEETCODE_SESSION", "--body", session, "--repo", repo],
        env=gh_env, check=True
    )
    subprocess.run(
        ["gh", "secret", "set", "LEETCODE_CSRF", "--body", csrf, "--repo", repo],
        env=gh_env, check=True
    )

    print("  ✓ LEETCODE_SESSION updated")
    print("  ✓ LEETCODE_CSRF updated")
    print("Done — cookies will stay fresh for another few weeks.")


if __name__ == "__main__":
    refresh_cookies()
