"""Data models for CVMatch."""

from dataclasses import dataclass, field


@dataclass
class CV:
    """One candidate's CV, parsed from a file."""

    name: str = ""
    source: str = ""
    raw_text: str = ""
    skills: list = field(default_factory=list)
    years_experience: float | None = None
    degree_level: str = ""


@dataclass
class Job:
    """One job description, parsed from a file or text."""

    title: str = ""
    source: str = ""
    raw_text: str = ""
    required_skills: list = field(default_factory=list)
    min_experience: float | None = None


@dataclass
class MatchResult:
    """The match between one CV and one job."""

    cv_name: str
    job_title: str
    score: float
    similarity: float = 0.0
    skill_score: float = 0.0
    experience_score: float = 0.0
    matched_skills: list = field(default_factory=list)
    missing_skills: list = field(default_factory=list)
    keyword_overlap: float = 0.0
    breakdown: dict = field(default_factory=dict)
