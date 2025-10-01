#!/usr/bin/env python3
"""
explore.py
- Loads data/data_metadata.csv (or a path you pass)
- Cleans and normalizes columns
- Produces:
    - cleaned CSV: outputs/metadata_cleaned.csv
    - sample CSV for fast iteration: outputs/sample_metadata.csv
    - plots saved into outputs/: publications_by_year.png, top_journals.png, top_sources.png, wordcloud_titles.png
    - CSV of top title words: outputs/top_title_words.csv

Usage:
    python scripts/explore.py --input data/metadata.csv --outdir outputs --sample_size 5000
"""
import argparse
import os
import re
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

# -------------------------
# Helper functions
# -------------------------
def normalize_columns(df):
    # make columns predictable: lower, strip, replace spaces and special chars with underscores
    new_cols = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[ \/\-#]", "_", regex=True)
        .str.replace(r"[^0-9a-zA-Z_]", "", regex=True)
    )
    df.columns = new_cols
    return df


def ensure_dir(d):
    os.makedirs(d, exist_ok=True)


def safe_read_csv(path):
    # read with a bit of tolerance for large files / weird lines
    return pd.read_csv(path, low_memory=False, keep_default_na=True, na_values=["", "NA", "N/A"], on_bad_lines="warn")


# -------------------------
# Main processing
# -------------------------
def main(input_path, outdir, sample_size):
    ensure_dir(outdir)
    print(f"Loading {input_path} ...")
    df = safe_read_csv(input_path)
    print("Raw shape:", df.shape)

    # normalize column names to be robust to spaces/case
    df = normalize_columns(df)

    # common names we expect (after normalization)
    expected = [
        "sha",
        "source_x",
        "title",
        "doi",
        "pmcid",
        "pubmed_id",
        "license",
        "abstract",
        "publish_time",
        "authors",
        "journal",
        "microsoft_academic_paper_id",
        "who_covidence",
        "has_full_text",
    ]

    present = [c for c in expected if c in df.columns]
    if not present:
        print("Warning: none of the expected columns found. I'll continue with whatever columns are present.")
    else:
        print("Using columns:", present)
        df = df.copy()  # make a copy for safety

    # convert publish_time to datetime, extract year
    if "publish_time" in df.columns:
        df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce", infer_datetime_format=True)
        df["year"] = df["publish_time"].dt.year
    else:
        df["year"] = pd.NA

    # fill missing text fields to avoid operations failing
    if "abstract" in df.columns:
        df["abstract"] = df["abstract"].fillna("")
    else:
        df["abstract"] = ""

    if "title" in df.columns:
        df["title"] = df["title"].fillna("")
    else:
        df["title"] = ""

    # derived columns
    df["abstract_word_count"] = df["abstract"].str.split().str.len()
    df["title_word_count"] = df["title"].str.split().str.len()

    # save cleaned full dataset
    cleaned_path = os.path.join(outdir, "metadata_cleaned.csv")
    df.to_csv(cleaned_path, index=False)
    print("Saved cleaned CSV:", cleaned_path)

    # save a sample for fast iteration (if sample_size provided)
    if sample_size and sample_size > 0:
        n = min(sample_size, len(df))
        sample = df.sample(n=n, random_state=42)
        sample_path = os.path.join(outdir, "sample_metadata.csv")
        sample.to_csv(sample_path, index=False)
        print("Saved sample CSV:", sample_path)

    # -------------------------
    # Analysis & visualizations
    # -------------------------
    # Publications by year
    if df["year"].notna().any():
        year_counts = df["year"].dropna().astype(int).value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(year_counts.index, year_counts.values)
        ax.set_xlabel("Year")
        ax.set_ylabel("Number of papers")
        ax.set_title("Publications by Year")
        fig.tight_layout()
        path = os.path.join(outdir, "publications_by_year.png")
        fig.savefig(path)
        plt.close(fig)
        print("Saved:", path)
    else:
        print("No publish_time/year data available to plot publications by year.")

    # Top journals
    if "journal" in df.columns:
        top_journals = df["journal"].fillna("Unknown").value_counts().head(15)
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(range(len(top_journals)), top_journals.values)
        ax.set_xticks(range(len(top_journals)))
        ax.set_xticklabels(top_journals.index, rotation=45, ha="right")
        ax.set_title("Top Journals (by paper count)")
        fig.tight_layout()
        path = os.path.join(outdir, "top_journals.png")
        fig.savefig(path)
        plt.close(fig)
        print("Saved:", path)
    else:
        print("No 'journal' column present for top_journals plot.")

    # Top sources
    if "source_x" in df.columns:
        top_sources = df["source_x"].fillna("Unknown").value_counts().head(15)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(range(len(top_sources)), top_sources.values)
        ax.set_xticks(range(len(top_sources)))
        ax.set_xticklabels(top_sources.index, rotation=45, ha="right")
        ax.set_title("Top Sources")
        fig.tight_layout()
        path = os.path.join(outdir, "top_sources.png")
        fig.savefig(path)
        plt.close(fig)
        print("Saved:", path)
    else:
        print("No 'source_x' column present for source counts.")

    # Word cloud of titles
    all_titles = " ".join(df["title"].dropna().astype(str).values)
    if len(all_titles.strip()) > 0:
        wc = WordCloud(width=1200, height=600, background_color="white").generate(all_titles)
        path = os.path.join(outdir, "wordcloud_titles.png")
        wc.to_file(path)
        print("Saved wordcloud:", path)
    else:
        print("No titles to generate a word cloud.")

    # Top title words CSV (simple tokenization and stopwords filtering)
    text = all_titles.lower()
    words = re.findall(r"\b\w+\b", text)
    stopwords = set(
        [
            "the",
            "and",
            "of",
            "in",
            "to",
            "a",
            "for",
            "on",
            "with",
            "by",
            "an",
            "is",
            "from",
            "that",
            "are",
            "as",
            "at",
            "be",
            "this",
            "we",
            "our",
            "or",
            "using",
            "use",
            "study",
            "studies",
            "paper",
            "research",
            "covid",
            "covid19",
            "coronavirus",
            "sars",
            "sarscov2",
            "2019",
            "2019ncov",
            "novel",
        ]
    )
    filtered = [w for w in words if w not in stopwords and len(w) > 2]
    counter = Counter(filtered)
    most = counter.most_common(200)
    top_words_df = pd.DataFrame(most, columns=["word", "count"])
    tpath = os.path.join(outdir, "top_title_words.csv")
    top_words_df.to_csv(tpath, index=False)
    print("Saved top words CSV:", tpath)

    # Print quick summary
    print("\nQuick summary:")
    print("Total papers:", len(df))
    if "year" in df.columns:
        print("Years present:", df["year"].dropna().astype(int).unique()[:20])
    if "journal" in df.columns:
        print("Unique journals:", df["journal"].nunique())
    if "source_x" in df.columns:
        print("Unique sources:", df["source_x"].nunique())

    print("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Explore CORD-19-style metadata")
    parser.add_argument("--input", default="data/metadata.csv", help="path to metadata.csv")
    parser.add_argument("--outdir", default="outputs", help="output directory for cleaned csv and plots")
    parser.add_argument("--sample_size", type=int, default=5000, help="sample rows to save for fast iteration (0 to disable)")
    args = parser.parse_args()
    main(args.input, args.outdir, args.sample_size)