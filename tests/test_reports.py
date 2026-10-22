import csv
import pytest
from pypdf import PdfReader
from app.reports.export import snapshot,write_pdf,write_csv,report_html


@pytest.mark.parametrize("kind",["assessment","register","plan"])
def test_pdf_reports_embed_uzbek_text(qapp,populated,tmp_path,kind):
    path=write_pdf(tmp_path/f"{kind}.pdf",snapshot(populated),kind,1 if kind=="plan" else None)
    reader=PdfReader(path)
    text="\n".join(p.extract_text() for p in reader.pages)
    assert len(reader.pages)>=1
    assert "NAMUNA" in text and "Metodologiya" in text
    assert "o‘" in text or "g‘" in text
    assert "20" in text and "0.30" in text
    if kind!="plan":assert "80.00" in text
    else:assert "Hodisani" in text
    assert path.stat().st_size>5000


def test_csv_unicode_and_formula_protection(populated,tmp_path):
    s=populated
    p=s.repo.get("business_process",1);p.pop("id");p["name"]="=HYPERLINK(bad)";s.save("business_process",p,1)
    path=write_csv(tmp_path/"register.csv",snapshot(s))
    assert path.read_bytes().startswith(b"\xef\xbb\xbf")
    rows=list(csv.reader(path.open(encoding="utf-8-sig")))
    assert any("'=HYPERLINK(bad)" in row for row in rows)
    assert any("80.0" in row for row in rows)
    assert any("Kritik" in row for row in rows)
    assert any("Metodologiya" in row for row in rows)


def test_report_html_escapes_fields(populated):
    data=snapshot(populated)
    data["organization"]["name"]="<script>alert(1)</script>"
    html=report_html(data)
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "password_hash" not in html and "salt" not in data


def test_csv_metadata_is_formula_safe(populated,tmp_path):
    data=snapshot(populated)
    data["organization"]["name"]="=2+2"
    path=write_csv(tmp_path/"metadata.csv",data)
    with path.open(encoding="utf-8-sig",newline="") as handle:
        assert next(csv.reader(handle))[1]=="'=2+2"


def test_empty_reports_are_meaningful(qapp,service,tmp_path):
    write_pdf(tmp_path/"empty.pdf",snapshot(service))
    text=" ".join(" ".join(page.extract_text() for page in PdfReader(tmp_path/"empty.pdf").pages).split())
    assert "mavjud emas" in text
