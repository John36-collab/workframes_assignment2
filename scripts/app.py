#!/usr/bin/env python3
"""
app.py - Streamlit app for interactive exploration
Run:
    streamlit run scripts/app.py
Notes:
 - The app prefers outputs/sample_metadata.csv (fast). If missing it tries data/metadata.csv.
 - The app will warn if key columns (title, publish_time, authors, journal, source_x) are absent.
"""
import io
import os

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st 
import wordcloud as wc

st.set_page_config(page_title="CORD-19 Explorer", layout="wide")
st.title("CORD-19-style Metadata Explorer")
st.markdown("Interactive exploration: filter by year/source/title, view charts, generate word cloud, and download filtered CSV.")

DATA_SAMPLE = "outputs/sample_metadata.csv"
DATA_FULL = "data/metadata.csv"

@st.cache_data
def load_df():
    # prefer the sample (faster)
    path = DATA_SAMPLE if os.path.exists(DATA_SAMPLE) else DATA_FULL
    if not os.path.exists(path):
        st.error("No metadata found. Put metadata.csv in data/ or run scripts/explore.py to create outputs/sample_metadata.csv.")
        st.stop()
    df = pd.read_csv(path, low_memory=False, on_bad_lines="warn")
    # normalize columns same way as explore.py
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[ \/\-#]", "_", regex=True)
        .str.replace(r"[^0-9a-zA-Z_]", "", regex=True)
    )
    # ensure columns exist
    if "publish_time" in df.columns:
        df["publish_time"] = pd.to_datetime(df["publish_time"], errors="coerce")
        df["year"] = df["publish_time"].dt.year
    else:
        df["year"] = pd.NA
    df["title"] = df.get("title", "").fillna("").astype(str)
    df["abstract"] = df.get("abstract", "").fillna("").astype(str)
    df["authors"] = df.get("authors", "").fillna("").astype(str)
    df["journal"] = df.get("journal", "").fillna("").astype(str)
    df["source_x"] = df.get("source_x", "").fillna("").astype(str)
    df["abstract_word_count"] = df["abstract"].str.split().str.len()
    return df

df = load_df()

# Check required columns and show a warning if missing
required = ["title", "abstract", "publish_time", "authors", "journal", "source_x"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.warning("The metadata file is missing some expected columns which may limit analysis: " + ", ".join(missing))

# Sidebar filters
st.sidebar.header("Filters")
min_year = int(df["year"].dropna().min()) if df["year"].notna().any() else 2018
max_year = int(df["year"].dropna().max()) if df["year"].notna().any() else 2023

# ✅ fixed indentation and logic here
if min_year == max_year:
    st.sidebar.write(f"Only one year in data: {min_year}")
    year_range = (min_year, max_year)
else:
    year_range = st.sidebar.slider(
        "Year range",
        min_year,
        max_year,
        (min_year, max_year)
    )

sources = ["All"] + sorted(df["source_x"].fillna("Unknown").unique().tolist()) if "source_x" in df.columns else ["All"]
selected_source = st.sidebar.selectbox("Source", sources)
title_query = st.sidebar.text_input("Title contains (case-insensitive)")
top_n = st.sidebar.slider("Top N journals", 5, 30, 10)

# Apply filters
filtered = df.copy()
if df["year"].notna().any():
    filtered = filtered[(filtered["year"] >= year_range[0]) & (filtered["year"] <= year_range[1])]
if selected_source != "All":
    filtered = filtered[filtered["source_x"].fillna("Unknown") == selected_source]
if title_query.strip():
    filtered = filtered[filtered["title"].str.contains(title_query, case=False, na=False)]

st.markdown(f"Showing {len(filtered)} papers (filtered) — total rows in file: {len(df)}")

# Two-column layout for charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Publications by year")
    if filtered["year"].notna().any():
        yc = filtered["year"].dropna().astype(int).value_counts().sort_index()
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.bar(yc.index, yc.values)
        ax.set_xlabel("Year")
        ax.set_ylabel("Count")
        st.pyplot(fig)
    else:
        st.write("No year data available to plot.")

with col2:
    st.subheader(f"Top {top_n} journals")
    if "journal" in filtered.columns:
        top_j = filtered["journal"].fillna("Unknown").value_counts().head(top_n)
        fig2, ax2 = plt.subplots(figsize=(6, 3))
        ax2.bar(range(len(top_j)), top_j.values)
        ax2.set_xticks(range(len(top_j)))
        ax2.set_xticklabels(top_j.index, rotation=45, ha="right")
        st.pyplot(fig2)
    else:
        st.write("No journal column available.")

st.subheader("Word cloud (titles)")
if st.button("Generate word cloud"):
    titles_text = " ".join(filtered["title"].dropna().astype(str).values)
    if titles_text.strip() == "":
        st.write("No titles available for a word cloud.")
    else:
        wc = WordCloud(width=900, height=400, background_color="white").generate(titles_text)
        fig3, ax3 = plt.subplots(figsize=(9, 4))
        ax3.imshow(wc, interpolation="bilinear")
        ax3.axis("off")
        st.pyplot(fig3)

st.subheader("Data sample")
display_cols = [c for c in ["title", "authors", "journal", "year", "abstract_word_count"] if c in filtered.columns]
st.dataframe(filtered[display_cols].head(200), use_container_width=True)

# Download filtered CSV
buf = io.StringIO()
filtered.to_csv(buf, index=False)
st.download_button("Download filtered CSV", buf.getvalue().encode("utf-8"), file_name="filtered_metadata.csv", mime="text/csv")

st.info("If app is slow, run: python scripts/explore.py --input data/metadata.csv --outdir outputs --sample_size 5000 first to create outputs/sample_metadata.csv (faster).")