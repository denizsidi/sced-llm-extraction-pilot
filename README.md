# LLM-Assisted Extraction of SCED Study Characteristics

## Overview

This small pilot project explored whether a large language model (LLM) could extract basic study characteristics from open-access single-case experimental design (SCED) papers involving children and adolescents.

The project was designed as a familiarisation exercise rather than a formal validation study. The main goal was to gain practical experience with structured LLM extraction, manual reference coding, and transparent comparison of automated outputs against human-coded data.

## Research Question

How closely do LLM-extracted study characteristics agree with manual coding across a small sample of youth SCED papers?

## Sample

Five open-access empirical SCED papers were selected from a larger initial set of youth intervention studies.

The pilot included:

- paper01
- paper03
- paper05
- paper07
- paper10

The papers represented different SCED structures, including ABC, multiple-baseline, non-concurrent multiple-baseline, ABAB, and AB designs.

## Extraction Fields

The LLM was asked to extract three study characteristics from each paper:

- number of analysed participants/cases
- SCED design
- mean participant age

A fixed extraction schema and the same prompt structure were used across all papers.

## Manual Coding

A manual reference table was created before comparing it with the LLM output.

For each paper, the following fields were coded:

- `n_participants`
- `design`
- `age_mean`

When mean age was not explicitly reported in the article, it was coded as not reported rather than inferred.

## LLM Extraction

PDF text was extracted using Python and `pypdf`.

The extracted article text was then sent to an LLM through OpenRouter using a fixed prompt that instructed the model to:

- use only information explicitly stated in the article
- avoid guessing or inferring missing information
- return structured JSON output
- provide supporting evidence for extracted values

The structured outputs were saved as CSV files for comparison with the manual coding.

## Evaluation

Agreement was evaluated separately for each field.

Participant count was scored using exact numeric agreement.

Mean age was scored using numeric agreement with a small tolerance.

SCED design was reviewed manually because equivalent design labels can differ in wording. Design agreement was scored as:

- `1` = materially correct
- `0.5` = partially correct
- `0` = incorrect

## Results

Across the five-paper pilot:

- **Participant count:** 100% agreement
- **SCED design:** 80% agreement
- **Mean age:** 60% agreement

The mean descriptive agreement across the three fields was:

**80%**

These values are descriptive only and should not be interpreted as an estimate of general LLM extraction accuracy.

## Interpretation

The pilot showed that some structured study characteristics were easier for the LLM to extract than others.

Participant count was extracted consistently across all five papers, while mean age produced more disagreement. SCED design extraction was generally successful but still required human review because differences in terminology and level of specificity can affect whether two labels should be considered equivalent.

The exercise highlighted the importance of validating automated extraction rather than treating LLM-generated outputs as automatically reliable.

## Limitations

This project has several important limitations:

- the sample included only five papers
- the papers were selected purposively rather than systematically
- manual coding was completed by a single coder
- no inter-rater reliability estimate was available
- only three study characteristics were evaluated
- PDF-to-text extraction may introduce formatting or encoding errors
- results may depend on the specific model, prompt, and model version used
- the project did not attempt to reconstruct symptom trajectories from figures or graphs
- the project does not establish clinical validity or suitability for automated evidence synthesis

## Reproducibility

The repository contains:

- the extraction script
- the manual coding template
- the LLM output structure
- the comparison script
- the summary script
- the extraction schema and workflow

Article PDFs are not included in the repository.

## Project Structure

```text
sced_pilot_5papers/
├── data/
│   └── manual_coding.csv
├── papers/
│   └── README.txt
├── results/
│   ├── llm_output.csv
│   ├── comparison.csv
│   └── summary.csv
├── extract.py
├── evaluate.py
├── summarise.py
├── requirements.txt
└── README.md
