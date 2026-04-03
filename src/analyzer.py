"""
Uses GitHub Models (gpt-4o-mini, free for all GitHub users) to analyze a LeetCode solution.
Returns structured data: pattern, time complexity, space complexity, explanation.

Authentication uses the GITHUB_TOKEN automatically provided by GitHub Actions —
no separate API key required.

Tag-based pattern inference and editorial complexity are used as free fallbacks
when the model call fails (rate-limited, quota exhausted, etc.).
"""

import json
import re
import time
from openai import OpenAI

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


# GitHub Models free tier (gpt-4o-mini): 20 requests/minute.
# One call per ~3s keeps us safely under.
_RATE_LIMIT_DELAY = 3  # seconds between calls

GITHUB_MODELS_BASE_URL = "https://models.inference.ai.azure.com"
GITHUB_MODELS_MODEL = "gpt-4o-mini"

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
    Calls GitHub Models (gpt-4o-mini) and returns a structured analysis dict.
    api_key should be the GITHUB_TOKEN from the Actions environment.
    If prefill is provided (e.g. pattern from tags, complexity from editorial),
    those values override fallback placeholders when the model call fails.
    """
    prompt = PROMPT_TEMPLATE.format(
        title=title, difficulty=difficulty, lang=lang, code=code
    )

    try:
        time.sleep(_RATE_LIMIT_DELAY)
        client = OpenAI(
            base_url=GITHUB_MODELS_BASE_URL,
            api_key=api_key,
        )
        response = client.chat.completions.create(
            model=GITHUB_MODELS_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        text = response.choices[0].message.content.strip()

        # Strip accidental markdown fences
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"WARN: Model returned non-JSON for '{title}': {e}")
    except Exception as e:
        print(f"WARN: GitHub Models analysis failed for '{title}': {e}")

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
