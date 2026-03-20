# Daily AI & Tech News Digest 🤖

Automated bilingual (English + 中文) daily news digest, delivered to your inbox.

## How it works

1. **Fetch** — Pulls top stories from Hacker News + RSS feeds (TechCrunch, The Verge, Ars Technica, Google AI Blog, OpenAI, Anthropic)
2. **Curate** — AI picks the 8 most important AI/tech stories via OpenRouter (free models with automatic fallback)
3. **Translate** — Generates bilingual titles and summaries
4. **Send** — Delivers a styled HTML email via Gmail SMTP

## Setup

### 1. Get API keys

- **OpenRouter API key** (free): [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys)
- **Gmail App Password** (free): [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2-Step Verification)

### 2. Create GitHub repo and add secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|--------|-------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `GMAIL_ADDRESS` | Your Gmail address |
| `GMAIL_APP_PASSWORD` | Your Gmail App Password |
| `RECIPIENT_EMAILS` | Comma-separated recipient emails (e.g. `a@gmail.com,b@gmail.com`) |

### 3. Push and go

```bash
git init && git add -A && git commit -m "Initial commit"
gh repo create daily-ai-news --private --source=. --push
```

The workflow runs daily at **6:00 AM PST**. You can also trigger it manually from the Actions tab.

## Local testing

```bash
export OPENROUTER_API_KEY=sk-or-v1-...
export GMAIL_ADDRESS=you@gmail.com
export GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
export RECIPIENT_EMAILS=you@gmail.com,friend@gmail.com

pip install -r requirements.txt
python daily_news.py
```

## Cost

- **OpenRouter**: Free (uses free-tier models with automatic fallback)
- **Gmail SMTP**: Free (up to 500 emails/day)
- **GitHub Actions**: Free

**Total: $0/month**
