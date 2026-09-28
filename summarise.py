"""Summarise the 5-paper pilot after manual review of design_match.

Usage:
    python summarise.py
"""

from pathlib import Path
import pandas as pd

COMP = Path("results/comparison.csv")

def main():
    df = pd.read_csv(COMP)

    df["design_match"] = pd.to_numeric(df["design_match"], errors="coerce")
    if df["design_match"].isna().any():
        raise SystemExit("Fill all design_match cells in results/comparison.csv first.")

    field_scores = {
        "n_participants": df["n_participants_match"].mean(),
        "age_mean": df["age_mean_match"].mean(),
        "design": df["design_match"].mean(),
    }

    overall = sum(field_scores.values()) / len(field_scores)

    print("Field-level agreement")
    for field, score in field_scores.items():
        print(f"- {field}: {score*100:.1f}%")

    print(f"\nOverall mean agreement across 3 fields: {overall*100:.1f}%")
    print("\nUse this only as a descriptive pilot result (N=5), not as a general accuracy claim.")

if __name__ == "__main__":
    main()
