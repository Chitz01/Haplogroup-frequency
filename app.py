import streamlit as st
import pandas as pd
import csv
import io
import plotly.express as px

st.set_page_config(layout="wide")   # makes the page wider

st.title("Haplogroup Frequency Explorer")
st.write("This app shows where ancient DNA haplogroups are found around the world.")

# ---- File upload ----
st.sidebar.header("Step 1: Upload your data")
uploaded_file = st.sidebar.file_uploader("Upload the AADR CSV file", type=["csv", "tsv", "txt"])

# ---- If no file uploaded, show instructions ----
if uploaded_file is None:
    st.info("Please upload the AADR CSV file using the sidebar on the left.")

    st.subheader("What does this app do?")
    st.write("You can search for any ancient DNA haplogroup and see:")
    st.write("- Which countries it was found in")
    st.write("- How common it is in each country")
    st.write("- The oldest samples ever found")
    st.write("- A world map showing the distribution")
    st.stop()

# ---- Read the file ----
# The AADR file uses semicolons to separate columns
content = uploaded_file.read().decode("utf-8-sig")
reader = csv.reader(io.StringIO(content), delimiter=";")
next(reader)  # skip the header row

# ---- Pick only the columns we need ----
rows = []
for row in reader:
    if len(row) < 29:
        continue
    rows.append({
        "Sample ID": row[1],
        "Country":   row[14],
        "Y Haplo":   row[25],
        "mt Haplo":  row[28],
        "Date BP":   row[8],
        "Full Date": row[10],
        "Sex":       row[23],
    })

df = pd.DataFrame(rows)
df = df.replace("..", "")   # replace missing values
df["Date BP"] = pd.to_numeric(df["Date BP"], errors="coerce")

# ---- Show a summary ----
st.success(f"File loaded! Found {len(df)} individuals from {df['Country'].nunique()} countries.")

# ---- Show the table ----
st.subheader("Raw Data")
st.write("Here are the first 50 rows:")
st.dataframe(df.head(50))

col1, col2, col3 = st.columns(3)
col1.metric("Total individuals", len(df))
col2.metric("Countries",         df["Country"].nunique())
col3.metric("Y haplogroups",     df["Y Haplo"].replace("", pd.NA).nunique())

st.divider()

# ---- Search section ----
st.subheader("Step 2: Search for a haplogroup")
st.write("Examples: **R1b** (Y-DNA, Western Europe)  |  **H** (mtDNA, common Europe)  |  **U5** (mtDNA, hunter-gatherers)  |  **J2** (Y-DNA, Near East)")

haplo_type = st.radio("Choose DNA type", ["Y-DNA", "mtDNA"], horizontal=True)
haplogroup = st.text_input("Type a haplogroup", placeholder="e.g. R1b or H or U5")

if st.button("Search"):

    if haplogroup.strip() == "":
        st.warning("Please type a haplogroup first.")
        st.stop()

    # figure out which column to look in
    if haplo_type == "Y-DNA":
        col = "Y Haplo"
    else:
        col = "mt Haplo"

    # find all matching individuals
    all_matches = df[df[col].str.startswith(haplogroup, na=False)]

    if len(all_matches) == 0:
        st.error(f"No results found for '{haplogroup}' in {haplo_type}.")
        st.info("Tip: H, U5, J, T, K are mtDNA haplogroups — switch to mtDNA above.")
        st.stop()

    # count matches per country
    results = []
    for country, group in df.groupby("Country"):
        total   = len(group[group[col] != ""])
        matches = group[group[col].str.startswith(haplogroup, na=False)]
        count   = len(matches)
        if count > 0:
            results.append({
                "Country":       country,
                "Matches":       count,
                "Total Sampled": total,
                "Frequency %":   round(count / total * 100, 1),
            })
    
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values("Frequency %", ascending=False)

    st.write(f"Found **{len(all_matches)}** individuals with **{haplogroup}** across **{len(result_df)}** countries.")

    # ---- World map ----
    st.subheader("World Map")
    fig_map = px.choropleth(
        result_df,
        locations="Country",
        locationmode="country names",
        color="Frequency %",
        hover_name="Country",
        hover_data=["Matches", "Total Sampled"],
        color_continuous_scale="blues",
        title=f"{haplogroup} frequency by country",
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # ---- Bar chart ----
    st.subheader("Top 15 Countries")
    fig_bar = px.bar(
        result_df.head(15),
        x="Country",
        y="Frequency %",
        color="Frequency %",
        color_continuous_scale="blues",
        text="Frequency %",
        title=f"{haplogroup} — top 15 countries by frequency",
    )
    fig_bar.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

    # ---- Oldest samples ----
    st.subheader("Oldest Samples")
    st.write("The 10 oldest individuals found carrying this haplogroup:")
    oldest = all_matches[all_matches["Date BP"] > 0].sort_values("Date BP", ascending=False)
    st.dataframe(oldest[["Sample ID", "Country", "Full Date", col]].head(10))

    # ---- Full table ----
    st.subheader("Full Results Table")
    st.dataframe(result_df)

    # ---- Download button ----
    st.download_button(
        label="Download results as CSV",
        data=result_df.to_csv(index=False),
        file_name=f"{haplogroup}_frequency.csv",
        mime="text/csv",
    )
