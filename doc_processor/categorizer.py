import json
import anthropic

client = anthropic.Anthropic()

SYSTEM = """You are a document categorizer.
Given raw document text, return ONLY a valid JSON object with:
- category: string (invoice, contract, report, form, other)
- language: string
- summary: string (max 2 sentences)
- key_fields: object (any important extracted key-value pairs)
- confidence: float (0-1)
No preamble, no markdown, only raw JSON."""

MAX_INPUT_CHARS = 8000


def categorize(raw_text: str) -> dict:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": raw_text[:MAX_INPUT_CHARS]}],
    )
    return json.loads(response.content[0].text)
