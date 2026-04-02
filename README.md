# GitLeetNotes

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

### 1. Use this repo as a template

Click **"Use this template"** → **"Create a new repository"** on GitHub.

Make it **public** so GitHub Actions minutes are free (2,000 min/month on free tier).

### 2. Get your LeetCode session cookies

1. Log in to [leetcode.com](https://leetcode.com)
2. Open DevTools → Application → Cookies → `https://leetcode.com`
3. Copy the values for `LEETCODE_SESSION` and `csrftoken`

> Session cookies expire every few weeks. When the Action starts failing with auth errors, just refresh these secrets.

### 3. Get a free Gemini API key

Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a key — it's free, no billing required.

### 4. Add secrets to your repo

**Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `LEETCODE_SESSION` | Your LeetCode session cookie |
| `LEETCODE_CSRF` | Your LeetCode csrftoken cookie |
| `GEMINI_API_KEY` | Your Gemini API key |

### 5. Trigger your first run

Go to **Actions → Sync LeetCode Solutions → Run workflow**.

After that, it runs automatically every day.

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
