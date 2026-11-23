"""Tests for TF-IDF similarity, the 0–100 score and the breakdown."""

import pytest

from cvmatch.models import CV, Job
from cvmatch.score import (
    breakdown_lines,
    cosine_score,
    experience_fit_score,
    keyword_overlap,
    match_details,
    match_score,
    missing_skills,
    score_label,
    skill_gap_report,
    skill_match_score,
)

PYTHON_JOB = Job(
    title="Python Developer",
    raw_text=(
        "Python Developer. Need Django, Flask, SQL, REST API and Git. "
        "3 years of experience in Python development required."
    ),
)

STRONG_CV = CV(
    name="Ayesha Khan",
    raw_text=(
        "Ayesha Khan. Python Developer with 5 years of experience. "
        "Django, Flask, SQL, REST API, Git, Docker, AWS. "
        "BS Computer Science."
    ),
)

WEAK_CV = CV(
    name="Usman Raza",
    raw_text=(
        "Usman Raza. Fresh graduate. Basic Python and HTML. "
        "BS Computer Science, 2025. Fast learner."
    ),
)


def test_cosine_identical_texts_is_one():
    assert cosine_score("python django sql", "python django sql") > 0.99


def test_cosine_unrelated_texts_is_low():
    assert cosine_score("python django sql", "cooking recipes baking bread") < 0.3


def test_cosine_empty_text_is_zero():
    assert cosine_score("", "python django") == 0.0


def test_skill_match_score():
    assert skill_match_score(["Python", "Django"], ["Python", "Django", "SQL"]) == pytest.approx(2 / 3)
    assert skill_match_score([], ["Python"]) == 0.0
    assert skill_match_score(["Python"], []) == 1.0


def test_experience_fit():
    assert experience_fit_score(5.0, 3.0) == 1.0
    assert experience_fit_score(1.0, 4.0) == pytest.approx(0.25)
    assert experience_fit_score(None, 3.0) == 0.5
    assert experience_fit_score(2.0, None) == 1.0


def test_match_score_strong_beats_weak():
    strong = match_score(STRONG_CV, PYTHON_JOB)
    weak = match_score(WEAK_CV, PYTHON_JOB)
    assert 0 <= strong.score <= 100
    assert 0 <= weak.score <= 100
    assert strong.score > weak.score
    assert strong.score >= 60
    assert "Django" in strong.matched_skills
    assert "Flask" in strong.matched_skills


def test_match_score_missing_skills():
    result = match_score(WEAK_CV, PYTHON_JOB)
    assert "Django" in result.missing_skills
    assert "SQL" in result.missing_skills
    assert missing_skills(WEAK_CV.skills, PYTHON_JOB.required_skills) == result.missing_skills


def test_score_breakdown_adds_up():
    result = match_score(STRONG_CV, PYTHON_JOB)
    parts = result.breakdown
    total = sum(parts[k]["points"] for k in ("text similarity", "skill match", "experience fit"))
    assert total == pytest.approx(result.score, abs=0.2)
    lines = breakdown_lines(result)
    assert any("Total:" in line for line in lines)


def test_score_labels():
    assert score_label(85) == "Excellent match"
    assert score_label(65) == "Good match"
    assert score_label(45) == "Fair match"
    assert score_label(25) == "Weak match"
    assert score_label(5) == "Poor match"


def test_keyword_overlap():
    overlap = keyword_overlap("python django sql", "python django flask")
    assert 0 < overlap < 1
    details = match_details(match_score(STRONG_CV, PYTHON_JOB))
    assert details["matched_count"] > 0
    assert details["keyword_overlap"] > 0


def test_skill_gap_report():
    report = skill_gap_report(STRONG_CV, PYTHON_JOB)
    assert "required skills are present" in report.lower()
    weak_report = skill_gap_report(WEAK_CV, PYTHON_JOB)
    assert "Missing" in weak_report
