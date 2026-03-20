# Daily AI & Tech News Digest 🤖

Automated bilingual (English + 中文) daily news digest, delivered to your inbox.

## How it works

1. **Fetch** — Pulls top stories from Hacker News + RSS feeds (TechCrunch, The Verge, Ars Technica, Google AI Blog, OpenAI, Anthropic)
2. **Curate** — Gemini 2.0 Flash picks the 8 most important AI/tech stories
3. **Translate** — Generates bilingual titles and summaries
4. **Send** — Delivers a styled HTML email via Resend

## Setup

### 1. Get API keys

- **Gemini API key** (free): [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- **Resend API key** (free): [resend.com](https://resend.com) (100 emails/day)

### 2. Create GitHub repo and add secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Value |
|--------|-------|
| `GEMINI_API_KEY` | Your Gemini API key |
| `RESEND_API_KEY` | Your Resend API key |
| `RECIPIENT_EMAIL` | Your email address |

### 3. Push and go

```bash
git init && git add -A && git commit -m "Initial commit"
gh repo create daily-ai-news --private --source=. --push
```

The workflow runs daily at **6:00 AM PST**. You can also trigger it manually from the Actions tab.

### 4. (Optional) Custom sender domain

By default, emails come from `news@resend.dev`. To use your own domain, configure it in [Resend dashboard](https://resend.com/domains) and update `SENDER_EMAIL`.

## Local testing

```bash
export GEMINI_API_KEY=AIza...
export RESEND_API_KEY=re_...
export RECIPIENT_EMAIL=you@example.com

pip install -r requirements.txt
python daily_news.py
```

## Cost

- **Gemini API**: Free (2.0 Flash free tier)
- **Resend**: Free (under 100 emails/day)
- **GitHub Actions**: Free

**Total: $0/month**
