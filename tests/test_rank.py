"""Tests for ranking, shortlisting, reports and batch screening."""

from pathlib import Path

from cvmatch.batch import find_cv_files, screen_folder, screen_folder_to_files
from cvmatch.extract import enrich_cv
from cvmatch.models import CV, Job
from cvmatch.rank import rank_cvs, rank_jobs, shortlist, shortlist_cvs
from cvmatch.report import (
    markdown_report,
    save_results_csv,
    save_results_json,
    save_shortlist_csv,
    text_report,
)
from cvmatch.score import match_score

SAMPLES = Path(__file__).resolve().parent.parent / "examples" / "samples"


def _cv(name, text):
    return CV(name=name, raw_text=text)


def _python_job():
    return Job(
        title="Python Developer",
        raw_text=(
            "Python Developer. Need Django, Flask, SQL, REST API and Git. "
            "3 years of experience in Python development required."
        ),
    )


STRONG = _cv(
    "Ayesha Khan",
    "Python Developer with 5 years of experience. Django, Flask, SQL, "
    "REST API, Git, Docker, AWS. BS Computer Science.",
)
MID = _cv(
    "Bilal Ahmed",
    "Data Analyst with 4 years of experience. Excel, SQL, Power BI, "
    "pandas, Python. BBA.",
)
WEAK = _cv(
    "Usman Raza",
    "Fresh graduate. Basic Python and HTML. BS Computer Science, 2025.",
)


def test_rank_cvs_orders_best_first():
    ranked = rank_cvs([WEAK, MID, STRONG], _python_job())
    assert [r.cv_name for r in ranked] == ["Ayesha Khan", "Bilal Ahmed", "Usman Raza"]
    assert ranked[0].score > ranked[-1].score


def test_rank_cvs_top_n():
    ranked = rank_cvs([WEAK, MID, STRONG], _python_job(), top_n=2)
    assert len(ranked) == 2
    assert ranked[0].cv_name == "Ayesha Khan"


def test_rank_jobs_orders_best_first():
    python_job = _python_job()
    analyst_job = Job(
        title="Data Analyst",
        raw_text="Data Analyst. Need Excel, SQL, Power BI, pandas. 2 years of experience.",
    )
    ranked = rank_jobs(MID, [python_job, analyst_job])
    assert ranked[0].job_title == "Data Analyst"


def test_shortlist_threshold():
    ranked = rank_cvs([WEAK, MID, STRONG], _python_job())
    kept, dropped = shortlist(ranked, threshold=60.0)
    assert all(r.score >= 60.0 for r in kept)
    assert all(r.score < 60.0 for r in dropped)
    assert len(kept) + len(dropped) == 3
    assert shortlist_cvs([WEAK, MID, STRONG], _python_job(), threshold=60.0) == kept


def test_text_and_markdown_reports(tmp_path):
    ranked = rank_cvs([WEAK, MID, STRONG], _python_job())
    job = _python_job()
    text = text_report(job, ranked, threshold=60.0)
    assert "Ayesha Khan" in text
    assert "Screening report" in text
    markdown = markdown_report(job, ranked, threshold=60.0)
    assert markdown.startswith("# Screening report")
    assert "| Ayesha Khan |" in markdown


def test_save_results_csv_and_json(tmp_path):
    ranked = rank_cvs([WEAK, MID, STRONG], _python_job())
    csv_path = save_results_csv(tmp_path / "results.csv", ranked)
    assert "Ayesha Khan" in Path(csv_path).read_text(encoding="utf-8")
    json_path = save_results_json(tmp_path / "results.json", ranked)
    assert "Ayesha Khan" in Path(json_path).read_text(encoding="utf-8")
    shortlist_path, kept = save_shortlist_csv(tmp_path / "short.csv", ranked, threshold=60.0)
    assert kept == len([r for r in ranked if r.score >= 60.0])
    assert "Usman Raza" not in Path(shortlist_path).read_text(encoding="utf-8")


def test_find_cv_files_dedupes_formats(tmp_path):
    for suffix in (".txt", ".pdf", ".docx"):
        (tmp_path / f"cv-same{suffix}").write_text("x", encoding="utf-8")
    (tmp_path / "cv-other.txt").write_text("x", encoding="utf-8")
    files = find_cv_files(tmp_path)
    assert len(files) == 2
    assert files[0].suffix == ".txt"


def test_screen_folder_on_samples():
    ranked, kept, dropped = screen_folder(SAMPLES, SAMPLES / "job-python-developer.txt", threshold=60.0)
    assert len(ranked) == 4
    assert ranked[0].cv_name == "Ayesha Khan"
    assert ranked[-1].cv_name == "Usman Raza"
    assert all(r.score >= 60.0 for r in kept)


def test_screen_folder_to_files(tmp_path):
    paths = screen_folder_to_files(SAMPLES, SAMPLES / "job-python-developer.txt", tmp_path / "out")
    assert paths["screened"] == 4
    assert paths["shortlisted"] >= 1
    assert Path(paths["report_md"]).exists()
    assert Path(paths["results_csv"]).exists()
    assert Path(paths["shortlist_csv"]).exists()


def test_match_score_is_not_hardcoded():
    job = _python_job()
    a = match_score(STRONG, job)
    b = match_score(_cv("Copy", STRONG.raw_text.replace("Django", "Cooking")), job)
    assert a.score != b.score


def test_rank_fixtures_all_have_degree_levels():
    # Bilal Ahmed's CV says "BBA." — before the fix his degree level
    # came back empty, so every fixture CV must enrich to a level.
    for cv in (STRONG, MID, WEAK):
        assert enrich_cv(cv).degree_level, f"{cv.name} has no degree level"
    assert enrich_cv(MID).degree_level == "Bachelor's"
