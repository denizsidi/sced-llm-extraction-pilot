"""Extract 3 SCED study characteristics from 5 PDFs via OpenRouter.

Before running:
    export OPENROUTER_API_KEY="..."
    export LLM_MODEL="openrouter/free"   # or set a fixed free model
    python extract.py
"""

import csv
import json
import os
import re
from pathlib import Path

import requests
from pypdf import PdfReader

PAPERS = Path("papers")
OUT = Path("results/llm_output.csv")
RAW = Path("results/raw")

PAPER_IDS = ["paper01", "paper03", "paper05", "paper07", "paper10"]
MODEL = os.environ.get("LLM_MODEL", "openrouter/free")
MAX_CHARS = 60000

SYSTEM = (
    "You extract structured data from single-case experimental design (SCED) "
    "research articles. Use only information explicitly stated in the article. "
    "Do not guess. If a value is not reported, return null. Return JSON only."
)

USER_TEMPLATE = """Extract exactly these three fields from the article:

- n_participants: integer number of analysed participants/cases
- design: concise SCED design label
- age_mean: mean participant age in years as a number, or null if not reported

Also include:
- evidence: object with n_participants, design, and age_mean; each value should be
  a short verbatim quote (maximum 20 words) supporting the extraction, or null.

Return valid JSON with exactly these top-level keys:
n_participants, design, age_mean, evidence

ARTICLE:
{text}
"""

def pdf_to_text(path: Path) -> str:
    reader = PdfReader(str(path))
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    return text[:MAX_CHARS]

def parse_json(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.MULTILINE).strip()
    m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
    if m:
        raw = m.group(0)
    return json.loads(raw)

def call_openrouter(user_prompt: str) -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is not set.")
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "temperature": 0,
            "messages": [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout=180,
    )
    r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    if content is None:
        raise ValueError("Model returned empty content.")
    return content

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)

    rows = []

    for paper_id in PAPER_IDS:
        pdf = PAPERS / f"{paper_id}.pdf"
        if not pdf.exists():
            print(f"SKIP {paper_id}: missing {pdf}")
            continue

        print(f"Processing {paper_id} ...")
        text = pdf_to_text(pdf)

        raw = call_openrouter(USER_TEMPLATE.format(text=text))
        (RAW / f"{paper_id}.json").write_text(raw, encoding="utf-8")

        try:
            data = parse_json(raw)
        except Exception as e:
            print(f"  ERROR parsing {paper_id}: {e}")
            data = {}

        rows.append({
            "paper_id": paper_id,
            "n_participants": data.get("n_participants"),
            "design": data.get("design"),
            "age_mean": data.get("age_mean"),
        })

        print(f"  OK {paper_id}")

    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["paper_id", "n_participants", "design", "age_mean"]
        )
        w.writeheader()
        w.writerows(rows)

    print(f"\nSaved {len(rows)} rows to {OUT} (model: {MODEL})")

if __name__ == "__main__":
    main()
