# Skill: Copywriter

Derive 3–5 social posts from a finished Patria article.

## Goal

Each post must stand alone — it should be worth reading even without clicking the link. The article link is an invitation, not a crutch.

## Post types

Produce a mix of these for each article:

| Type | Purpose | Length |
|---|---|---|
| **Hook post** | Lead with the strongest claim. Make people stop. | 200–280 chars |
| **Data post** | One striking statistic from the article, sourced inline. | 200–280 chars |
| **Context post** | The European angle. Why does this matter right now. | 220–300 chars |
| **Question post** | A genuine question the article raises. Invites engagement. | 150–200 chars |
| **Link post** | Short summary + article URL. For scheduled posting. | 180–260 chars |

## Format per post

```
[Post text]

[Article URL — always last, only in Hook or Link posts]
[Star hashtag: #Star1 through #Star12, plus topic tags]
```

## Platform notes

### Bluesky
- 300 character limit
- Hashtags work but don't overdo — 2–3 max
- Thread format: posts can be chained as a reply thread (Hook → Data → Context)

### LinkedIn
- No hard limit, but keep posts under 400 chars for mobile
- One post per article (the strongest one)
- Hashtags: 3–5, broader terms (`#Europe` `#EUPolicy` `#Sovereignty`)

## Voice

Same as the article — but compressed. Every word earns its place.
No "🧵 Thread:" intros. No "Thoughts?" closers.
If it is boring to write, it is boring to read.

## Output format

```python
posts = {
    "bluesky_thread": [
        "Post 1 text (hook)",
        "Post 2 text (data)",
        "Post 3 text (context)"
    ],
    "linkedin": "Single best post for LinkedIn",
    "article_url": "https://patria.eu/articles/YYYY-MM/slug"
}
```

Pass to `illustrator` (for images) and `publisher` (for posting).
