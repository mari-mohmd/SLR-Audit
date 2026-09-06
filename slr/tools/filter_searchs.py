import csv
import os
import sys
from difflib import SequenceMatcher

searches_file = sys.argv[1]
executions_file = sys.argv[2]
output_folder = sys.argv[3]

output_file = os.path.join(
    output_folder,
    "searches_minus_exclusions.csv"
)


def similarity(title1, title2):
    return SequenceMatcher(
        None,
        title1.lower().strip(),
        title2.lower().strip()
    ).ratio()


# Read execution titles
with open(executions_file, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    execution_titles = [
        row["title"]
        for row in reader
        if row.get("title")
    ]


# Read searches
with open(searches_file, "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)

    rows = list(reader)
    columns = reader.fieldnames


# Remove searches that match an execution by 90% or more
remaining_rows = []

for row in rows:
    search_title = row.get("title", "")

    excluded = False

    for execution_title in execution_titles:
        if similarity(search_title, execution_title) >= 0.90:
            excluded = True
            break

    if not excluded:
        remaining_rows.append(row)


# Write output
os.makedirs(output_folder, exist_ok=True)

with open(output_file, "w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(remaining_rows)


print(f"Searches: {len(rows)}")
print(f"Executions: {len(execution_titles)}")
print(f"Remaining: {len(remaining_rows)}")
print(f"Excluded: {len(rows) - len(remaining_rows)}")
print(f"Output: {output_file}")