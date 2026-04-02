# GitLeetNotes

![Tests](https://github.com/aqn96/gitleetnotes/actions/workflows/test.yml/badge.svg)

> Your LeetCode grind, auto-documented. Every accepted solution becomes a structured study note — pattern, complexity, and key insight included.

---

## The problem with grinding LeetCode

Most people solve 200 problems and still blank on the approach two weeks later. That's not a volume problem — it's a retention problem.

The standard workflow is: solve a problem, move on. Maybe the code ends up in a GitHub repo somewhere. But raw code files don't help you study. They don't tell you *why* a two-pointer approach works here, or *what* to remember before you see this pattern in an interview.

**GitLeetNotes turns your repo into a study guide that builds itself.**

Every time you solve a problem, a GitHub Action fetches your solution, sends it to Gemini AI (free tier) for analysis, and commits a clean study note — organized by pattern, with time/space complexity and the key insight written out. Your README becomes a live progress dashboard showing coverage by pattern and difficulty.

No browser extension. No manual steps. It just runs in the background and accumulates knowledge.

---

## What you get

Every accepted solution automatically becomes a note:

```markdown
# 1. Two Sum

| Field             | Value          |
|---|---|
| Difficulty        | Easy           |
| Pattern           | Hash Map       |
| Time Complexity   | O(n)           |
| Space Complexity  | O(n)           |
| Solved On         | 2024-03-15     |

## Key Insight
Use a hash map to store complements in a single pass — no nested loop needed.

## Review Tip
> Remember: check `target - current` in the map before inserting.
```

And your repo's README becomes a live dashboard:

```
| Difficulty | Solved |
|---|---|
| Easy       | 42     |
| Medium     | 31     |
| Hard       | 8      |

Total: 81 problems solved

| Pattern              | Count | Progress             |
|---|---|---|
| Hash Map             | 18    | ████████████░░░░░░░░ |
| Dynamic Programming  | 12    | ████████░░░░░░░░░░░░ |
| Two Pointers         | 9     | ██████░░░░░░░░░░░░░░ |
```

Before an interview you don't re-solve 50 problems — you open your repo and see exactly where your gaps are.

---

## How it works

1. A GitHub Action runs **daily at 9 AM UTC** (or on demand)
2. Fetches your recent accepted submissions from LeetCode
3. Calls **Gemini 2.0 Flash** (free tier) to identify the algorithmic pattern, complexity, and a key insight
4. Commits a markdown note to `solutions/<pattern>/` and regenerates your README dashboard
5. Everything runs inside your own GitHub repo — no external servers, no accounts to manage

**Total cost: $0.** Gemini free tier handles ~1,500 requests/day, well above any daily solving pace.

---

## Setup

Two commands. That's it.

```bash
pip install -r requirements-setup.txt
python setup.py
```

The setup script handles everything automatically:

1. **Creates your repo** from this template via GitHub CLI — no clicking
2. **Opens a browser window** for LeetCode login — you log in once, the script extracts your session cookies automatically (Playwright watches for the login event and pulls the cookies without you touching DevTools)
3. **Prompts for your Gemini API key** — one paste ([get a free key here](https://aistudio.google.com/app/apikey), no billing required)
4. **Sets all three secrets** on your new repo via GitHub CLI
5. **Triggers your first sync** immediately

> **Prerequisite:** [GitHub CLI](https://cli.github.com/) installed and authenticated (`gh auth login`). Python 3.10+.

After setup, the Action runs automatically every day at 9 AM UTC. Session cookies expire every few weeks — when the Action starts failing, refresh them with one command:

```bash
python setup.py --refresh YOUR_USERNAME/YOUR_REPO_NAME
```

This opens a browser, re-extracts your cookies, and updates the repo secrets. Nothing else changes.

### Manual setup (if you prefer)

<details>
<summary>Expand for step-by-step instructions</summary>

1. Click **"Use this template"** → **"Create a new repository"** on GitHub. Make it **public**.
2. Log in to [leetcode.com](https://leetcode.com), open DevTools → Application → Cookies, and copy `LEETCODE_SESSION` and `csrftoken`.
3. Get a free Gemini API key at [Google AI Studio](https://aistudio.google.com/app/apikey).
4. Go to your repo → **Settings → Secrets and variables → Actions** and add:

| Secret name | Value |
|---|---|
| `LEETCODE_SESSION` | Your LeetCode session cookie |
| `LEETCODE_CSRF` | Your LeetCode csrftoken cookie |
| `GEMINI_API_KEY` | Your Gemini API key |

5. Go to **Actions → Sync LeetCode Solutions → Run workflow**.

</details>

---

## Project structure

```
your-repo/
├── .github/
│   └── workflows/
│       └── sync.yml              # Daily cron Action
├── solutions/
│   ├── hash_map/
│   │   └── 0001_two-sum.md
│   ├── dynamic_programming/
│   │   └── 0070_climbing-stairs.md
│   └── ...
├── src/
│   ├── main.py                   # Action entry point
│   ├── fetcher.py                # LeetCode GraphQL client
│   ├── analyzer.py               # Gemini analysis
│   ├── note_generator.py         # Markdown note builder
│   └── progress_tracker.py       # Progress state + README generator
├── tests/                        # pytest suite (55 tests)
├── progress.json                 # Auto-managed, do not edit manually
├── README.md                     # Auto-generated dashboard
└── requirements.txt
```

---

## Running locally

```bash
# Create a virtual environment
python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Configure secrets
cp .env.example .env
# Edit .env with your actual values

# Run sync
export $(cat .env | xargs)
python src/main.py

# Run tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Limitations

- **LeetCode's API is unofficial.** There is no public LeetCode API — this tool uses the same GraphQL endpoint their website uses. It has been stable for years but could break if LeetCode changes their frontend. Session cookies also expire every few weeks.
- **Gemini free tier is per-project.** The 1,500 requests/day limit is shared across all your Gemini usage. At one problem per day, you'll use ~30 requests/month — well within limits.
- **Fetches the 20 most recent accepted submissions per run.** If you solve more than 20 problems in one day, trigger the Action manually to catch up.

---

## Contributing

Issues and PRs are welcome. See the [issues](../../issues) tab.

---

## License

MIT — use it, fork it, improve it.
