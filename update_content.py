import os, json, datetime, re
from groq import Groq

TODAY = datetime.date.today().strftime("%B %d, %Y")

client = Groq(api_key=os.environ["GROQ_API_KEY"])

PROMPT = f"""
You are the editor of "The Bull Brief," a daily finance newsletter written specifically
for high school students (ages 14-18) in the US. Today is {TODAY}.

Generate today's content as a JSON object with this EXACT structure.
Return ONLY the JSON, no markdown, no backticks, no extra text.

{{
  "date": "{TODAY}",
  "breaking_news": {{
    "text": "One sentence breaking financial news headline for today",
    "is_breaking": true
  }},
  "market_stories": [
    {{
      "cat": "Markets",
      "catClass": "tag-market",
      "time": "2h ago",
      "title": "Headline about today's biggest market story",
      "summary": "3-4 sentence explanation in plain language a high schooler can understand. End with why it matters to them personally.",
      "fullContent": "<p>Opening paragraph expanding on the headline with real context.</p><h4>Subheading One</h4><p>Second paragraph going deeper. Explain any terms used.</p><div class='highlight'>A key stat, quote, or fact pulled out as a callout.</div><h4>What This Means For You</h4><p>Final paragraph connecting this directly to the student's life, savings, or future.</p>",
      "mins": "3 min read",
      "featured": true
    }},
    {{
      "cat": "Markets",
      "catClass": "tag-market",
      "time": "3h ago",
      "title": "Second market story",
      "summary": "3-4 sentence summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "2 min read",
      "featured": false
    }},
    {{
      "cat": "Markets",
      "catClass": "tag-market",
      "time": "4h ago",
      "title": "Third market story",
      "summary": "3-4 sentence summary.",
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
      "title": "World story 1",
      "summary": "3-4 sentence summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "3 min read",
      "featured": false
    }},
    {{
      "cat": "Global",
      "catClass": "tag-world",
      "time": "5h ago",
      "title": "World story 2",
      "summary": "3-4 sentence summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "4 min read",
      "featured": false
    }},
    {{
      "cat": "Economy",
      "catClass": "tag-world",
      "time": "6h ago",
      "title": "World story 3",
      "summary": "3-4 sentence summary.",
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
      "title": "Personal finance story 1",
      "summary": "3-4 sentence summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "5 min read",
      "featured": false
    }},
    {{
      "cat": "Personal Finance",
      "catClass": "tag-personal",
      "time": "Today",
      "title": "Personal finance story 2",
      "summary": "3-4 sentence summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "4 min read",
      "featured": false
    }}
  ],
  "tech_stories": [
    {{
      "cat": "Tech",
      "catClass": "tag-tech",
      "time": "3h ago",
      "title": "Tech story 1",
      "summary": "3-4 sentence summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "3 min read",
      "featured": false
    }},
    {{
      "cat": "Tech",
      "catClass": "tag-tech",
      "time": "5h ago",
      "title": "Tech story 2",
      "summary": "3-4 sentence summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "3 min read",
      "featured": false
    }},
    {{
      "cat": "Tech",
      "catClass": "tag-tech",
      "time": "7h ago",
      "title": "Tech story 3",
      "summary": "3-4 sentence summary.",
      "fullContent": "<p>Opening paragraph.</p><h4>Subheading</h4><p>Deeper explanation.</p><div class='highlight'>Key fact or stat.</div><h4>What This Means For You</h4><p>Student relevance.</p>",
      "mins": "2 min read",
      "featured": false
    }}
  ],
  "word_of_day": {{
    "word": "A financial term relevant to today's news",
    "type": "noun / finance",
    "definition": "Clear 2-sentence definition a high schooler understands",
    "example": "A realistic quote using the word in a news context",
    "tags": ["related", "terms", "here"]
  }},
  "quiz": {{
    "question": "Multiple choice question testing understanding of today's news",
    "options": [
      {{"text": "A. Option one", "correct": false}},
      {{"text": "B. Correct answer", "correct": true}},
      {{"text": "C. Option three", "correct": false}},
      {{"text": "D. Option four", "correct": false}}
    ],
    "explanation": "2-sentence explanation of why the correct answer is right"
  }},
  "explainer_strip": [
    {{"term": "Today's Context", "def": "One key concept from today's news explained simply"}},
    {{"term": "Why It Matters", "def": "Why today's news affects students personally"}},
    {{"term": "Key Number", "def": "One important number from today's news with context"}},
    {{"term": "Quick Tip", "def": "One actionable personal finance tip tied to today's theme"}}
  ]
}}

Rules:
- Write at an 8th-10th grade reading level
- Explain every financial term the first time you use it
- Always connect news to what it means for students lives, savings, or future
- Use real current financial news and data from today {TODAY}
- Sound like a smart older student, not a corporate newsletter
- For fullContent: write real, full article content — not placeholder text. Each article should have 3-4 paragraphs with actual information expanding on the summary. Use the HTML tags exactly as shown.
- IMPORTANT: the catClass field must use camelCase exactly as shown (catClass, not cat_class)
"""

def update():
    print(f"Generating content for {TODAY}...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": PROMPT}],
        temperature=0.7,
        max_tokens=8000
    )
    raw = response.choices[0].message.content.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    data = json.loads(raw)
    with open("content.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done! content.json written for {TODAY}")

if __name__ == "__main__":
    update()
