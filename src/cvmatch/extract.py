"""Extract structured facts from CV and job text.

Skill extraction matches the built-in skills list against the text.
Experience and education extraction use plain patterns, and the
README is honest that unusual wording can be missed.
"""

import re

from cvmatch.clean import clean_text
from cvmatch.skills import SKILLS


def extract_skills(text):
    """Return the canonical skills found in the text, in list order.

    Matching is case-insensitive and word-boundary aware, so "java"
    does not match "javascript". Longer variants are checked so
    "machine learning" wins over a bare "ml" mention in the same text.
    """
    cleaned = " " + clean_text(text) + " "
    found = []
    for skill, variants in SKILLS.items():
        for variant in sorted(variants, key=len, reverse=True):
            pattern = r"(?<![a-z0-9+#])" + re.escape(variant) + r"(?![a-z0-9+#])"
            if re.search(pattern, cleaned):
                found.append(skill)
                break
    return found


def extract_years_experience(text):
    """Guess years of experience from phrases like "5 years experience".

    Returns the largest number found in such phrases, or None.
    """
    lowered = clean_text(text)
    years = []
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:\+)?\s*years?(?:\s+of)?\s+experience", lowered):
        years.append(float(match.group(1)))
    for match in re.finditer(r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*years?", lowered):
        years.append(float(match.group(1)))
    return max(years) if years else None


DEGREE_LEVELS = [
    ("PhD", [r"\bph\.?d\b", r"\bdoctorate\b"]),
    ("Master's", [r"\bmaster'?s\b", r"\bm\.?sc\b", r"\bmba\b", r"\bms\b", r"\bm\.?phil\b"]),
    ("Bachelor's", [r"\bbachelor'?s\b", r"\bb\.?sc\b", r"\bbs\b", r"\bba\b", r"\bb\.?com\b", r"\bbe\b", r"\bb\.?eng\b"]),
    ("Diploma", [r"\bdiploma\b"]),
    ("Intermediate", [r"\bintermediate\b", r"\bf\.?sc\b", r"\bfa\b"]),
    ("Matric", [r"\bmatric\b"]),
]

RANK = {"Matric": 1, "Intermediate": 2, "Diploma": 3, "Bachelor's": 4, "Master's": 5, "PhD": 6}


def extract_degree_level(text):
    """Return the highest degree level named in the text, or ""."""
    lowered = clean_text(text)
    best = ""
    for level, patterns in DEGREE_LEVELS:
        for pattern in patterns:
            if re.search(pattern, lowered):
                if RANK[level] > RANK.get(best, 0):
                    best = level
                break
    return best


def enrich_cv(cv):
    """Fill in a CV's skills, experience and degree from its text."""
    cv.skills = extract_skills(cv.raw_text)
    cv.years_experience = extract_years_experience(cv.raw_text)
    cv.degree_level = extract_degree_level(cv.raw_text)
    return cv


def enrich_job(job):
    """Fill in a job's required skills and minimum experience."""
    job.required_skills = extract_skills(job.raw_text)
    job.min_experience = extract_years_experience(job.raw_text)
    return job
