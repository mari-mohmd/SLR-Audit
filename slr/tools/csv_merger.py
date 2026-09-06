import csv
import glob
import os
import sys

folder = sys.argv[1]
output = os.path.join(folder, "merged_csvs.csv")

files = glob.glob(os.path.join(folder, "*.csv"))

# Remove the output file from the input files
files = [
    file for file in files
    if os.path.basename(file) != "merged_csvs.csv"
]

all_headers = []
rows = []


# --------------------------------------------------
# Read all CSV files
# --------------------------------------------------

for file in files:

    with open(
        file,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as infile:

        reader = csv.DictReader(infile)

        headers = reader.fieldnames

        if not headers or "title" not in headers:
            print(f"Skipping {file}: no title column")
            continue

        # Add new headers
        for header in headers:
            if header not in all_headers:
                all_headers.append(header)

        # Store rows
        for row in reader:
            rows.append(row)


# --------------------------------------------------
# Make title the first column
# --------------------------------------------------

all_headers.remove("title")
all_headers.insert(0, "title")


# --------------------------------------------------
# Write merged CSV
# --------------------------------------------------

with open(
    output,
    "w",
    newline="",
    encoding="utf-8"
) as outfile:

    writer = csv.DictWriter(
        outfile,
        fieldnames=all_headers,
        extrasaction="ignore"
    )

    writer.writeheader()

    for row in rows:
        writer.writerow(row)


print(f"Files merged: {len(files)}")
print(f"Rows merged: {len(rows)}")
print(f"Columns: {len(all_headers)}")
print(f"Merged CSV: {output}")