import os, json, datetime, re
from google import genai

TODAY = datetime.date.today().strftime("%B %d, %Y")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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
      "cat_class": "tag-market",
      "time": "2h ago",
      "title": "Headline about today's biggest market story",
      "summary": "3-4 sentence explanation in plain language a high schooler can understand. End with why it matters to them personally.",
      "mins": "3 min read",
      "featured": true
    }},
    {{"cat": "Markets", "cat_class": "tag-market", "time": "3h ago", "title": "Second market story", "summary": "Explanation.", "mins": "2 min read", "featured": false}},
    {{"cat": "Markets", "cat_class": "tag-market", "time": "4h ago", "title": "Third market story", "summary": "Explanation.", "mins": "2 min read", "featured": false}}
  ],
  "world_stories": [
    {{"cat": "Economy", "cat_class": "tag-world", "time": "1h ago", "title": "World story 1", "summary": "Explanation.", "mins": "3 min read", "featured": false}},
    {{"cat": "Global", "cat_class": "tag-world", "time": "5h ago", "title": "World story 2", "summary": "Explanation.", "mins": "4 min read", "featured": false}},
    {{"cat": "Economy", "cat_class": "tag-world", "time": "6h ago", "title": "World story 3", "summary": "Explanation.", "mins": "2 min read", "featured": false}}
  ],
  "personal_stories": [
    {{"cat": "Personal Finance", "cat_class": "tag-personal", "time": "Today", "title": "Personal finance story 1", "summary": "Explanation.", "mins": "5 min read", "featured": false}},
    {{"cat": "Personal Finance", "cat_class": "tag-personal", "time": "Today", "title": "Personal finance story 2", "summary": "Explanation.", "mins": "4 min read", "featured": false}}
  ],
  "tech_stories": [
    {{"cat": "Tech", "cat_class": "tag-tech", "time": "3h ago", "title": "Tech story 1", "summary": "Explanation.", "mins": "3 min read", "featured": false}},
    {{"cat": "Tech", "cat_class": "tag-tech", "time": "5h ago", "title": "Tech story 2", "summary": "Explanation.", "mins": "3 min read", "featured": false}},
    {{"cat": "Tech", "cat_class": "tag-tech", "time": "7h ago", "title": "Tech story 3", "summary": "Explanation.", "mins": "2 min read", "featured": false}}
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
"""

def update():
    print(f"Generating content for {TODAY}...")
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=PROMPT
    )
    raw = response.text.strip()
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    data = json.loads(raw)
    with open("content.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done! content.json written for {TODAY}")

if __name__ == "__main__":
    update()
```

**Then also update `daily-update.yml`** — find this line:
```
run: pip install google-generativeai
```
Change it to:
```
run: pip install google-genai
