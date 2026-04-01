"""
update_content.py — The Bull Brief Daily AI Content Updater
Run this script daily (via GitHub Actions) to refresh content.json
Requires: pip install google-generativeai python-dotenv
Get your FREE Gemini API key at: https://aistudio.google.com
"""

import os, json, datetime, re
import google.generativeai as genai

# ── CONFIG ──────────────────────────────────────────────────────────────────
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")  # Free tier model

TODAY = datetime.date.today().strftime("%B %d, %Y")

# ── PROMPT ──────────────────────────────────────────────────────────────────
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
    {{same structure, featured: false}},
    {{same structure, featured: false}}
  ],
  "world_stories": [
    {{same 3-story structure with cat: "Economy" or "Global", cat_class: "tag-world"}},
    ...
  ],
  "personal_stories": [
    {{same structure with cat: "Personal Finance", cat_class: "tag-personal", 2 stories}},
    ...
  ],
  "tech_stories": [
    {{same structure with cat: "Tech", cat_class: "tag-tech", 3 stories}},
    ...
  ],
  "word_of_day": {{
    "word": "Financial term",
    "type": "noun / finance",
    "definition": "Clear 2-sentence definition a high schooler understands",
    "example": "A realistic quote using the word in a news context",
    "tags": ["related", "terms", "here", "max5"]
  }},
  "quiz": {{
    "question": "Multiple choice question testing understanding of today's news",
    "options": [
      {{"text": "A. Option one", "correct": false}},
      {{"text": "B. Correct answer", "correct": true}},
      {{"text": "C. Option three", "correct": false}},
      {{"text": "D. Option four", "correct": false}}
    ],
    "explanation": "2-sentence explanation of why the correct answer is right, in plain English"
  }},
  "explainer_strip": [
    {{"term": "Today's Context", "def": "One key concept from today's news explained simply"}},
    {{"term": "Why It Matters", "def": "Why today's news affects students personally"}},
    {{"term": "Key Number", "def": "One important number from today's news with context"}},
    {{"term": "Quick Tip", "def": "One actionable personal finance tip tied to today's theme"}}
  ]
}}

Rules:
- Write at an 8th-10th grade reading level (clear, not dumbed down)
- Explain every financial term the first time you use it
- Always connect news to what it means for students' lives, savings, or future
- Be accurate — use real current events and real market data from {TODAY}
- Sound like a smart older student, not a corporate newsletter
- Stories must be genuinely educational, not just headlines
"""

# ── RUN ──────────────────────────────────────────────────────────────────────
def update():
    print(f"Generating content for {TODAY}...")
    response = model.generate_content(PROMPT)
    raw = response.text.strip()
    
    # Strip any accidental markdown fences
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    
    data = json.loads(raw)
    
    with open("content.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ content.json written with {len(data)} top-level keys")
    print(f"  Stories: {len(data['market_stories'])} market, {len(data['world_stories'])} world, {len(data['personal_stories'])} personal, {len(data['tech_stories'])} tech")

if __name__ == "__main__":
    update()
