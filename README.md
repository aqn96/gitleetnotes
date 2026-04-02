# GitLeetNotes

> **"Get leet notes."** — Auto-generate structured study notes from your LeetCode solutions and track your progress on GitHub.

LeetHub pushes your code. **GitLeetNotes pushes your understanding.**

Every time you solve a LeetCode problem, a GitHub Action automatically fetches your solution, analyzes it with AI (Gemini free tier), and commits a clean study note to your repo — organized by pattern, complete with time/space complexity and a key insight to review before interviews.

---

## What You Get

Every accepted solution becomes a note like this:

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

Plus a live README dashboard that updates itself:

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

---

## How It Works

1. A GitHub Action runs **daily at 9 AM UTC**
2. Fetches your recent accepted submissions from LeetCode's GraphQL API
3. Calls **Gemini 2.0 Flash** (free tier) to identify the pattern, complexity, and generate an insight
4. Commits a markdown note to `solutions/<pattern>/` and updates your README dashboard
5. Everything runs in your own repo — no external servers, no paid subscriptions

**Total cost: $0.** Uses your free Gemini API quota (~30 requests/month for daily solving).

---

## Setup

### 1. Use this repo as a template

Click **"Use this template"** → **"Create a new repository"** on GitHub.

Make it **public** so GitHub Actions minutes are free.

### 2. Get your LeetCode session cookies

1. Log in to [leetcode.com](https://leetcode.com)
2. Open DevTools → Application → Cookies → `https://leetcode.com`
3. Copy the values for `LEETCODE_SESSION` and `csrftoken`

> These expire periodically. Re-add them when the Action starts failing.

### 3. Get a free Gemini API key

Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a free API key.

The free tier gives you **1,500 requests/day** — more than enough.

### 4. Add secrets to your repo

Go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Secret name | Value |
|---|---|
| `LEETCODE_SESSION` | Your LeetCode session cookie |
| `LEETCODE_CSRF` | Your LeetCode csrftoken cookie |
| `GEMINI_API_KEY` | Your Gemini API key |

### 5. Enable Actions and trigger a manual run

Go to **Actions → Sync LeetCode Solutions → Run workflow** to test it immediately.

After that, it runs automatically every day at 9 AM UTC.

---

## Project Structure

```
your-repo/
├── .github/
│   └── workflows/
│       └── sync.yml          # Daily cron Action
├── solutions/
│   ├── hash_map/
│   │   └── 0001_two-sum.md
│   ├── dynamic_programming/
│   │   └── 0070_climbing-stairs.md
│   └── ...
├── src/
│   ├── main.py               # Action entry point
│   ├── fetcher.py            # LeetCode GraphQL client
│   ├── analyzer.py           # Gemini analysis
│   ├── note_generator.py     # Markdown note builder
│   └── progress_tracker.py   # Progress JSON + README updater
├── tests/                    # pytest test suite
├── progress.json             # Auto-managed progress state
├── README.md                 # Auto-generated dashboard (this file, in your repo)
└── requirements.txt
```

---

## Running Locally

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Set environment variables
cp .env.example .env
# Edit .env with your actual values

# Run sync
export $(cat .env | xargs)
python src/main.py

# Run tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## vs LeetHub

| Feature | LeetHub (Chrome ext) | GitLeetNotes |
|---|---|---|
| Pushes code to GitHub | ✅ | ✅ |
| Works without a browser extension | ❌ | ✅ |
| AI complexity analysis | ❌ | ✅ |
| Pattern identification | ❌ | ✅ |
| Study notes with key insights | ❌ | ✅ |
| Progress dashboard by pattern | ❌ | ✅ |
| Runs automatically in background | ❌ | ✅ |
| Free | ✅ | ✅ |

---

## Limitations

- **LeetCode's GraphQL API is unofficial** — it may break if LeetCode changes their API. Session cookies also expire every few weeks.
- **Gemini free tier**: 1,500 requests/day is plenty for daily use but shared across all your projects.
- The Action fetches your **20 most recent accepted submissions** per run. If you solve more than 20 problems in a day, run the Action manually to catch up.

---

## Contributing

Issues and PRs are welcome. See the [issues](../../issues) tab.

---

## License

MIT — use it, fork it, improve it.
