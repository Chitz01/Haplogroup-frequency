
cd Documents/LU/SEM2/BINP29/

mkdir haplogroup-frequency
cd mkdir haplogroup-frequency

# Connect to git
git init
git remote add origin https://github.com/Chitz01/Haplogroup-frequency.git

# app.py - hello world page- title with description
# requirements.txt - all the necessary libraries

git add .
git commit -m "Commit 1: Basic page with title and description"
git branch -M main
git push -u origin main

# test locally

# Create a virtual environment
python3 -m venv .venv
# Activate your virtual environment
source .venv/bin/activate
# Install packages (first time only)
pip install -r requirements.txt
# Run the app
streamlit run app.py

git add .
git commit -m "Commit 2: Added file upload and display data as a table"
git push





