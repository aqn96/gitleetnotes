"""
Fetches accepted LeetCode submissions and problem details via GraphQL.
Uses session cookie auth — no official API key needed.
"""

import os
import requests
from datetime import datetime, timezone

LC_GRAPHQL = "https://leetcode.com/graphql"


def _headers(session: str, csrf: str) -> dict:
    return {
        "Content-Type": "application/json",
        "Cookie": f"LEETCODE_SESSION={session}; csrftoken={csrf}",
        "X-CSRFToken": csrf,
        "Referer": "https://leetcode.com",
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


def timestamp_to_date(ts: str | int) -> str:
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
