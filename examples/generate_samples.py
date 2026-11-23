"""Generate PDF and Word versions of the fictional sample CVs.

Run from the project root:  python examples/generate_samples.py

Reads the .txt samples in examples/samples/ and writes a .pdf and a
.docx copy of each CV, so the demo can show all three formats. The
people are fictional; the script only copies the text files.
"""

from pathlib import Path

SAMPLES = Path(__file__).resolve().parent / "samples"


def make_pdf(text_path, pdf_path):
    """Write a simple one-page PDF with the CV text, using pypdf-free
    reportlab-free approach: build the PDF by hand is fragile, so we
    use pypdf's writer with a minimal content stream via fpdf-free
    raw PDF — instead, use the `pypdf` writer only for structure and
    draw text with a tiny hand-written PDF writer below.
    """
    # Minimal PDF writer: one page, Helvetica, plain text lines.
    lines = text_path.read_text(encoding="utf-8").splitlines()
    content_lines = []
    y = 750
    for line in lines:
        safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content_lines.append(f"BT /F1 11 Tf 50 {y} Td ({safe}) Tj ET")
        y -= 16
    content = "\n".join(content_lines).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n"
        + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_pos = len(pdf)
    pdf += f"xref\n0 {len(objects) + 1}\n".encode()
    pdf += b"0000000000 65535 f \n"
    for off in offsets:
        pdf += f"{off:010d} 00000 n \n".encode()
    pdf += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode()
    pdf_path.write_bytes(bytes(pdf))


def make_docx(text_path, docx_path):
    """Write a .docx copy of a text CV."""
    from docx import Document

    document = Document()
    for line in text_path.read_text(encoding="utf-8").splitlines():
        document.add_paragraph(line)
    document.save(str(docx_path))


def main():
    made = []
    for txt in sorted(SAMPLES.glob("cv-*.txt")):
        pdf_path = txt.with_suffix(".pdf")
        docx_path = txt.with_suffix(".docx")
        make_pdf(txt, pdf_path)
        make_docx(txt, docx_path)
        made.append((txt.name, pdf_path.name, docx_path.name))
    for name, pdf, docx in made:
        print(f"{name} -> {pdf}, {docx}")
    print(f"Generated {len(made)} PDF and {len(made)} Word CVs.")


if __name__ == "__main__":
    main()
