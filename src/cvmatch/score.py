"""Score a CV against a job.

The headline score is 0–100 and combines three parts:

- text similarity (TF-IDF cosine similarity) — 50 points
- skill match (share of the job's required skills found) — 35 points
- experience fit (CV years vs the job's minimum) — 15 points

Every part is a real computed value; nothing is hardcoded.
"""

from sklearn.metrics.pairwise import cosine_similarity

from cvmatch.clean import tokenise
from cvmatch.extract import enrich_cv, enrich_job
from cvmatch.models import MatchResult
from cvmatch.vectorise import vectorise_pair


def cosine_score(cv_text, job_text):
    """Cosine similarity (0–1) between a CV and a job, via TF-IDF."""
    if not cv_text.strip() or not job_text.strip():
        return 0.0
    cv_vector, job_vector, _ = vectorise_pair(cv_text, job_text)
    return float(cosine_similarity(cv_vector, job_vector)[0][0])


def keyword_overlap(cv_text, job_text):
    """Share of the job's meaningful words that also appear in the CV."""
    job_words = set(tokenise(job_text))
    if not job_words:
        return 0.0
    cv_words = set(tokenise(cv_text))
    return len(job_words & cv_words) / len(job_words)


def skill_match_score(cv_skills, job_skills):
    """Share of the job's required skills found in the CV (0–1)."""
    if not job_skills:
        return 1.0
    matched = set(cv_skills) & set(job_skills)
    return len(matched) / len(job_skills)


def experience_fit_score(cv_years, min_years):
    """How well the CV's experience fits the job's minimum (0–1).

    Full marks at or above the minimum, partial marks below it, and
    full marks when the job states no minimum.
    """
    if min_years is None:
        return 1.0
    if cv_years is None:
        return 0.5
    if cv_years >= min_years:
        return 1.0
    if min_years <= 0:
        return 1.0
    return max(0.0, cv_years / min_years)


SCORE_BANDS = [
    (80, "Excellent match"),
    (60, "Good match"),
    (40, "Fair match"),
    (20, "Weak match"),
    (0, "Poor match"),
]


def score_label(score):
    """Plain-language band for a 0–100 score."""
    for threshold, label in SCORE_BANDS:
        if score >= threshold:
            return label
    return "Poor match"


def score_summary(result):
    """One-sentence summary of a match result, from its real numbers."""
    return (
        f"{result.cv_name} scores {result.score}/100 against "
        f"{result.job_title or 'the job'} ({score_label(result.score)}): "
        f"{len(result.matched_skills)} of "
        f"{len(result.matched_skills) + len(result.missing_skills)} required "
        f"skills matched."
    )


def score_breakdown(result):
    """Explain where a score comes from, in plain numbers.

    Returns a dict with each part's points out of its maximum, so a
    report can show the working instead of just the total.
    """
    return {
        "text similarity": {
            "value": result.similarity,
            "points": round(50 * result.similarity, 1),
            "max_points": 50,
        },
        "skill match": {
            "value": result.skill_score,
            "points": round(35 * result.skill_score, 1),
            "max_points": 35,
        },
        "experience fit": {
            "value": result.experience_score,
            "points": round(15 * result.experience_score, 1),
            "max_points": 15,
        },
        "total": {"value": result.score, "points": result.score, "max_points": 100},
    }


def breakdown_lines(result):
    """Human-readable lines explaining a result's score."""
    breakdown = score_breakdown(result)
    lines = []
    for name in ("text similarity", "skill match", "experience fit"):
        part = breakdown[name]
        lines.append(
            f"{name}: {part['points']} of {part['max_points']} points "
            f"(value {part['value']})"
        )
    lines.append(f"Total: {result.score} of 100 — {score_label(result.score)}")
    return lines


def missing_skills(cv_skills, job_skills):
    """Skills the job needs that the CV does not show, in job order."""
    cv_set = set(cv_skills)
    return [skill for skill in job_skills if skill not in cv_set]


def skill_gap_report(cv, job):
    """Plain-language summary of the skill gap between a CV and a job."""
    if not job.required_skills and job.raw_text:
        enrich_job(job)
    missing = missing_skills(cv.skills, job.required_skills)
    matched = [s for s in job.required_skills if s in cv.skills]
    if not job.required_skills:
        return "The job lists no required skills from the built-in list."
    if not missing:
        return f"All {len(matched)} required skills are present in the CV."
    return (
        f"{len(matched)} of {len(job.required_skills)} required skills "
        f"matched. Missing: {', '.join(missing)}."
    )


def match_score(cv, job):
    """Score one CV against one job and return a :class:`MatchResult`.

    The CV and job are enriched (skills, experience) if not already.
    """
    if not cv.skills:
        enrich_cv(cv)
    if not job.required_skills and job.raw_text:
        enrich_job(job)
    similarity = cosine_score(cv.raw_text, job.raw_text)
    skill_score = skill_match_score(cv.skills, job.required_skills)
    experience = experience_fit_score(cv.years_experience, job.min_experience)
    score = round(50 * similarity + 35 * skill_score + 15 * experience, 1)
    matched = [s for s in job.required_skills if s in cv.skills]
    missing = [s for s in job.required_skills if s not in cv.skills]
    overlap = keyword_overlap(cv.raw_text, job.raw_text)
    result = MatchResult(
        cv_name=cv.name,
        job_title=job.title,
        score=score,
        similarity=round(similarity, 3),
        skill_score=round(skill_score, 3),
        experience_score=round(experience, 3),
        matched_skills=matched,
        missing_skills=missing,
        keyword_overlap=round(overlap, 3),
    )
    result.breakdown = score_breakdown(result)
    return result
