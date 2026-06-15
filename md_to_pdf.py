"""
Conversion ACADEMIQ_V3_CahierDesCharges_BDD.md → PDF
Utilise: markdown (md→HTML) + xhtml2pdf (HTML→PDF)
"""
import sys
import os
import markdown
from xhtml2pdf import pisa

MD_FILE  = "ACADEMIQ_V3_CahierDesCharges_BDD.md"
PDF_FILE = "ACADEMIQ_V3_CahierDesCharges_BDD.pdf"

CSS = """
@page {
    size: A4;
    margin: 2cm 2.2cm 2.5cm 2.2cm;
}

body {
    font-family: "DejaVu Sans", Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #1a1a1a;
}

h1 {
    font-size: 22pt;
    color: #1a3a5c;
    text-align: center;
    margin-bottom: 4pt;
    border-bottom: 2pt solid #1a3a5c;
    padding-bottom: 6pt;
}

h2 {
    font-size: 15pt;
    color: #1a3a5c;
    border-bottom: 1pt solid #b0c4de;
    padding-bottom: 3pt;
    margin-top: 18pt;
    page-break-before: auto;
}

h3 {
    font-size: 12pt;
    color: #2c5282;
    margin-top: 12pt;
}

h4 {
    font-size: 11pt;
    color: #2d3748;
    margin-top: 8pt;
}

p {
    margin: 4pt 0 6pt 0;
    text-align: justify;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 8.5pt;
    margin: 8pt 0 10pt 0;
}

th {
    background-color: #1a3a5c;
    color: white;
    padding: 4pt 6pt;
    text-align: left;
    font-weight: bold;
}

td {
    padding: 3pt 6pt;
    border-bottom: 0.5pt solid #d0d8e4;
    border-right: 0.5pt solid #e8ecf0;
    vertical-align: top;
}

tr:nth-child(even) td {
    background-color: #f5f8fc;
}

code {
    background-color: #f0f4f8;
    font-family: "DejaVu Sans Mono", "Courier New", monospace;
    font-size: 8pt;
    padding: 1pt 3pt;
    border-radius: 2pt;
}

pre {
    background-color: #f0f4f8;
    border: 0.5pt solid #c8d4e0;
    border-left: 3pt solid #1a3a5c;
    padding: 8pt 10pt;
    font-size: 7.5pt;
    font-family: "DejaVu Sans Mono", "Courier New", monospace;
    white-space: pre-wrap;
    word-wrap: break-word;
    margin: 6pt 0;
    line-height: 1.4;
}

pre code {
    background: none;
    padding: 0;
    border: none;
}

blockquote {
    border-left: 3pt solid #4a90d9;
    background-color: #f0f6ff;
    margin: 6pt 0;
    padding: 4pt 10pt;
    font-style: italic;
    color: #2c4a6e;
}

ul, ol {
    margin: 4pt 0 4pt 16pt;
    padding-left: 6pt;
}

li {
    margin: 2pt 0;
}

strong {
    color: #1a1a1a;
    font-weight: bold;
}

em {
    color: #444;
}

hr {
    border: none;
    border-top: 1pt solid #b0c4de;
    margin: 12pt 0;
}

a {
    color: #1a3a5c;
    text-decoration: none;
}
"""

def convert():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    md_path  = os.path.join(base_dir, MD_FILE)
    pdf_path = os.path.join(base_dir, PDF_FILE)

    print(f"Lecture de : {md_path}")
    with open(md_path, encoding="utf-8") as f:
        md_text = f.read()

    print("Conversion Markdown -> HTML...")
    extensions = ["tables", "fenced_code", "codehilite", "toc", "nl2br", "sane_lists"]
    html_body = markdown.markdown(md_text, extensions=extensions)

    html_doc = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<style>
{CSS}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    print(f"Génération PDF : {pdf_path}")
    with open(pdf_path, "wb") as pdf_out:
        result = pisa.CreatePDF(html_doc, dest=pdf_out, encoding="utf-8")

    if result.err:
        print(f"ERREUR xhtml2pdf : {result.err}", file=sys.stderr)
        sys.exit(1)
    else:
        size_kb = os.path.getsize(pdf_path) // 1024
        print(f"PDF généré avec succès : {PDF_FILE}  ({size_kb} Ko)")

if __name__ == "__main__":
    convert()
