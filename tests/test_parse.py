"""Tests for CV and job parsing (txt, PDF, Word)."""

from pathlib import Path

import pytest

from cvmatch.parse import parse_cv, parse_job

SAMPLES = Path(__file__).resolve().parent.parent / "examples" / "samples"

STRONG_CV = """Ayesha Khan
Python Developer with 5 years of experience.
Django, Flask, SQL, REST API, Git, Docker, AWS.
BS Computer Science, 2019.
"""


def test_parse_txt_cv(tmp_path):
    path = tmp_path / "cv.txt"
    path.write_text(STRONG_CV, encoding="utf-8")
    cv = parse_cv(path)
    assert cv.name == "Ayesha Khan"
    assert "Django" in cv.raw_text


def test_parse_pdf_cv():
    cv = parse_cv(SAMPLES / "cv-ayesha-khan.pdf")
    assert cv.name == "Ayesha Khan"
    assert "Django" in cv.raw_text


def test_parse_docx_cv(tmp_path):
    from docx import Document

    path = tmp_path / "cv.docx"
    document = Document()
    document.add_paragraph("Bilal Ahmed")
    document.add_paragraph("Data Analyst with 4 years of experience. Excel, SQL, Power BI.")
    document.save(str(path))
    cv = parse_cv(path)
    assert cv.name == "Bilal Ahmed"
    assert "Power BI" in cv.raw_text


def test_parse_docx_sample():
    cv = parse_cv(SAMPLES / "cv-bilal-ahmed.docx")
    assert cv.name == "Bilal Ahmed"


def test_unsupported_file_type(tmp_path):
    path = tmp_path / "cv.rtf"
    path.write_text("hello", encoding="utf-8")
    with pytest.raises(ValueError):
        parse_cv(path)


def test_parse_job_txt(tmp_path):
    path = tmp_path / "job.txt"
    path.write_text(
        "Python Developer\nWe need Django, SQL and REST API skills. "
        "3 years of experience required.",
        encoding="utf-8",
    )
    job = parse_job(path)
    assert job.title == "Python Developer"
    assert "Django" in job.raw_text
