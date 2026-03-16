import streamlit as st
import pandas as pd
import csv
import io
import plotly.express as px
import plotly.graph_objects as go

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
    st.write("- A migration map showing how the haplogroup spread over time")
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
    # clean lat/lon — AADR uses comma as decimal separator
    def parse_coord(val):
        try:
            return float(val.strip().replace(",", "."))
        except:
            return None
    rows.append({
        "Sample ID": row[1],
        "Country":   row[14],
        "Y Haplo":   row[26] if row[25].strip() in ("", "..") else row[25],
        "mt Haplo":  row[28],
        "Date BP":   row[8],
        "Full Date": row[10],
        "Sex":       row[23],
        "Lat":       parse_coord(row[15]) if len(row) > 15 else None,
        "Lon":       parse_coord(row[16]) if len(row) > 16 else None,
    })

df = pd.DataFrame(rows)
df = df.replace("..", "")   # replace missing values
df["Date BP"] = pd.to_numeric(df["Date BP"], errors="coerce")

# ---- Clean country names ----
country_map = {
    "England": "United Kingdom", "Scotland": "United Kingdom",
    "Wales": "United Kingdom", "Northern Ireland": "United Kingdom",
    "Sardinia": "Italy", "Sicily": "Italy",
    "Siberia": "Russia", "Crimea": "Ukraine",
    "Prussia": "Germany", "Bavaria": "Germany",
    "Anatolia": "Turkey", "Bohemia": "Czech Republic",
    "Moravia": "Czech Republic", "Iberia": "Spain",
}
df["Country"] = df["Country"].replace(country_map)
df["Country"] = df["Country"].apply(
    lambda x: x.split("_")[0] if "_" in str(x) else x
)

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
        color_continuous_scale=[[0.0, "#e0f2f1"],[0.3, "#00897b"],[0.7, "#00574b"],[1.0, "#002b25"],],
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

    # MIGRATION MAP
    st.subheader("Migration Map")
    st.write(
        "Arrows show the spread of this haplogroup over time — from the oldest "
        "known sample to progressively more recent ones. Each arrow points from "
        "an older location to a newer one."
    )
 
    # Get matched samples that have coordinates and a date
    migration_df = all_matches.copy()
    migration_df = migration_df[
        migration_df["Lat"].notna() &
        migration_df["Lon"].notna() &
        migration_df["Date BP"].notna()
    ].copy()
 
    # Convert BP to approximate year CE for labelling
    migration_df["Year CE"] = (1950 - migration_df["Date BP"]).astype(int)
 
    # Sort oldest first (highest BP = oldest)
    migration_df = migration_df.sort_values("Date BP", ascending=False).reset_index(drop=True)
 
    if len(migration_df) < 2:
        st.info("Not enough samples with GPS coordinates to draw migration arrows for this haplogroup.")
    else:
        # Limit to top 30 oldest samples so the map stays readable
        migration_df = migration_df.head(30)
 
        fig_mig = go.Figure()
 
        # ---- Draw one arrow line between each consecutive pair ----
        for i in range(len(migration_df) - 1):
            src = migration_df.iloc[i]    # older sample
            dst = migration_df.iloc[i+1]  # newer sample
 
            # The line connecting them
            fig_mig.add_trace(go.Scattergeo(
                lon=[src["Lon"], dst["Lon"]],
                lat=[src["Lat"], dst["Lat"]],
                mode="lines",
                line=dict(width=1.5, color="#f59e0b"),
                opacity=0.6,
                showlegend=False,
                hoverinfo="skip",
            ))
 
            # Arrowhead — a small marker at the destination end
            fig_mig.add_trace(go.Scattergeo(
                lon=[dst["Lon"]],
                lat=[dst["Lat"]],
                mode="markers",
                marker=dict(
                    size=6,
                    color="#f59e0b",
                    symbol="triangle-up",
                ),
                showlegend=False,
                hoverinfo="skip",
            ))
 
        # ---- Plot each sample as a dot, coloured by age ----
        fig_mig.add_trace(go.Scattergeo(
            lon=migration_df["Lon"],
            lat=migration_df["Lat"],
            mode="markers",
            marker=dict(
                size=10,
                color=migration_df["Year CE"],
                colorscale=[
                    [0.0, "#dc2626"],   # oldest = red
                    [0.5, "#f59e0b"],   # middle = amber
                    [1.0, "#2dd4bf"],   # newest = teal
                ],
                colorbar=dict(title="Year CE"),
                line=dict(color="white", width=0.8),
                showscale=True,
            ),
            text=migration_df.apply(
                lambda r: (
                    f"<b>{r['Sample ID']}</b><br>"
                    f"Country: {r['Country']}<br>"
                    f"Date: {r['Full Date']}<br>"
                    f"Haplogroup: {r[col]}"
                ), axis=1
            ),
            hovertemplate="%{text}<extra></extra>",
            name="Ancient samples",
        ))
 
        # ---- Add start label (oldest) and end label (newest) ----
        oldest_row = migration_df.iloc[0]
        newest_row = migration_df.iloc[-1]
 
        fig_mig.add_trace(go.Scattergeo(
            lon=[oldest_row["Lon"]],
            lat=[oldest_row["Lat"]],
            mode="markers+text",
            marker=dict(size=14, color="#dc2626", line=dict(color="white", width=1.5)),
            text=["OLDEST"],
            textposition="top center",
            textfont=dict(size=10, color="#dc2626"),
            showlegend=False,
            hoverinfo="skip",
        ))
 
        fig_mig.add_trace(go.Scattergeo(
            lon=[newest_row["Lon"]],
            lat=[newest_row["Lat"]],
            mode="markers+text",
            marker=dict(size=14, color="#2dd4bf", line=dict(color="white", width=1.5)),
            text=["NEWEST"],
            textposition="top center",
            textfont=dict(size=10, color="#2dd4bf"),
            showlegend=False,
            hoverinfo="skip",
        ))
 
        fig_mig.update_layout(
            title=f"Migration path of {haplogroup} — oldest to newest ({len(migration_df)} samples)",
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="#94a3b8",
                showland=True,
                landcolor="#f1f5f9",
                showocean=True,
                oceancolor="#e0f2fe",
                showcountries=True,
                countrycolor="#cbd5e1",
                projection_type="natural earth",
            ),
            height=520,
            margin=dict(l=0, r=0, t=50, b=0),
            showlegend=False,
        )
 
        st.plotly_chart(fig_mig, use_container_width=True)
 
        # Small explanation below the map
        st.caption(
            f"Showing the {len(migration_df)} oldest samples with GPS coordinates. "
            f"Red = oldest ({oldest_row['Full Date']}), "
            f"Teal = most recent shown ({newest_row['Full Date']}). "
            "Arrows follow chronological order oldest → newest."
        )

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
