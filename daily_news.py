"""
Daily AI & Tech News Digest — Bilingual (中文 + English)
Fetches top stories from multiple sources, uses Gemini to curate and summarize,
then sends a bilingual email digest via Resend.
"""

import json
import os
import sys
from datetime import datetime, timezone

import feedparser
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "AI News Digest <news@resend.dev>")
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
RESEND_API_KEY = os.environ["RESEND_API_KEY"]

RSS_FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://blog.google/technology/ai/rss/",
    "https://openai.com/blog/rss.xml",
    "https://www.anthropic.com/rss.xml",
]

MAX_HN_STORIES = 40
MAX_RSS_PER_FEED = 10


# ---------------------------------------------------------------------------
# News fetching
# ---------------------------------------------------------------------------
def fetch_hackernews() -> list[dict]:
    """Fetch top stories from Hacker News."""
    try:
        top_ids = requests.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10
        ).json()[:MAX_HN_STORIES]
    except Exception as e:
        print(f"[WARN] HackerNews fetch failed: {e}")
        return []

    stories = []
    for sid in top_ids:
        try:
            item = requests.get(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5
            ).json()
            if item and item.get("title"):
                stories.append(
                    {
                        "title": item["title"],
                        "url": item.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "source": "Hacker News",
                        "score": item.get("score", 0),
                    }
                )
        except Exception:
            continue
    return stories


def fetch_rss_feeds() -> list[dict]:
    """Fetch recent articles from RSS feeds."""
    stories = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:MAX_RSS_PER_FEED]:
                stories.append(
                    {
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "source": feed.feed.get("title", feed_url),
                        "summary": entry.get("summary", "")[:200],
                    }
                )
        except Exception as e:
            print(f"[WARN] RSS fetch failed for {feed_url}: {e}")
    return stories


def fetch_all_news() -> list[dict]:
    """Aggregate news from all sources."""
    hn = fetch_hackernews()
    rss = fetch_rss_feeds()
    all_news = hn + rss
    print(f"[INFO] Fetched {len(hn)} HN stories + {len(rss)} RSS articles = {len(all_news)} total")
    return all_news


# ---------------------------------------------------------------------------
# AI curation & translation
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You are a senior tech news editor. Your reader is a software engineer at Salesforce \
who cares about AI, cloud/SaaS, enterprise software, and the broader tech industry.

Your task: from the raw story list, pick the **8 most important and interesting stories** \
of the day. Prioritize:
1. Major AI breakthroughs, product launches, and policy changes
2. Enterprise software / CRM / Salesforce ecosystem news
3. Big tech company moves (Google, Microsoft, Apple, Meta, Amazon, etc.)
4. Developer tools and open-source AI news

Output a bilingual digest in **valid JSON** (no markdown fences) with this schema:
{
  "stories": [
    {
      "title_en": "English title",
      "title_zh": "中文标题",
      "summary_en": "1-2 sentence English summary",
      "summary_zh": "1-2句中文摘要",
      "url": "original URL",
      "source": "source name"
    }
  ],
  "editor_note_en": "One sentence about today's overall theme",
  "editor_note_zh": "一句话总结今日主题"
}
"""


def curate_news(stories: list[dict]) -> dict:
    """Use Gemini to pick top stories and produce bilingual summaries."""
    story_text = "\n".join(
        f"- [{s.get('source','')}] {s['title']} | {s.get('url','')} | {s.get('summary','')}"
        for s in stories
    )

    user_msg = f"Today is {datetime.now(timezone.utc).strftime('%Y-%m-%d')}.\n\nRaw stories:\n{story_text}"

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": [{"text": user_msg}]}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 3000,
                "responseMimeType": "application/json",
            },
        },
        timeout=60,
    )
    response.raise_for_status()

    raw = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    # Handle potential markdown code fences
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:-3]
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Email rendering
# ---------------------------------------------------------------------------
def render_email(digest: dict) -> str:
    """Render the digest as an HTML email."""
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stories_html = ""

    for i, s in enumerate(digest["stories"], 1):
        stories_html += f"""
        <tr>
          <td style="padding:16px 0;border-bottom:1px solid #eee;">
            <div style="font-size:13px;color:#888;margin-bottom:4px;">#{i} · {s['source']}</div>
            <a href="{s['url']}" style="font-size:17px;font-weight:600;color:#1a1a1a;text-decoration:none;">
              {s['title_en']}
            </a>
            <div style="font-size:15px;color:#555;margin-top:2px;">{s['title_zh']}</div>
            <p style="font-size:14px;color:#333;margin:8px 0 4px 0;line-height:1.5;">{s['summary_en']}</p>
            <p style="font-size:14px;color:#555;margin:0;line-height:1.5;">{s['summary_zh']}</p>
          </td>
        </tr>"""

    return f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f5;padding:24px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);">
        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:28px 24px;text-align:center;">
            <div style="font-size:22px;font-weight:700;color:#fff;">🤖 Daily AI & Tech Digest</div>
            <div style="font-size:14px;color:#aaa;margin-top:4px;">{date_str} · AI 科技日报</div>
          </td>
        </tr>
        <!-- Editor note -->
        <tr>
          <td style="padding:20px 24px 8px;">
            <div style="background:#f0f4ff;border-radius:8px;padding:14px 16px;font-size:14px;color:#333;line-height:1.5;">
              📝 {digest['editor_note_en']}<br>
              <span style="color:#666;">{digest['editor_note_zh']}</span>
            </div>
          </td>
        </tr>
        <!-- Stories -->
        <tr>
          <td style="padding:8px 24px 24px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              {stories_html}
            </table>
          </td>
        </tr>
        <!-- Footer -->
        <tr>
          <td style="background:#fafafa;padding:16px 24px;text-align:center;font-size:12px;color:#999;">
            Curated by Gemini · Powered by Google AI<br>
            Built with ❤️ for engineers who stay informed
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Send email
# ---------------------------------------------------------------------------
def send_email(subject: str, html: str):
    """Send email via Resend API."""
    import resend

    resend.api_key = RESEND_API_KEY
    resp = resend.Emails.send(
        {
            "from": SENDER_EMAIL,
            "to": [RECIPIENT_EMAIL],
            "subject": subject,
            "html": html,
        }
    )
    print(f"[INFO] Email sent: {resp}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("[INFO] Fetching news...")
    stories = fetch_all_news()
    if not stories:
        print("[ERROR] No stories fetched, aborting.")
        sys.exit(1)

    print("[INFO] Curating with Gemini...")
    digest = curate_news(stories)
    print(f"[INFO] Selected {len(digest['stories'])} stories")

    print("[INFO] Rendering email...")
    date_str = datetime.now(timezone.utc).strftime("%m/%d")
    subject = f"🤖 AI Daily {date_str} | {digest['editor_note_en'][:60]}"
    html = render_email(digest)

    print("[INFO] Sending email...")
    send_email(subject, html)
    print("[INFO] Done!")


if __name__ == "__main__":
    main()
