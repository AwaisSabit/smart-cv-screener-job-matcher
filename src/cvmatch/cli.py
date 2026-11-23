"""Command line interface for CVMatch.

Subcommands:
    parse   show what was read from one CV
    match   score one CV against one job
    rank    rank CVs in a folder against one job
    screen  screen a folder and write a report
    batch   batch-screen a folder and save CSV/JSON results
"""

import argparse
import sys

from cvmatch.batch import find_cv_files, screen_folder, screen_folder_to_files
from cvmatch.extract import enrich_cv, enrich_job, extract_education
from cvmatch.parse import parse_cv, parse_job
from cvmatch.rank import rank_cvs, rank_jobs, shortlist
from cvmatch.report import markdown_report, text_report, write_report
from cvmatch.score import breakdown_lines, match_details_lines, match_score, score_summary


def _print_result(result):
    print(score_summary(result))
    for line in breakdown_lines(result):
        print(f"  {line}")
    for line in match_details_lines(result):
        print(f"  {line}")


def cmd_parse(args):
    cv = parse_cv(args.cv)
    enrich_cv(cv)
    print(f"Candidate: {cv.name}")
    print(f"Source: {cv.source}")
    print(f"Skills ({len(cv.skills)}): {', '.join(cv.skills) or 'none found'}")
    print(f"Experience: {cv.years_experience if cv.years_experience is not None else 'not stated'} years")
    print(f"Degree: {extract_education(cv.raw_text)['degree'] or cv.degree_level or 'not stated'}")
    return 0


def cmd_match(args):
    cv = parse_cv(args.cv)
    job = parse_job(args.job)
    result = match_score(cv, job)
    _print_result(result)
    return 0


def cmd_rank(args):
    job = parse_job(args.job)
    if args.jobs:
        cv = parse_cv(args.cv)
        jobs = [parse_job(path) for path in args.jobs]
        results = rank_jobs(cv, jobs, top_n=args.top)
        print(f"Jobs ranked for {cv.name}:")
        for rank, result in enumerate(results, 1):
            print(f"  {rank}. {result.job_title} — {result.score}/100")
        return 0
    cvs = [parse_cv(path) for path in find_cv_files(args.folder)]
    results = rank_cvs(cvs, job, top_n=args.top)
    print(f"CVs ranked for {job.title}:")
    for rank, result in enumerate(results, 1):
        print(f"  {rank}. {result.cv_name} — {result.score}/100")
    return 0


def cmd_screen(args):
    job = parse_job(args.job)
    ranked, shortlisted, rejected = screen_folder(args.folder, args.job, threshold=args.threshold)
    content = markdown_report(job, ranked, args.threshold) if args.format == "md" else text_report(job, ranked, args.threshold)
    if args.report:
        write_report(args.report, content)
        print(f"Report written to {args.report}")
    else:
        print(content)
    print(f"\nShortlisted ({len(shortlisted)}): {', '.join(r.cv_name for r in shortlisted) or 'none'}")
    print(f"Rejected ({len(rejected)}): {', '.join(r.cv_name for r in rejected) or 'none'}")
    return 0


def cmd_batch(args):
    paths = screen_folder_to_files(args.folder, args.job, args.output_dir, threshold=args.threshold)
    print(f"Screened {paths['screened']} CVs: {paths['shortlisted']} shortlisted, {paths['rejected']} rejected")
    for key in ("report_txt", "report_md", "results_csv", "results_json", "shortlist_csv"):
        print(f"  {key}: {paths[key]}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="cvmatch", description="Smart CV Screener and Job Matcher")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("parse", help="Show what was read from one CV")
    p.add_argument("cv", help="CV file (.txt, .pdf or .docx)")
    p.set_defaults(func=cmd_parse)

    p = sub.add_parser("match", help="Score one CV against one job")
    p.add_argument("cv", help="CV file")
    p.add_argument("job", help="Job description file")
    p.set_defaults(func=cmd_match)

    p = sub.add_parser("rank", help="Rank CVs against a job, or jobs against a CV")
    p.add_argument("folder", help="Folder of CV files")
    p.add_argument("job", help="Job description file")
    p.add_argument("--cv", help="Rank jobs against this CV instead")
    p.add_argument("--jobs", nargs="+", help="Job files to rank against the CV")
    p.add_argument("--top", type=int, default=None, help="Show only the top N")
    p.set_defaults(func=cmd_rank)

    p = sub.add_parser("screen", help="Screen a folder and write a report")
    p.add_argument("folder", help="Folder of CV files")
    p.add_argument("job", help="Job description file")
    p.add_argument("--threshold", type=float, default=60.0, help="Shortlist score threshold (default 60)")
    p.add_argument("--format", choices=["txt", "md"], default="txt", help="Report format")
    p.add_argument("--report", help="Write the report to this file")
    p.set_defaults(func=cmd_screen)

    p = sub.add_parser("batch", help="Batch-screen a folder and save results")
    p.add_argument("folder", help="Folder of CV files")
    p.add_argument("job", help="Job description file")
    p.add_argument("--output-dir", default="output", help="Folder for report, CSV and JSON")
    p.add_argument("--threshold", type=float, default=60.0, help="Shortlist score threshold (default 60)")
    p.set_defaults(func=cmd_batch)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError, NotImplementedError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
