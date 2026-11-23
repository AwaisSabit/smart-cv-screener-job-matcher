"""Batch-screen a whole folder of CVs against one job."""

from pathlib import Path

from cvmatch.parse import SUPPORTED_SUFFIXES, parse_cv, parse_job
from cvmatch.rank import rank_cvs, shortlist
from cvmatch.report import (
    markdown_report,
    save_results_csv,
    save_results_json,
    save_shortlist_csv,
    text_report,
    write_report,
)


def find_cv_files(folder):
    """List the CV files in a folder, sorted by name.

    When the same CV exists in several formats (.txt, .docx, .pdf),
    only one copy is kept — .txt first, then .docx, then .pdf — so
    one person is never screened three times.
    """
    folder = Path(folder)
    preference = {".txt": 0, ".docx": 1, ".pdf": 2}
    best = {}
    for path in folder.iterdir():
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        stem = path.stem.lower()
        if stem not in best or preference[path.suffix.lower()] < preference[best[stem].suffix.lower()]:
            best[stem] = path
    return sorted(best.values(), key=lambda p: p.name.lower())


def screen_folder(folder, job_path, threshold=60.0, top_n=None):
    """Screen every CV in a folder against one job.

    Returns ``(ranked_results, shortlisted, rejected)``.
    """
    job = parse_job(job_path)
    cvs = [parse_cv(path) for path in find_cv_files(folder)]
    if not cvs:
        raise ValueError(f"No CV files found in {folder}")
    ranked = rank_cvs(cvs, job, top_n=top_n)
    shortlisted, rejected = shortlist(ranked, threshold=threshold)
    return ranked, shortlisted, rejected


def screen_folder_to_files(folder, job_path, output_dir, threshold=60.0):
    """Screen a folder and write the report, CSV and JSON to output_dir.

    Returns a dict of the paths written and the counts.
    """
    from cvmatch.parse import parse_job as _parse_job

    job = _parse_job(job_path)
    ranked, shortlisted, rejected = screen_folder(folder, job_path, threshold=threshold)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "report_txt": write_report(output_dir / "report.txt", text_report(job, ranked, threshold)),
        "report_md": write_report(output_dir / "report.md", markdown_report(job, ranked, threshold)),
        "results_csv": save_results_csv(output_dir / "results.csv", ranked),
        "results_json": save_results_json(output_dir / "results.json", ranked),
    }
    shortlist_path, kept = save_shortlist_csv(
        output_dir / "shortlist.csv", ranked, threshold=threshold
    )
    paths["shortlist_csv"] = shortlist_path
    paths["screened"] = len(ranked)
    paths["shortlisted"] = kept
    paths["rejected"] = len(rejected)
    return paths
