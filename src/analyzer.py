"""
Uses Gemini 2.0 Flash (free tier) to analyze a LeetCode solution.
Returns structured data: pattern, time complexity, space complexity, explanation.

Tag-based pattern inference and editorial complexity are used as free fallbacks
when Gemini is unavailable (rate-limited, quota exhausted, etc.).
"""

import json
import re
import time
import requests

# Maps LeetCode topic tag names (lowercase) to analysis pattern labels.
_TAG_TO_PATTERN = {
    "array": "Array",
    "two pointers": "Two Pointers",
    "sliding window": "Sliding Window",
    "binary search": "Binary Search",
    "hash table": "Hash Map",
    "stack": "Stack",
    "monotonic stack": "Stack",
    "queue": "Queue",
    "monotonic queue": "Queue",
    "linked list": "Linked List",
    "tree": "Tree",
    "binary tree": "Tree",
    "binary indexed tree": "Tree",
    "segment tree": "Tree",
    "graph": "Graph",
    "union find": "Graph",
    "topological sort": "Graph",
    "shortest path": "Graph",
    "breadth-first search": "BFS",
    "depth-first search": "DFS",
    "backtracking": "Backtracking",
    "dynamic programming": "Dynamic Programming",
    "greedy": "Greedy",
    "heap (priority queue)": "Heap",
    "trie": "Trie",
    "math": "Math",
    "string": "String",
    "bit manipulation": "Bit Manipulation",
    "divide and conquer": "Backtracking",
    "recursion": "DFS",
}


def infer_pattern_from_tags(tags: list[str]) -> str | None:
    """Returns the first matching pattern for a list of topic tag names, or None."""
    for tag in tags:
        pattern = _TAG_TO_PATTERN.get(tag.lower())
        if pattern:
            return pattern
    return None

# Gemini free tier: 15 requests/minute. One call per ~4s keeps us safely under.
_RATE_LIMIT_DELAY = 4  # seconds between calls

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)

PROMPT_TEMPLATE = """You are a senior software engineer reviewing a LeetCode solution.

Problem: {title} (Difficulty: {difficulty})
Language: {lang}

Code:
```
{code}
```

Respond in valid JSON only — no markdown fences, no extra text:
{{
  "pattern": "<one of: Array, Two Pointers, Sliding Window, Binary Search, Hash Map, Stack, Queue, Linked List, Tree, Graph, BFS, DFS, Backtracking, Dynamic Programming, Greedy, Heap, Trie, Math, String, Bit Manipulation>",
  "time_complexity": "<e.g. O(n log n)>",
  "space_complexity": "<e.g. O(n)>",
  "key_insight": "<1–2 sentences explaining the core idea>",
  "review_tip": "<1 sentence: what to remember before an interview>"
}}"""


def analyze_solution(
    title: str,
    difficulty: str,
    lang: str,
    code: str,
    api_key: str,
    prefill: dict | None = None,
) -> dict:
    """
    Calls Gemini and returns a structured analysis dict.
    If prefill is provided (e.g. pattern from tags, complexity from editorial),
    those values override fallback placeholders when Gemini fails.
    """
    prompt = PROMPT_TEMPLATE.format(
        title=title, difficulty=difficulty, lang=lang, code=code
    )

    try:
        time.sleep(_RATE_LIMIT_DELAY)
        resp = requests.post(
            f"{GEMINI_URL}?key={api_key}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30,
        )
        resp.raise_for_status()
        raw = resp.json()
        text = raw["candidates"][0]["content"]["parts"][0]["text"].strip()

        # Strip accidental markdown fences
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"WARN: Gemini returned non-JSON for '{title}': {e}")
    except Exception as e:
        print(f"WARN: Gemini analysis failed for '{title}': {e}")

    fallback = _fallback()
    if prefill:
        fallback.update(prefill)
    return fallback


def _fallback() -> dict:
    return {
        "pattern": "Unknown",
        "time_complexity": "Unknown",
        "space_complexity": "Unknown",
        "key_insight": "Analysis unavailable.",
        "review_tip": "Review this problem manually.",
    }
