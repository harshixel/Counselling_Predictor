"""
scrape_cutoffs.py

Extracts round-wise admission cutoff data (rank/percentile by college,
branch, category, round, and year) from official counselling PDFs.

Usage:
    python scrape_cutoffs.py --input data/raw/round1_2025.pdf --output data/processed/round1_2025.csv
"""

import argparse
import pandas as pd
import pdfplumber


def extract_tables_from_pdf(pdf_path: str) -> list:
    """Extract raw tables from every page of the given PDF."""
    all_tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            all_tables.extend(tables)
    return all_tables


def tables_to_dataframe(tables: list) -> pd.DataFrame:
    """
    Convert raw extracted tables into a cleaned DataFrame.
    NOTE: Column mapping will need to be adjusted once you see the
    actual structure of your source PDFs — cutoff PDFs vary a lot
    in layout between years/authorities.
    """
    rows = []
    for table in tables:
        for row in table[1:]:  # skip header row of each table
            rows.append(row)

    df = pd.DataFrame(rows, columns=[
        "college_code", "college_name", "branch", "category",
        "rank", "percentile"
    ])
    return df


def main():
    parser = argparse.ArgumentParser(description="Scrape counselling cutoff PDFs into CSV.")
    parser.add_argument("--input", required=True, help="Path to source PDF")
    parser.add_argument("--output", required=True, help="Path to write cleaned CSV")
    parser.add_argument("--round", type=int, required=False, help="Counselling round number")
    parser.add_argument("--year", type=int, required=False, help="Admission year")
    args = parser.parse_args()

    tables = extract_tables_from_pdf(args.input)
    df = tables_to_dataframe(tables)

    if args.round is not None:
        df["round"] = args.round
    if args.year is not None:
        df["year"] = args.year

    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()
