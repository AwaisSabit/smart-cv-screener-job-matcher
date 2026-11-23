"""Tests for the cvmatch CLI, run as a real subprocess."""

import subprocess
import sys
from pathlib import Path

SAMPLES = Path(__file__).resolve().parent.parent / "examples" / "samples"


def run_cli(*args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "cvmatch", *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_cli_match_reports_real_score():
    result = run_cli(
        "match",
        str(SAMPLES / "cv-ayesha-khan.txt"),
        str(SAMPLES / "job-python-developer.txt"),
    )
    assert result.returncode == 0
    assert "Ayesha Khan" in result.stdout
    assert "scores" in result.stdout
    assert "Django" in result.stdout


def test_cli_rank_orders_candidates():
    result = run_cli(
        "rank", str(SAMPLES), str(SAMPLES / "job-python-developer.txt")
    )
    assert result.returncode == 0
    assert result.stdout.index("Ayesha Khan") < result.stdout.index("Usman Raza")


def test_cli_parse_shows_skills():
    result = run_cli("parse", str(SAMPLES / "cv-ayesha-khan.txt"))
    assert result.returncode == 0
    assert "Python" in result.stdout
    assert "5" in result.stdout


def test_cli_screen_writes_report(tmp_path):
    report = tmp_path / "report.md"
    result = run_cli(
        "screen",
        str(SAMPLES),
        str(SAMPLES / "job-python-developer.txt"),
        "--threshold", "60",
        "--format", "md",
        "--report", str(report),
    )
    assert result.returncode == 0
    assert report.exists()
    assert "Ayesha Khan" in report.read_text(encoding="utf-8")


def test_cli_batch_writes_outputs(tmp_path):
    out = tmp_path / "out"
    result = run_cli(
        "batch",
        str(SAMPLES),
        str(SAMPLES / "job-python-developer.txt"),
        "--output-dir", str(out),
    )
    assert result.returncode == 0
    assert (out / "results.csv").exists()
    assert (out / "shortlist.csv").exists()
    assert (out / "report.md").exists()


def test_cli_missing_file_is_an_error():
    result = run_cli("match", "no-such-cv.txt", str(SAMPLES / "job-python-developer.txt"))
    assert result.returncode == 1
    assert "Error" in result.stderr
