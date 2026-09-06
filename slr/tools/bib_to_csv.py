import csv
import glob
import os
import re
import sys

folder = sys.argv[1]
output_file = os.path.join(folder, "merged_bib.csv")

files = glob.glob(os.path.join(folder, "*.bib"))

rows = []

for input_file in files:
    with open(input_file, "r", encoding="utf-8") as file:
        text = file.read()

    # Find each BibTeX entry
    entries = re.findall(r"@\w+\{.*?\n\}", text, re.DOTALL)

    for entry in entries:
        row = {}

        # Get fields like: author = {...},
        fields = re.findall(
            r"(\w+)\s*=\s*\{(.*?)\}",
            entry,
            re.DOTALL
        )

        for field, value in fields:
            row[field] = " ".join(value.split())

        rows.append(row)

# Get all unique column names
columns = []

for row in rows:
    for column in row:
        if column not in columns:
            columns.append(column)

# Write everything into one CSV
with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print(f"Processed {len(files)} BibTeX files.")
print(f"Created: {output_file}")