# GitLeetNotes

![Tests](https://github.com/aqn96/gitleetnotes/actions/workflows/test.yml/badge.svg)

> Your LeetCode grind, auto-documented. Every newly solved problem becomes a structured study note — pattern, complexity, and key insight included.

---

## The problem with grinding LeetCode

Most people solve 200 problems and still blank on the approach two weeks later. That's not a volume problem — it's a retention problem.

The standard workflow is: solve a problem, move on. Maybe the code ends up in a GitHub repo somewhere. But raw code files don't help you study. They don't tell you *why* a two-pointer approach works here, or *what* to remember before you see this pattern in an interview.

**GitLeetNotes turns your repo into a study guide that builds itself.**

Every time you solve a problem, a GitHub Action fetches your solution, sends it to **GitHub Models (gpt-4o-mini)** for analysis, and commits a clean study note — organized by pattern, with time/space complexity and the key insight written out. Your README becomes a live progress dashboard showing coverage by pattern and difficulty.

No browser extension. No manual steps. No API keys to manage. It just runs in the background and accumulates knowledge.

---

## What you get

Every newly solved problem automatically becomes a note:

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
3. Keeps only unique problems (skips repeat accepted submissions of the same problem)
4. Calls **GitHub Models (gpt-4o-mini)** — free for all GitHub users, authenticated automatically via `GITHUB_TOKEN` — to identify the algorithmic pattern, complexity, and a key insight
5. Commits a markdown note to `solutions/<pattern>/` and regenerates your README dashboard
6. Everything runs inside your own GitHub repo — no external servers, no accounts to manage

**Total cost: $0.** GitHub Models is free for all GitHub users with no separate API key required.

---

## Setup

Clone this repo and run the setup script. It creates **your own personal repo** on your GitHub account and configures everything — you don't need to keep this clone afterwards.

```bash
git clone https://github.com/aqn96/gitleetnotes
cd gitleetnotes
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-setup.txt
python setup.py
```

The script walks you through:

1. **Creates your repo** — makes a new public repo (e.g. `your-username/leetcode-notes`) on your GitHub account from this template, via GitHub CLI
2. **Extracts your LeetCode cookies** — reads cookies from your existing logged-in browser profile (Chrome/Chromium/Brave/Edge). No Playwright login flow.
3. **Sets all secrets** on your new repo via GitHub CLI
4. **Triggers your first sync** — your repo gets its first notes within a minute

After that, your personal repo runs on its own every day. You can delete this local clone — everything lives in your new repo from here on.

> **Prerequisites:** [GitHub CLI](https://cli.github.com/) installed and authenticated (`gh auth login`). Python 3.10+.

**When cookies expire** (every few weeks), run this from the same clone:

```bash
python setup.py --refresh YOUR_USERNAME/YOUR_REPO_NAME
```

Reads local browser cookies and updates your repo secrets. Done in under a minute.

Or use the standalone helper:

```bash
python src/refresh_lc_secrets.py YOUR_USERNAME/YOUR_REPO_NAME
```

### Why Playwright was removed from setup

The previous setup flow opened a Playwright browser and waited for interactive login. In practice this was fragile due to anti-bot/CAPTCHA/OAuth interstitial behavior on LeetCode, which could leave login frozen or fail with target/page closed errors. Cookie extraction now uses your normal local browser profile instead, which is more reliable and avoids automated-login brittleness.

### Manual setup (if you prefer)

<details>
<summary>Expand for step-by-step instructions</summary>

1. Click **"Use this template"** → **"Create a new repository"** on GitHub. Make it **public**.
2. Log in to [leetcode.com](https://leetcode.com), open DevTools → Application → Cookies, and copy `LEETCODE_SESSION` and `csrftoken`.
3. Go to your repo → **Settings → Secrets and variables → Actions** and add:

| Secret name | Value |
|---|---|
| `LEETCODE_SESSION` | Your LeetCode session cookie |
| `LEETCODE_CSRF` | Your LeetCode csrftoken cookie |

4. Go to **Actions → Sync LeetCode Solutions → Run workflow**.

No API key needed — `GITHUB_TOKEN` is provided automatically by GitHub Actions.

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
│   ├── analyzer.py               # GitHub Models analysis
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
# GITHUB_TOKEN can be a Personal Access Token with no special scopes

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
- **GitHub Models free tier rate limits.** gpt-4o-mini allows 200 requests/day. At one problem per day, you'll use ~30 requests/month — well within limits. The sync throttles calls automatically.
- **Fetches the 20 most recent accepted submissions per run.** If you solve more than 20 problems in one day, trigger the Action manually to catch up.
- **Tracks unique problems, not submission attempts.** Re-accepted submissions of a problem you've already recorded are intentionally skipped.

---

## Contributing

Issues and PRs are welcome. See the [issues](../../issues) tab.

---

## License

MIT — use it, fork it, improve it.
