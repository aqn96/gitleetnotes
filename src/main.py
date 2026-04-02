"""
Entry point for the GitHub Action.
Orchestrates: fetch → analyze → generate note → update progress → write README.
"""

import os
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent))

from fetcher import (
    fetch_username,
    fetch_recent_accepted,
    fetch_submission_code,
    fetch_problem_details,
    timestamp_to_date,
)
from analyzer import analyze_solution
from note_generator import generate_note, save_note
from progress_tracker import (
    load_progress,
    save_progress,
    record_solution,
    generate_readme,
)

SOLUTIONS_DIR = Path("solutions")
README_PATH = Path("README.md")
PROGRESS_PATH = Path("progress.json")


def run() -> int:
    """Returns the number of new solutions processed."""
    lc_session = os.environ.get("LEETCODE_SESSION", "").strip()
    lc_csrf = os.environ.get("LEETCODE_CSRF", "").strip()
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not lc_session or not lc_csrf:
        print("ERROR: LEETCODE_SESSION and LEETCODE_CSRF must be set.")
        sys.exit(1)
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY must be set.")
        sys.exit(1)

    print("Fetching LeetCode username...")
    username = fetch_username(lc_session, lc_csrf)
    if not username:
        print("ERROR: Could not authenticate with LeetCode.")
        sys.exit(1)
    print(f"Logged in as: {username}")

    progress = load_progress(PROGRESS_PATH)
    already_seen = set(progress.get("solved", {}).keys())

    print("Fetching recent accepted submissions...")
    submissions = fetch_recent_accepted(lc_session, lc_csrf, username, limit=20)
    new_count = 0

    for sub in submissions:
        sub_id = str(sub["id"])
        if sub_id in already_seen:
            print(f"  skip (already recorded): {sub['title']}")
            continue

        print(f"  processing: {sub['title']} [{sub['lang']}]")

        code = fetch_submission_code(lc_session, lc_csrf, sub_id)
        if not code:
            print(f"  WARN: could not fetch code for submission {sub_id}, skipping.")
            continue

        details = fetch_problem_details(lc_session, lc_csrf, sub["titleSlug"])
        if not details:
            print(f"  WARN: could not fetch problem details for {sub['titleSlug']}, skipping.")
            continue

        problem_id = details["questionId"]
        difficulty = details.get("difficulty", "Unknown")
        tags = [t["name"] for t in details.get("topicTags", [])]
        solved_on = timestamp_to_date(sub["timestamp"])

        print(f"    analyzing with Gemini...")
        analysis = analyze_solution(
            title=sub["title"],
            difficulty=difficulty,
            lang=sub["lang"],
            code=code,
            api_key=gemini_key,
        )

        note_content = generate_note(
            problem_id=problem_id,
            title=sub["title"],
            slug=sub["titleSlug"],
            difficulty=difficulty,
            tags=tags,
            lang=sub["lang"],
            code=code,
            analysis=analysis,
            solved_on=solved_on,
        )

        note_path = save_note(
            solutions_dir=SOLUTIONS_DIR,
            pattern=analysis["pattern"],
            problem_id=problem_id,
            slug=sub["titleSlug"],
            content=note_content,
        )

        is_new = record_solution(
            progress=progress,
            submission_id=sub_id,
            problem_id=problem_id,
            title=sub["title"],
            slug=sub["titleSlug"],
            difficulty=difficulty,
            pattern=analysis["pattern"],
            note_path=str(note_path),
            solved_on=solved_on,
        )

        if is_new:
            new_count += 1
            print(f"    saved: {note_path}")

    save_progress(progress, PROGRESS_PATH)

    readme_content = generate_readme(progress)
    README_PATH.write_text(readme_content, encoding="utf-8")
    print(f"\nDone. {new_count} new solution(s) added.")
    return new_count


if __name__ == "__main__":
    run()
