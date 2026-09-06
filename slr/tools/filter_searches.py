import csv
import os
import sys


# Usage:
# python filter_searches.py searches.csv exclusions.csv output_folder


searches_file = sys.argv[1]
exclusions_file = sys.argv[2]
output_folder = sys.argv[3]

output_file = os.path.join(
    output_folder,
    "extraction.csv"
)


def normalize_title(title):
    """Normalize title for exact matching."""
    return " ".join(title.strip().lower().split())


# --------------------------------------------------
# Load exclusion titles into a set
# --------------------------------------------------

exclusion_titles = set()

with open(
    exclusions_file,
    "r",
    encoding="utf-8-sig",
    newline=""
) as file:

    reader = csv.DictReader(file)

    for row in reader:
        title = row.get("title", "")

        if title.strip():
            exclusion_titles.add(
                normalize_title(title)
            )


print(f"Exclusion titles loaded: {len(exclusion_titles):,}")


# --------------------------------------------------
# Read searches and write output
# --------------------------------------------------

os.makedirs(output_folder, exist_ok=True)

total = 0
excluded = 0
remaining = 0

with open(
    searches_file,
    "r",
    encoding="utf-8-sig",
    newline=""
) as infile, open(
    output_file,
    "w",
    encoding="utf-8",
    newline=""
) as outfile:

    reader = csv.DictReader(infile)

    # Preserve searches headers and their exact order
    writer = csv.DictWriter(
        outfile,
        fieldnames=reader.fieldnames
    )

    writer.writeheader()

    for row in reader:

        total += 1

        search_title = row.get("title", "")

        # Remove the entire row if the title
        # exists in the exclusion set
        if (
            search_title.strip()
            and normalize_title(search_title)
            in exclusion_titles
        ):
            excluded += 1
            continue

        writer.writerow(row)
        remaining += 1


# --------------------------------------------------
# Summary
# --------------------------------------------------

print()
print("Finished!")
print("-----------------------------")
print(f"Search rows:       {total:,}")
print(f"Exclusion titles:  {len(exclusion_titles):,}")
print(f"Rows removed:      {excluded:,}")
print(f"Rows remaining:    {remaining:,}")
print()
print(f"Output: {output_file}")