"""
Generates per-problem markdown study notes.
Each note is saved to solutions/<pattern>/<problem_id>_<slug>.md
"""

import html as html_lib
import re
from pathlib import Path
from datetime import date

NOTE_TEMPLATE = """\
# {problem_id}. {title}

| Field | Value |
|---|---|
| **Difficulty** | {difficulty} |
| **Pattern** | {pattern} |
| **Time Complexity** | {time_complexity} |
| **Space Complexity** | {space_complexity} |
| **Language** | {lang} |
| **Solved On** | {solved_on} |
| **Tags** | {tags} |

## Problem

{problem_description}

## Key Insight

{key_insight}

## Review Tip

> {review_tip}

## Solution

```{lang_slug}
{code}
```
"""


def _html_to_text(html: str) -> str:
    """Converts LeetCode HTML problem description to readable plain text."""
    # Preserve code blocks with backticks
    html = re.sub(r"<pre[^>]*>(.*?)</pre>", lambda m: "\n```\n" + re.sub(r"<[^>]+>", "", m.group(1)).strip() + "\n```\n", html, flags=re.DOTALL)
    # Bold
    html = re.sub(r"<strong>(.*?)</strong>", r"**\1**", html, flags=re.DOTALL)
    html = re.sub(r"<b>(.*?)</b>", r"**\1**", html, flags=re.DOTALL)
    # Italic
    html = re.sub(r"<em>(.*?)</em>", r"*\1*", html, flags=re.DOTALL)
    # Inline code
    html = re.sub(r"<code>(.*?)</code>", r"`\1`", html, flags=re.DOTALL)
    # List items
    html = re.sub(r"<li>(.*?)</li>", r"- \1", html, flags=re.DOTALL)
    # Paragraphs and line breaks
    html = re.sub(r"</?p>|<br\s*/?>", "\n", html)
    # Strip remaining tags
    html = re.sub(r"<[^>]+>", "", html)
    # Unescape HTML entities
    html = html_lib.unescape(html)
    # Clean up whitespace
    html = re.sub(r"\n{3,}", "\n\n", html).strip()
    return html

LANG_SLUG_MAP = {
    "python3": "python",
    "python": "python",
    "java": "java",
    "cpp": "cpp",
    "c": "c",
    "javascript": "javascript",
    "typescript": "typescript",
    "go": "go",
    "rust": "rust",
    "kotlin": "kotlin",
    "swift": "swift",
}


def generate_note(
    problem_id: str,
    title: str,
    slug: str,
    difficulty: str,
    tags: list[str],
    lang: str,
    code: str,
    analysis: dict,
    solved_on: str,
    problem_description: str = "",
) -> str:
    """Returns the full markdown string for a problem note."""
    description_text = _html_to_text(problem_description) if problem_description else "*No description available.*"
    return NOTE_TEMPLATE.format(
        problem_id=problem_id,
        title=title,
        difficulty=difficulty,
        pattern=analysis["pattern"],
        time_complexity=analysis["time_complexity"],
        space_complexity=analysis["space_complexity"],
        lang=lang,
        solved_on=solved_on,
        tags=", ".join(tags) if tags else "None",
        key_insight=analysis["key_insight"],
        review_tip=analysis["review_tip"],
        lang_slug=LANG_SLUG_MAP.get(lang.lower(), lang.lower()),
        code=code,
        problem_description=description_text,
    )


def save_note(
    solutions_dir: Path,
    pattern: str,
    problem_id: str,
    slug: str,
    content: str,
) -> Path:
    """Writes the note to solutions/<pattern>/<id>_<slug>.md and returns the path."""
    safe_pattern = pattern.replace(" ", "_").lower()
    dest_dir = solutions_dir / safe_pattern
    dest_dir.mkdir(parents=True, exist_ok=True)

    file_path = dest_dir / f"{problem_id.zfill(4)}_{slug}.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path
