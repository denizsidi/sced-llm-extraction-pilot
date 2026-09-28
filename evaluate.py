"""Compare manual coding with LLM output for the 5-paper pilot.

Usage:
    python evaluate.py
"""

from pathlib import Path
import pandas as pd
import re

MANUAL = Path("data/manual_coding.csv")
LLM = Path("results/llm_output.csv")
OUT = Path("results/comparison.csv")
SUMMARY = Path("results/summary.csv")

def norm_text(x):
    x = "" if pd.isna(x) else str(x)
    x = x.strip().lower()
    x = re.sub(r"\s+", " ", x)
    x = x.replace("–", "-").replace("—", "-")
    return x

def norm_number(x):
    if pd.isna(x) or str(x).strip() == "":
        return None
    try:
        return float(str(x).strip())
    except ValueError:
        m = re.search(r"-?\d+(?:\.\d+)?", str(x))
        return float(m.group()) if m else None

def main():
    manual = pd.read_csv(MANUAL)
    llm = pd.read_csv(LLM)

    merged = manual.merge(llm, on="paper_id", suffixes=("_manual", "_llm"))

    # Exact/near-exact structured scoring
    merged["n_participants_match"] = [
        int(norm_number(a) == norm_number(b) and norm_number(a) is not None)
        for a, b in zip(merged["n_participants_manual"], merged["n_participants_llm"])
    ]

    merged["age_mean_match"] = [
        int(
            norm_number(a) is not None
            and norm_number(b) is not None
            and abs(norm_number(a) - norm_number(b)) <= 0.05
        )
        for a, b in zip(merged["age_mean_manual"], merged["age_mean_llm"])
    ]

    # Design often differs in wording, so create a human-review column.
    merged["design_match"] = ""
    merged["design_notes"] = ""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUT, index=False)

    summary = pd.DataFrame({
        "field": ["n_participants", "age_mean"],
        "accuracy_percent": [
            round(100 * merged["n_participants_match"].mean(), 1),
            round(100 * merged["age_mean_match"].mean(), 1),
        ],
        "n": [len(merged), len(merged)]
    })
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")
    print("\nNext: open results/comparison.csv")
    print("For design_match, enter 1 if materially correct, 0.5 if partly correct, 0 if wrong.")
    print("Optionally explain differences in design_notes.")

if __name__ == "__main__":
    main()
