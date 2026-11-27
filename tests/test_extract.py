"""Tests for text cleaning, skill extraction and experience/degree."""

from cvmatch.clean import clean_text, keywords, tokenise
from cvmatch.extract import (
    enrich_cv,
    enrich_job,
    extract_degree_level,
    extract_degree_name,
    extract_education,
    extract_skills,
    extract_years_experience,
    experience_from_dates,
)
from cvmatch.models import CV, Job


def test_clean_text_lowercases_and_collapses():
    assert clean_text("  Hello   WORLD\n") == "hello world"


def test_tokenise_drops_stop_words_and_numbers():
    tokens = tokenise("I have 5 years of Python and Django experience")
    assert "python" in tokens
    assert "django" in tokens
    assert "5" not in tokens
    assert "i" not in tokens


def test_keywords_returns_frequent_words():
    words = keywords("Python Python Django SQL Python")
    assert words[0] == "python"


def test_extract_skills_finds_known_skills():
    skills = extract_skills("I work with Python, Django and SQL every day.")
    assert "Python" in skills
    assert "Django" in skills
    assert "SQL" in skills


def test_extract_skills_does_not_match_java_inside_javascript():
    skills = extract_skills("I write JavaScript and React.")
    assert "JavaScript" in skills
    assert "Java" not in skills


def test_extract_skills_covers_soft_and_business_skills():
    skills = extract_skills("Good communication, leadership and SEO experience.")
    assert "Communication" in skills
    assert "Leadership" in skills
    assert "SEO" in skills


def test_experience_from_phrase():
    assert extract_years_experience("5 years of experience in Python") == 5.0
    assert extract_years_experience("No experience mentioned") is None


def test_experience_from_dates():
    assert experience_from_dates("Software Engineer, 2020 - 2024") == 4.0
    assert experience_from_dates("Developer, 2019 to present") == 7.0
    assert experience_from_dates("No dates here") is None


def test_degree_level_and_name():
    text = "BS Computer Science, University of the Punjab, 2019"
    assert extract_degree_level(text) == "Bachelor's"
    assert extract_degree_name(text) == "BS Computer Science"
    assert extract_degree_level("MBA Marketing, 2018") == "Master's"


def test_bba_degree_level_and_name():
    # BBA is a Bachelor's degree: the old pattern only matched the
    # whole word "BA", so a BBA CV came back with no degree level.
    assert extract_degree_level("BBA, University of Karachi, 2020") == "Bachelor's"
    assert extract_degree_name("BBA, University of Karachi, 2020") == "BBA"
    edu = extract_education("BBA, University of Karachi, 2020")
    assert edu["level"] == "Bachelor's"
    assert edu["degree"] == "BBA"
    assert edu["years"] == [2020]


def test_education_dict():
    edu = extract_education("MBA Marketing, 2018")
    assert edu["level"] == "Master's"
    assert edu["degree"] == "MBA"
    assert edu["years"] == [2018]


def test_enrich_cv_fills_everything():
    cv = enrich_cv(CV(name="Test", raw_text="Sara, 6 years of experience. SEO, digital marketing. MBA, 2018."))
    assert "SEO" in cv.skills
    assert cv.years_experience == 6.0
    assert cv.degree_level == "Master's"


def test_enrich_job_fills_skills_and_minimum():
    job = enrich_job(Job(title="Dev", raw_text="Need Django and SQL. 3 years of experience required."))
    assert "Django" in job.required_skills
    assert job.min_experience == 3.0
