"""
Generates per-problem markdown study notes.
Each note is saved to solutions/<pattern>/<problem_id>_<slug>.md
"""

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

## Key Insight

{key_insight}

## Review Tip

> {review_tip}

## Solution

```{lang_slug}
{code}
```
"""

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
) -> str:
    """Returns the full markdown string for a problem note."""
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
