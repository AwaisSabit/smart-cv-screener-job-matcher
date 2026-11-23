"""Screening reports in plain text and Markdown."""

from cvmatch.score import breakdown_lines, match_details_lines, score_label


def text_report(job, results, threshold=None):
    """A plain-text screening report for a job and its ranked results."""
    lines = [
        f"Screening report — {job.title}",
        "=" * 60,
        f"Candidates screened: {len(results)}",
    ]
    if threshold is not None:
        kept = sum(1 for r in results if r.score >= threshold)
        lines.append(f"Shortlist threshold: {threshold} — {kept} shortlisted")
    lines.append("")
    for rank, result in enumerate(results, 1):
        lines.append(
            f"{rank}. {result.cv_name} — {result.score}/100 "
            f"({score_label(result.score)})"
        )
        for line in breakdown_lines(result):
            lines.append(f"   {line}")
        for line in match_details_lines(result):
            lines.append(f"   {line}")
        lines.append("")
    lines.append(
        "Note: scores are keyword-based TF-IDF matches. A high score "
        "does not mean a good hire — read the shortlisted CVs yourself."
    )
    return "\n".join(lines)


def markdown_report(job, results, threshold=None):
    """A Markdown screening report for a job and its ranked results."""
    lines = [f"# Screening report — {job.title}", ""]
    lines.append(f"- Candidates screened: {len(results)}")
    if threshold is not None:
        kept = sum(1 for r in results if r.score >= threshold)
        lines.append(f"- Shortlist threshold: {threshold} — {kept} shortlisted")
    lines.append("")
    lines.append("| Rank | Candidate | Score | Verdict | Matched skills | Missing skills |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for rank, result in enumerate(results, 1):
        lines.append(
            f"| {rank} | {result.cv_name} | {result.score} | "
            f"{score_label(result.score)} | "
            f"{', '.join(result.matched_skills) or '—'} | "
            f"{', '.join(result.missing_skills) or '—'} |"
        )
    lines.append("")
    for rank, result in enumerate(results, 1):
        lines.append(f"## {rank}. {result.cv_name} — {result.score}/100")
        lines.append("")
        for line in breakdown_lines(result):
            lines.append(f"- {line}")
        for line in match_details_lines(result):
            lines.append(f"- {line}")
        lines.append("")
    lines.append(
        "> Note: scores are keyword-based TF-IDF matches. A high score "
        "does not mean a good hire — read the shortlisted CVs yourself."
    )
    return "\n".join(lines)


def write_report(path, content):
    """Write report text to a file and return the path."""
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
    return str(path)


def results_to_rows(results):
    """Turn match results into plain dicts for CSV/JSON export."""
    rows = []
    for rank, result in enumerate(results, 1):
        rows.append(
            {
                "rank": rank,
                "candidate": result.cv_name,
                "job": result.job_title,
                "score": result.score,
                "verdict": score_label(result.score),
                "similarity": result.similarity,
                "skill_score": result.skill_score,
                "experience_score": result.experience_score,
                "matched_skills": "; ".join(result.matched_skills),
                "missing_skills": "; ".join(result.missing_skills),
                "keyword_overlap": result.keyword_overlap,
            }
        )
    return rows


def save_results_csv(path, results):
    """Save match results to a CSV file and return the path."""
    import csv

    rows = results_to_rows(results)
    fieldnames = list(rows[0].keys()) if rows else [
        "rank", "candidate", "job", "score", "verdict", "similarity",
        "skill_score", "experience_score", "matched_skills",
        "missing_skills", "keyword_overlap",
    ]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def save_results_json(path, results):
    """Save match results to a JSON file and return the path."""
    import json

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(results_to_rows(results), handle, indent=2)
    return str(path)


def save_shortlist_csv(path, results, threshold=60.0):
    """Save only the shortlisted results (score >= threshold) to CSV.

    Returns ``(path, shortlisted_count)``.
    """
    from cvmatch.rank import shortlist

    shortlisted, _ = shortlist(results, threshold=threshold)
    save_results_csv(path, shortlisted)
    return str(path), len(shortlisted)
