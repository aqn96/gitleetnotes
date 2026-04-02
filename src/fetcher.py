"""
Fetches accepted LeetCode submissions and problem details via GraphQL.
Uses session cookie auth — no official API key needed.
"""

import html as html_lib
import re
import requests
from datetime import datetime, timezone

LC_GRAPHQL = "https://leetcode.com/graphql"


def _headers(session: str, csrf: str) -> dict:
    return {
        "Content-Type": "application/json",
        "Cookie": f"LEETCODE_SESSION={session}; csrftoken={csrf}",
        "X-CSRFToken": csrf,
        "Referer": "https://leetcode.com",
        "Origin": "https://leetcode.com",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }


def fetch_username(session: str, csrf: str) -> str | None:
    query = """
    query globalData {
        userStatus {
            username
        }
    }
    """
    try:
        resp = requests.post(
            LC_GRAPHQL,
            json={"query": query},
            headers=_headers(session, csrf),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"]["userStatus"]["username"]
    except Exception as e:
        print(f"ERROR fetching username: {e}")
        return None


def fetch_recent_accepted(session: str, csrf: str, username: str, limit: int = 20) -> list[dict]:
    """Returns a list of recently accepted submissions."""
    query = """
    query recentAcSubmissions($username: String!, $limit: Int!) {
        recentAcSubmissionList(username: $username, limit: $limit) {
            id
            title
            titleSlug
            timestamp
            lang
        }
    }
    """
    try:
        resp = requests.post(
            LC_GRAPHQL,
            json={"query": query, "variables": {"username": username, "limit": limit}},
            headers=_headers(session, csrf),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"]["recentAcSubmissionList"] or []
    except Exception as e:
        print(f"ERROR fetching submissions: {e}")
        return []


def fetch_submission_code(session: str, csrf: str, submission_id: str) -> str | None:
    """Fetches the actual code for a specific submission."""
    query = """
    query submissionDetails($submissionId: Int!) {
        submissionDetails(submissionId: $submissionId) {
            code
            lang { name }
        }
    }
    """
    try:
        resp = requests.post(
            LC_GRAPHQL,
            json={"query": query, "variables": {"submissionId": int(submission_id)}},
            headers=_headers(session, csrf),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        details = data["data"]["submissionDetails"]
        return details["code"] if details else None
    except Exception as e:
        print(f"ERROR fetching code for submission {submission_id}: {e}")
        return None


def fetch_problem_details(session: str, csrf: str, slug: str) -> dict | None:
    """Fetches problem difficulty, tags, and description."""
    query = """
    query questionData($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionId
            title
            difficulty
            topicTags { name slug }
            content
        }
    }
    """
    try:
        resp = requests.post(
            LC_GRAPHQL,
            json={"query": query, "variables": {"titleSlug": slug}},
            headers=_headers(session, csrf),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"]["question"]
    except Exception as e:
        print(f"ERROR fetching problem details for {slug}: {e}")
        return None


def fetch_editorial_analysis(session: str, csrf: str, slug: str) -> dict | None:
    """
    Fetches the official editorial for a problem (requires LeetCode Premium).
    Returns {"time_complexity": ..., "space_complexity": ...} or None if
    unavailable (free tier, no editorial, or parse failure).
    """
    query = """
    query officialSolution($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            solution {
                canSeeDetail
                content
            }
        }
    }
    """
    try:
        resp = requests.post(
            LC_GRAPHQL,
            json={"query": query, "variables": {"titleSlug": slug}},
            headers=_headers(session, csrf),
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        solution = (data.get("data") or {}).get("question", {}).get("solution")
        if not solution or not solution.get("canSeeDetail"):
            return None
        content = solution.get("content", "")
        return _parse_complexity_from_editorial(content)
    except Exception:
        return None


def _parse_complexity_from_editorial(content: str) -> dict | None:
    """Extracts time/space complexity O(...) values from editorial HTML."""
    # Strip HTML tags and unescape entities
    text = re.sub(r"<[^>]+>", " ", content)
    text = html_lib.unescape(text)
    # Remove LaTeX math delimiters and common formatting noise
    text = re.sub(r"\$+", "", text)
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)  # \textit{...} -> ...

    time_match = re.search(
        r"[Tt]ime\s+[Cc]omplexity\s*:?\s*(O\([^)]+\))",
        text,
    )
    space_match = re.search(
        r"[Ss]pace\s+[Cc]omplexity\s*:?\s*(O\([^)]+\))",
        text,
    )

    if not time_match and not space_match:
        return None

    return {
        "time_complexity": time_match.group(1) if time_match else "See editorial",
        "space_complexity": space_match.group(1) if space_match else "See editorial",
    }


def timestamp_to_date(ts: str | int) -> str:
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
