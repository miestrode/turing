import csv
import json
from glob import glob

LOG_FOLDER = "logs"
LOG_GLOB = LOG_FOLDER + "/*/*/*/*.json"
DEFAULT_SAVE_LOCATION = "results.csv"
FIELDS = [
    "agent",
    "domain",
    "problem",
    "learning",
    "success",
    "cpu-time",
    "wall-time",
    "stderr",
    "actions",
    "perception-requests",
    "terminated",
]


def main():
    csv_path = input(
        "This is the CSV log exporter. Currently it exports to "
        + DEFAULT_SAVE_LOCATION
        + ". Press enter to continue or type here an alternative saving file: "
    )
    writer = csv.writer(open(csv_path if csv_path else DEFAULT_SAVE_LOCATION, "w"))

    writer.writerow(FIELDS)

    for file_path in glob(LOG_GLOB):
        try:
            with open(file_path) as problem_run:
                data = json.loads(problem_run.read())

            writer.writerow([data[field] for field in FIELDS])
        except json.JSONDecodeError:
            pass


if __name__ == "__main__":
    main()
