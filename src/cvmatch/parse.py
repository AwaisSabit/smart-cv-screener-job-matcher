"""Read CVs from files.

Supported formats grow with the project: text files first, then PDF
and Word. Each reader returns plain text; :func:`parse_cv` wraps it
in a :class:`~cvmatch.models.CV`.
"""

from pathlib import Path

from cvmatch.models import CV

SUPPORTED_SUFFIXES = {".txt", ".pdf", ".docx"}


def read_text_file(path):
    """Read a plain-text CV file and return its text."""
    return Path(path).read_text(encoding="utf-8", errors="replace")


def read_pdf_file(path):
    """Read a PDF CV and return its text, page by page.

    Scanned PDFs (pictures of text) have no extractable text, so they
    come back empty — the README says so plainly.
    """
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def guess_name(text, source):
    """Guess the candidate's name from the first non-empty line.

    Falls back to the file name (without extension) when the text is
    empty or the first line looks like a heading.
    """
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower() in {"curriculum vitae", "cv", "resume"}:
            continue
        words = line.split()
        if 1 <= len(words) <= 4 and all(w[0].isupper() for w in words if w):
            return line
        return line
    return Path(source).stem.replace("_", " ").replace("-", " ").title()


def parse_cv(path):
    """Parse a CV file into a :class:`~cvmatch.models.CV`.

    Only ``.txt`` files are supported yet; PDF and Word support is
    added in later commits.
    """
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".txt":
        text = read_text_file(path)
    elif suffix == ".pdf":
        text = read_pdf_file(path)
    elif suffix == ".docx":
        raise NotImplementedError(
            ".docx CV parsing is not built yet — use a .txt or .pdf CV for now"
        )
    else:
        raise ValueError(f"Unsupported CV file type: {suffix or '(no extension)'}")
    return CV(name=guess_name(text, str(path)), source=str(path), raw_text=text)
