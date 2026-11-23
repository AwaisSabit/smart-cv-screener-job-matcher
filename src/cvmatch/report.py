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
