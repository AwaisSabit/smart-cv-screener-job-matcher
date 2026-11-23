"""Demo: screen the fictional sample CVs against the Python job.

Run from the project root:  python examples/demo.py

Writes the screening report, results CSV/JSON and shortlist to
examples/output/. All people and companies are fictional.
"""

from pathlib import Path

from cvmatch.batch import screen_folder_to_files
from cvmatch.parse import parse_cv, parse_job
from cvmatch.rank import rank_cvs
from cvmatch.score import match_score

ROOT = Path(__file__).resolve().parent
SAMPLES = ROOT / "samples"
OUTPUT = ROOT / "output"


def main():
    job = parse_job(SAMPLES / "job-python-developer.txt")
    cv = parse_cv(SAMPLES / "cv-ayesha-khan.txt")

    print("=== One CV against one job ===")
    result = match_score(cv, job)
    print(f"{result.cv_name} scores {result.score}/100 against {result.job_title}")
    print(f"Matched skills: {', '.join(result.matched_skills)}")
    print(f"Missing skills: {', '.join(result.missing_skills) or 'none'}")
    print()

    print("=== Ranking all sample CVs ===")
    cvs = [parse_cv(p) for p in sorted(SAMPLES.glob("cv-*.txt"))]
    ranked = rank_cvs(cvs, job)
    for rank, item in enumerate(ranked, 1):
        print(f"{rank}. {item.cv_name} — {item.score}/100")
    print()

    print("=== Batch screen (threshold 60) ===")
    paths = screen_folder_to_files(SAMPLES, SAMPLES / "job-python-developer.txt", OUTPUT)
    print(f"Screened {paths['screened']} CVs: {paths['shortlisted']} shortlisted")
    for key in ("report_txt", "report_md", "results_csv", "results_json", "shortlist_csv"):
        print(f"  {key}: {paths[key]}")


if __name__ == "__main__":
    main()
