import streamlit as st
import pandas as pd
import csv
import io

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