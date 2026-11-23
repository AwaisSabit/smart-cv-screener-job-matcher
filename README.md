# CVMatch — Smart CV Screener and Job Matcher

Built as part of a 30-day portfolio challenge, Nov–Dec 2026.

CVMatch screens CVs against job descriptions and ranks them by fit.
Give it one CV and one job, and it returns a 0–100 match score with a
breakdown: how much comes from text similarity, how many of the job's
skills the CV has, and whether the experience fits. Give it a folder of
CVs and one job, and it ranks them all, shortlists the ones above your
threshold, and writes a screening report.

## What it does

- Reads CVs from `.txt`, `.pdf` and `.docx` files
- Extracts skills from a built-in list of 60+ tech, business and soft skills
- Extracts years of experience and degree level from CV text
- Scores a CV against a job with TF-IDF + cosine similarity, matched
  skills and experience fit, combined into one 0–100 score
- Shows which skills matched, which are missing, and where the score
  comes from
- Ranks many CVs against one job, or many jobs against one CV
- Shortlists above a score threshold and exports results to CSV and JSON
- Batch-screens a whole folder of CVs in one command

## Install

```bash
pip install -e .
```

## Quick start

```bash
# Score one CV against one job
cvmatch match cv.txt job.txt

# Rank every CV in a folder against a job
cvmatch rank cvs/ job.txt --top 5

# Screen a folder and write a report
cvmatch screen cvs/ job.txt --threshold 60 --report report.md

# Batch-screen and save results
cvmatch batch cvs/ job.txt --output results.csv
```

See `examples/demo.py` for a full worked example with fictional CVs.
Run it from the project root:

```bash
python examples/demo.py
```

It scores one CV against the Python Developer job, ranks all four
sample CVs, and writes the screening report, results CSV/JSON and
shortlist to `examples/output/`. Regenerate the PDF and Word versions
of the sample CVs with:

```bash
python examples/generate_samples.py
```

## Honest limits

- TF-IDF matching is keyword-based. It compares the words in a CV with
  the words in a job description — it does not understand what a person
  can actually do, and it cannot judge attitude, honesty or potential.
- A high score does not mean a good hire. Use the score to shortlist,
  then read the CVs yourself.
- The built-in skills list is not exhaustive. A skill that is not in the
  list is never counted as matched or missing.
- PDF parsing can miss text in badly formatted or scanned CVs (a scanned
  CV is a picture, not text). `.txt` and `.docx` CVs parse most reliably.
- Experience and degree extraction use patterns in the text; unusual
  wording can be missed or misread.

## All sample data is fictional

Every sample CV and job description in `examples/samples/` is made up.
The people, companies and contact details do not exist.
