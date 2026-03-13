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
        "Sex":       row[23],
    })

df = pd.DataFrame(rows)
df = df.replace("..", "")   # replace missing values

# ---- Show a summary ----
st.success(f"File loaded! Found {len(df)} individuals from {df['Country'].nunique()} countries.")

# ---- Show the table ----
st.subheader("Raw Data")
st.write("Here are the first 50 rows:")
st.dataframe(df.head(50))

st.divider()

# ---- Search section ----
st.subheader("Step 2: Search for a haplogroup")

haplo_type = st.radio("Choose DNA type", ["Y-DNA", "mtDNA"], horizontal=True)
haplogroup = st.text_input("Type a haplogroup", placeholder="e.g. R1b or H or U5")

if st.button("Search"):

    # figure out which column to look in
    if haplo_type == "Y-DNA":
        col = "Y Haplo"
    else:
        col = "mt Haplo"

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

    if len(results) == 0:
        st.error(f"No results found for {haplogroup}.")
        st.info("Tip: H, U5, J, T, K are mtDNA haplogroups — switch to mtDNA above.")
    else:
        result_df = pd.DataFrame(results)
        result_df = result_df.sort_values("Frequency %", ascending=False)

        st.write(f"Found **{haplogroup}** in **{len(result_df)}** countries.")

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
            title=f"{haplogroup} — top 15 countries",
        )
        fig_bar.update_traces(texttemplate="%{text}%", textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)

        # ---- Table ----
        st.subheader("Full Results")
        st.dataframe(result_df)

        