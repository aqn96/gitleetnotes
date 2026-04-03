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
    fetch_editorial_analysis,
    timestamp_to_date,
)
from analyzer import analyze_solution, infer_pattern_from_tags
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
    github_token = os.environ.get("GITHUB_TOKEN", "").strip()

    if not lc_session or not lc_csrf:
        print("ERROR: LEETCODE_SESSION and LEETCODE_CSRF must be set.")
        sys.exit(1)
    if not github_token:
        print("ERROR: GITHUB_TOKEN must be set.")
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

        # Build a prefill dict from free sources so model failure still
        # produces a useful note (pattern from tags, complexity from editorial).
        prefill: dict = {}
        inferred = infer_pattern_from_tags(tags)
        if inferred:
            prefill["pattern"] = inferred
        editorial = fetch_editorial_analysis(lc_session, lc_csrf, sub["titleSlug"])
        if editorial:
            prefill.update(editorial)

        print(f"    analyzing with GitHub Models...")
        analysis = analyze_solution(
            title=sub["title"],
            difficulty=difficulty,
            lang=sub["lang"],
            code=code,
            api_key=github_token,
            prefill=prefill or None,
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
            lang=sub["lang"],
        )

        if is_new:
            new_count += 1
            print(f"    saved: {note_path}")

    # Re-analyze any notes that previously fell back to "Unknown" (e.g. rate limit hit)
    retry_count = _retry_unknown(progress, lc_session, lc_csrf, github_token)
    if retry_count:
        print(f"  Re-analyzed {retry_count} previously-unknown note(s).")

    save_progress(progress, PROGRESS_PATH)

    readme_content = generate_readme(progress)
    README_PATH.write_text(readme_content, encoding="utf-8")
    print(f"\nDone. {new_count} new, {retry_count} re-analyzed.")
    return new_count


def _retry_unknown(progress: dict, session: str, csrf: str, github_token: str) -> int:
    """
    Finds solved entries where pattern=='Unknown' (model failed on a previous run)
    and re-runs analysis. Updates the note file and progress entry in place.
    Returns the number of entries successfully re-analyzed.
    """
    unknowns = [
        (sub_id, entry)
        for sub_id, entry in progress.get("solved", {}).items()
        if entry.get("pattern") == "Unknown"
    ]
    if not unknowns:
        return 0

    print(f"Re-analyzing {len(unknowns)} note(s) with unknown pattern...")
    fixed = 0

    for sub_id, entry in unknowns:
        title = entry["title"]
        print(f"  re-analyzing: {title}")

        code = fetch_submission_code(session, csrf, sub_id)
        if not code:
            print(f"    WARN: could not fetch code, skipping.")
            continue

        details = fetch_problem_details(session, csrf, entry["slug"])
        if not details:
            print(f"    WARN: could not fetch problem details, skipping.")
            continue

        difficulty = details.get("difficulty", "Unknown")
        tags = [t["name"] for t in details.get("topicTags", [])]
        lang = entry.get("lang", "python3")

        prefill: dict = {}
        inferred = infer_pattern_from_tags(tags)
        if inferred:
            prefill["pattern"] = inferred
        editorial = fetch_editorial_analysis(session, csrf, entry["slug"])
        if editorial:
            prefill.update(editorial)

        analysis = analyze_solution(
            title=title,
            difficulty=difficulty,
            lang=lang,
            code=code,
            api_key=github_token,
            prefill=prefill or None,
        )
        if analysis["pattern"] == "Unknown":
            print(f"    WARN: still unknown, skipping.")
            continue

        # Update the note file
        note_content = generate_note(
            problem_id=entry["problem_id"],
            title=title,
            slug=entry["slug"],
            difficulty=difficulty,
            tags=tags,
            lang=lang,
            code=code,
            analysis=analysis,
            solved_on=entry["solved_on"],
        )
        note_path = save_note(
            solutions_dir=SOLUTIONS_DIR,
            pattern=analysis["pattern"],
            problem_id=entry["problem_id"],
            slug=entry["slug"],
            content=note_content,
        )

        # Update progress entry
        old_pattern = entry["pattern"]
        entry["pattern"] = analysis["pattern"]
        entry["note_path"] = str(note_path)

        # Fix pattern counts
        progress["by_pattern"][old_pattern] = max(
            0, progress["by_pattern"].get(old_pattern, 1) - 1
        )
        progress["by_pattern"][analysis["pattern"]] = (
            progress["by_pattern"].get(analysis["pattern"], 0) + 1
        )

        fixed += 1
        print(f"    updated: {note_path}")

    return fixed


if __name__ == "__main__":
    run()
