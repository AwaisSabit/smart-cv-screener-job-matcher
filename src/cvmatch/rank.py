"""Rank CVs against jobs, and jobs against CVs.

Ranking reuses the same TF-IDF space for every CV in a run, so the
scores are comparable with each other.
"""

from cvmatch.extract import enrich_cv, enrich_job
from cvmatch.score import (
    experience_fit_score,
    keyword_overlap,
    skill_match_score,
)
from cvmatch.vectorise import vectorise_many
from sklearn.metrics.pairwise import cosine_similarity


def _score_from_parts(cv, job, similarity):
    """Combine one similarity value with skill and experience parts."""
    from cvmatch.models import MatchResult

    skill_score = skill_match_score(cv.skills, job.required_skills)
    experience = experience_fit_score(cv.years_experience, job.min_experience)
    score = round(50 * similarity + 35 * skill_score + 15 * experience, 1)
    matched = [s for s in job.required_skills if s in cv.skills]
    missing = [s for s in job.required_skills if s not in cv.skills]
    result = MatchResult(
        cv_name=cv.name,
        job_title=job.title,
        score=score,
        similarity=round(float(similarity), 3),
        skill_score=round(skill_score, 3),
        experience_score=round(experience, 3),
        matched_skills=matched,
        missing_skills=missing,
        keyword_overlap=round(keyword_overlap(cv.raw_text, job.raw_text), 3),
    )
    from cvmatch.score import score_breakdown

    result.breakdown = score_breakdown(result)
    return result


def rank_cvs(cvs, job, top_n=None):
    """Rank CVs against one job, best score first.

    Returns a list of :class:`~cvmatch.models.MatchResult`, sorted by
    score descending (ties broken by skill score, then by name).
    """
    for cv in cvs:
        enrich_cv(cv)
    enrich_job(job)
    texts = [cv.raw_text for cv in cvs]
    if not any(t.strip() for t in texts) or not job.raw_text.strip():
        similarities = [0.0] * len(cvs)
    else:
        cv_vectors, job_vector, _ = vectorise_many(texts, job.raw_text)
        similarities = cosine_similarity(cv_vectors, job_vector).flatten()
    results = [
        _score_from_parts(cv, job, float(sim)) for cv, sim in zip(cvs, similarities)
    ]
    results.sort(key=lambda r: (-r.score, -r.skill_score, r.cv_name))
    return results[:top_n] if top_n else results
