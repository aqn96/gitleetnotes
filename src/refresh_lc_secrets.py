#!/usr/bin/env python3
"""Refresh LeetCode cookies in GitHub Actions secrets from local browser cookies."""

from __future__ import annotations

import argparse
import subprocess
import sys

import browser_cookie3


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def get_leetcode_cookies() -> tuple[str, str]:
    loaders = [
        ("Chrome", browser_cookie3.chrome),
        ("Chromium", browser_cookie3.chromium),
        ("Brave", browser_cookie3.brave),
        ("Edge", browser_cookie3.edge),
    ]
    errors: list[str] = []

    for browser_name, loader in loaders:
        try:
            cookie_jar = loader(domain_name="leetcode.com")
        except Exception as exc:
            errors.append(f"{browser_name}: {exc}")
            continue

        values = {c.name: c.value for c in cookie_jar if c.name in {"LEETCODE_SESSION", "csrftoken"}}
        session = values.get("LEETCODE_SESSION")
        csrf = values.get("csrftoken")
        if session and csrf:
            return session, csrf

    print("Could not find LeetCode cookies in local browser profiles.")
    if errors:
        print("Browser read attempts:")
        for err in errors:
            print(f"  - {err}")
    return "", ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh LeetCode Actions secrets from local browser cookies.")
    parser.add_argument("repo", help="GitHub repo in OWNER/REPO form")
    parser.add_argument("--workflow", default="sync.yml", help="Workflow file name to trigger (default: sync.yml)")
    args = parser.parse_args()

    session, csrf = get_leetcode_cookies()
    if not session or not csrf:
        print("Log into leetcode.com in Chrome/Chromium/Brave/Edge first, then retry.")
        return 1

    run(["gh", "secret", "set", "LEETCODE_SESSION", "--repo", args.repo, "--body", session])
    run(["gh", "secret", "set", "LEETCODE_CSRF", "--repo", args.repo, "--body", csrf])
    run(["gh", "workflow", "run", args.workflow, "--repo", args.repo])
    print("Done: secrets refreshed + workflow triggered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
