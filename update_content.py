import os, json, datetime, re, urllib.request
from groq import Groq

TODAY = datetime.date.today().strftime("%B %d, %Y")
HISTORY_FILE = "content_history.json"

client = Groq(api_key=os.environ["GROQ_API_KEY"])


# ── HISTORY TRACKING ────────────────────────────────────────────────────────

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {"quiz_questions": [], "words_of_day": [], "story_titles": []}

def save_history(data):
    history = load_history()
    history["quiz_questions"].append(data.get("quiz", {}).get("question", ""))
    history["words_of_day"].append(data.get("word_of_day", {}).get("word", ""))
    for section in ["market_stories", "world_stories", "personal_stories", "tech_stories"]:
        for story in data.get(section, []):
            history["story_titles"].append(story.get("title", ""))
    # Keep only last 30 days worth
    for key in history:
        history[key] = history[key][-30:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


# ── REAL HEADLINES ───────────────────────────────────────────────────────────

def get_real_headlines():
    sources = [
        ("Yahoo Finance", "https://finance.yahoo.com/rss/topfinstories"),
        ("MarketWatch",   "https://feeds.content.dowjones.io/public/rss/mw_topstories"),
    ]
    all_titles = []
    for name, url in sources:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                content = r.read().decode("utf-8", errors="ignore")
            titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', content)
            if not titles:
                titles = re.findall(r'<title>(.*?)</title>', content)
            titles = [t.strip() for t in titles if len(t.strip()) > 20][:5]
            all_titles.extend(titles)
            print(f"Got {len(titles)} headlines from {name}")
        except Exception as e:
            print(f"Could not fetch {name}: {e}")
    if not all_titles:
        return "No live headlines available — use your knowledge of recent financial news."
    return "\n".join(f"- {t}" for t in all_titles[:10])


# ── PROMPT ───────────────────────────────────────────────────────────────────

BASE_PROMPT = """
You are the editor of "The Bull Brief," a daily finance newsletter written specifically
for high school students (ages 14-18) in the US. Today is {TODAY}.

TODAY'S REAL HEADLINES (use these as your primary source material):
{HEADLINES}

{AVOID_TEXT}

Generate today's content as a JSON object with this EXACT structure.
Return ONLY the JSON, no markdown, no backticks, no extra text.

{{
  "date": "{TODAY}",
  "breaking_news": {{
    "text": "One sentence breaking financial news headline based on today's real headlines above",
    "is_breaking": true
  }},
  "market_stories": [
    {{
      "cat": "Markets",
      "catClass": "tag-market",
      "time": "2h ago",
      "title": "Specific headline directly tied to today's real news above",
      "summary": "3-4 sentences in plain language a high schooler understands. Be specific — use real company names, real numbers, real events from today's headlines. End with why it matters to them personally.",
      "fullContent": "<p>Opening paragraph with real context and specific details from today's news.</p><h4>Subheading One</h4><p>Second paragraph going deeper. Explain any financial terms used.</p><div class='highlight'>A specific stat, number, or quote from today's news pulled out as a callout.</div><h4>What This Means For You</h4><p>Final paragraph connecting this directly to a high schooler's life, savings, or future.</p>",
      "mins": "3 min read",
      "featured": true
    }},
    {{
      "cat": "Markets",
      "catClass": "tag-market",
      "time": "3h ago",
      "title": "Second specific market story from today's headlines",
      "summary": "3-4 sentence specific summary with real numbers and names.",
      "fullContent": "<p>Opening paragraph with real details.</p><h4>Subheading</h4><p>Deeper explanation with real context.</p><div class='highlight'>Specific fact or number from today.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "2 min read",
      "featured": false
    }},
    {{
      "cat": "Markets",
      "catClass": "tag-market",
      "time": "4h ago",
      "title": "Third specific market story",
      "summary": "3-4 sentence specific summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "2 min read",
      "featured": false
    }}
  ],
  "world_stories": [
    {{
      "cat": "Economy",
      "catClass": "tag-world",
      "time": "1h ago",
      "title": "Economy or global story tied to today's news",
      "summary": "3-4 sentence specific summary with real details.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "3 min read",
      "featured": false
    }},
    {{
      "cat": "Global",
      "catClass": "tag-world",
      "time": "5h ago",
      "title": "Second world story",
      "summary": "3-4 sentence specific summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "4 min read",
      "featured": false
    }},
    {{
      "cat": "Economy",
      "catClass": "tag-world",
      "time": "6h ago",
      "title": "Third world story",
      "summary": "3-4 sentence specific summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "2 min read",
      "featured": false
    }}
  ],
  "personal_stories": [
    {{
      "cat": "Personal Finance",
      "catClass": "tag-personal",
      "time": "Today",
      "title": "Actionable personal finance topic for teens — must be different from recent ones",
      "summary": "3-4 sentence practical summary a teen can act on.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation with specific steps.</p><div class='highlight'>Key number or fact.</div><h4>Action Step</h4><p>One specific thing the student can do this week.</p>",
      "mins": "5 min read",
      "featured": false
    }},
    {{
      "cat": "Personal Finance",
      "catClass": "tag-personal",
      "time": "Today",
      "title": "Second personal finance topic — must be different from recent ones",
      "summary": "3-4 sentence practical summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact.</div><h4>Action Step</h4><p>Specific action item.</p>",
      "mins": "4 min read",
      "featured": false
    }}
  ],
  "tech_stories": [
    {{
      "cat": "Tech",
      "catClass": "tag-tech",
      "time": "3h ago",
      "title": "Tech or AI story from today's headlines",
      "summary": "3-4 sentence specific summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "3 min read",
      "featured": false
    }},
    {{
      "cat": "Tech",
      "catClass": "tag-tech",
      "time": "5h ago",
      "title": "Second tech story",
      "summary": "3-4 sentence specific summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "3 min read",
      "featured": false
    }},
    {{
      "cat": "Tech",
      "catClass": "tag-tech",
      "time": "7h ago",
      "title": "Third tech story",
      "summary": "3-4 sentence specific summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "2 min read",
      "featured": false
    }}
  ],
  "word_of_day": {{
    "word": "A financial term relevant to today's news — must not be a recently used word",
    "type": "noun / finance",
    "definition": "Clear 2-sentence definition a high schooler understands",
    "example": "A realistic quote using the word in today's news context",
    "tags": ["related", "terms", "here"]
  }},
  "quiz": {{
    "question": "A specific multiple choice question about today's actual news stories — must not repeat recent questions",
    "options": [
      {{"text": "A. Option one", "correct": false}},
      {{"text": "B. Correct answer", "correct": true}},
      {{"text": "C. Option three", "correct": false}},
      {{"text": "D. Option four", "correct": false}}
    ],
    "explanation": "2-sentence explanation of why the correct answer is right, referencing today's specific news"
  }},
  "explainer_strip": [
    {{"term": "Today's Context", "def": "One key concept from today's specific news explained simply with a real number or name"}},
    {{"term": "Why It Matters", "def": "Why today's specific news affects students personally — be concrete"}},
    {{"term": "Key Number", "def": "One important specific number from today's actual news with full context"}},
    {{"term": "Quick Tip", "def": "One actionable personal finance tip tied to today's specific theme"}}
  ]
}}

Rules:
- Write at an 8th-10th grade reading level
- Explain every financial term the first time you use it
- Always connect news to what it means for students lives, savings, or future
- Be SPECIFIC — use real company names, real dollar amounts, real percentages from today's headlines
- Sound like a smart older student, not a corporate newsletter
- For fullContent: write real full article content, not placeholder text
- IMPORTANT: catClass must use camelCase exactly as shown
- IMPORTANT: Every story, quiz question, and word of the day must feel fresh and different from recent content
"""


# ── MAIN ─────────────────────────────────────────────────────────────────────

def update():
    print(f"Generating content for {TODAY}...")

    headlines = get_real_headlines()
    print(f"\nHeadlines fetched:\n{headlines}\n")

    history = load_history()
    avoid_lines = []
    if history["quiz_questions"]:
        recent_q = [q for q in history["quiz_questions"][-7:] if q]
        if recent_q:
            avoid_lines.append(f"AVOID these recent quiz questions (do not repeat or closely resemble them): {' | '.join(recent_q)}")
    if history["words_of_day"]:
        recent_w = [w for w in history["words_of_day"][-14:] if w]
        if recent_w:
            avoid_lines.append(f"AVOID these recent words of the day (pick something completely different): {', '.join(recent_w)}")
    if history["story_titles"]:
        recent_s = [s for s in history["story_titles"][-15:] if s]
        if recent_s:
            avoid_lines.append(f"AVOID topics similar to these recent story titles: {' | '.join(recent_s)}")
    avoid_text = "\n".join(avoid_lines) if avoid_lines else ""

    prompt = BASE_PROMPT.format(
        TODAY=TODAY,
        HEADLINES=headlines,
        AVOID_TEXT=avoid_text
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=8000
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)

    data = json.loads(raw)

    with open("content.json", "w") as f:
        json.dump(data, f, indent=2)

    save_history(data)

    print(f"Done! content.json written for {TODAY}")
    print(f"Word of the day: {data.get('word_of_day', {}).get('word', 'N/A')}")
    print(f"Quiz: {data.get('quiz', {}).get('question', 'N/A')[:80]}...")


if __name__ == "__main__":
    update()
