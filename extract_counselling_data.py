"""
Extract Maharashtra CAP cutoff PDFs (data/raw/*.pdf) into one tidy CSV.

Run from the repo root:
    pip install pdfplumber pandas
    python scripts/extract.py

Output: data/processed/cutoffs_all.csv  (one row per college x branch x category x stage)
Year and round are read from the file name, e.g. 2026ENGG_CAP1_MH_CutOff_V1.pdf
"""
import re
import sys
from pathlib import Path

import pandas as pd
import pdfplumber

RAW_DIR = Path("data/raw")
OUT_FILE = Path("data/processed/cutoffs_all.csv")

COLLEGE_RE = re.compile(r"^(\d{5})\s*-\s*(.+)$")          # 01002 - Government College ...
BRANCH_RE = re.compile(r"^(\d{9,10})\s*-\s*(.+)$")        # 0100219110 - Civil Engineering
STATUS_RE = re.compile(r"^Status:\s*(.+)$", re.I)         # Status: Government Autonomous ...
VALUE_RE = re.compile(r"(\d+)\s*\(\s*([\d.]+)\s*\)")      # 34692 (91.7858261)
FILE_RE = re.compile(r"(\d{4})ENGG_CAP(\d)", re.I)
LEVEL_STARTS = (
    "state level",
    "other than home university",
    "home university",
    "all india",
)
LEVEL_CHARS = {"S": "State", "H": "Home University", "O": "Other than Home University"}


def parse_code(code):
    """Split a column code like GOPENS into (seat_group, category, level).
    Best effort; the raw code is always kept in the output as category_code."""
    if code in ("TFWS", "EWS") or code.startswith("ORPHAN"):
        return "", code, ""
    group, body = "", code
    for prefix in ("PWD", "DEF"):
        if code.startswith(prefix):
            group, body = prefix, code[len(prefix):]
            break
    else:
        if code[0] in "GL":
            group = {"G": "General", "L": "Ladies"}[code[0]]
            body = code[1:]
    level = LEVEL_CHARS.get(body[-1], "") if body else ""
    if level:
        body = body[:-1]
    return group, body, level


def read_context(page, top, bottom, state):
    """Read college / branch / status lines from the strip of page between two tables."""
    top, bottom = max(top, 0), min(bottom, page.height)
    if bottom - top < 5:
        return
    text = page.crop((0, top, page.width, bottom)).extract_text() or ""
    for line in (l.strip() for l in text.splitlines()):
        if not line:
            continue
        if m := COLLEGE_RE.match(line):
            state["college_code"], state["college_name"] = m.group(1), m.group(2).strip()
        elif m := BRANCH_RE.match(line):
            state["branch_code"], state["branch_name"] = m.group(1), m.group(2).strip()
        elif m := STATUS_RE.match(line):
            state["institute_status"] = m.group(1).strip()
        elif line.lower().startswith(LEVEL_STARTS):
            state["status_level"] = line


def extract_pdf(path):
    m = FILE_RE.search(path.name)
    if not m:
        print(f"  ! cannot read year/round from file name: {path.name}")
        return []
    year, rnd = int(m.group(1)), int(m.group(2))

    rows = []
    state = {}
    with pdfplumber.open(path) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            tables = sorted(page.find_tables(), key=lambda t: t.bbox[1])
            prev_bottom = 0
            for table in tables:
                _, top, _, bottom = table.bbox
                read_context(page, prev_bottom, top, state)
                prev_bottom = bottom

                data = table.extract()
                if not data or len(data) < 2:
                    continue
                header = [(c or "").strip() for c in data[0]]
                if not header or header[0].lower() != "stage":
                    print(f"  ! page {page_no}: unexpected table header {header[:3]}")
                    continue

                for row in data[1:]:
                    stage = (row[0] or "").strip()
                    for idx, code in enumerate(header):
                        if idx == 0 or not code or idx >= len(row):
                            continue
                        cell = (row[idx] or "").replace("\n", " ")
                        v = VALUE_RE.search(cell)
                        if not v:
                            continue
                        group, category, level = parse_code(code)
                        rows.append({
                            "year": year,
                            "round": rnd,
                            "stage": stage,
                            "college_code": state.get("college_code"),
                            "college_name": state.get("college_name"),
                            "branch_code": state.get("branch_code"),
                            "branch_name": state.get("branch_name"),
                            "institute_status": state.get("institute_status"),
                            "status_level": state.get("status_level"),
                            "category_code": code,
                            "seat_group": group,
                            "category": category,
                            "level": level,
                            "cutoff_rank": int(v.group(1)),
                            "cutoff_percentile": float(v.group(2)),
                            "source_file": path.name,
                        })
            # a college line can also sit below the last table of a page
            read_context(page, prev_bottom, page.height, state)
    return rows


def validate(df):
    print("\n--- validation ---")
    print("rows:", len(df))
    print("colleges:", df["college_code"].nunique(), "| branches:", df["branch_code"].nunique())
    for col in ("college_code", "branch_code", "status_level", "institute_status"):
        n = df[col].isna().sum()
        print(f"missing {col}: {n}" + ("   <-- check" if n else ""))
    bad_pct = df[(df.cutoff_percentile < 0) | (df.cutoff_percentile > 100)]
    print("percentiles outside 0-100:", len(bad_pct))
    print("ranks <= 0:", int((df.cutoff_rank <= 0).sum()))
    key = ["year", "round", "stage", "college_code", "branch_code", "status_level", "category_code"]
    print("duplicate keys:", int(df.duplicated(subset=key).sum()))
    print("\nrows per year/round:")
    print(df.groupby(["year", "round"]).size().to_string())
    print("\nspot-check these against the PDF:")
    print(df.sample(min(10, len(df)), random_state=1)[
        ["college_code", "branch_name", "category_code", "cutoff_rank", "cutoff_percentile"]
    ].to_string(index=False))


def main():
    pdfs = sorted(RAW_DIR.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found in {RAW_DIR}")
    all_rows = []
    for pdf_path in pdfs:
        print(f"Extracting {pdf_path.name} ...")
        all_rows += extract_pdf(pdf_path)
    if not all_rows:
        sys.exit("Nothing extracted; check the PDF layout.")
    df = pd.DataFrame(all_rows)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} rows to {OUT_FILE}")
    validate(df)


if __name__ == "__main__":
    main()
