import csv
import os


# ==================================================
# CONFIGURATION
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, "data")
BATCH_FOLDER = os.path.join(BASE_DIR, "batches")

BATCH_SIZE = 1000


CSV_FILES = [
    "movies.csv",
    "links.csv",
    "ratings.csv",
    "tags.csv"
]


# ==================================================
# CREATE BATCH ROOT FOLDER
# ==================================================

os.makedirs(BATCH_FOLDER, exist_ok=True)


# ==================================================
# SPLIT FUNCTION
# ==================================================

def split_csv(file_name):

    input_file_path = os.path.join(
        DATA_FOLDER,
        file_name
    )

    # movies.csv -> movies
    table_name = os.path.splitext(file_name)[0]

    output_folder = os.path.join(
        BATCH_FOLDER,
        table_name
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )


    print("\n" + "=" * 60)
    print(f"Processing: {file_name}")
    print("=" * 60)


    # ----------------------------------------------
    # OPEN ORIGINAL CSV
    # ----------------------------------------------

    with open(
        input_file_path,
        "r",
        encoding="utf-8",
        newline=""
    ) as input_file:

        reader = csv.reader(input_file)

        # First row = header
        header = next(reader)


        batch_number = 1
        row_count = 0

        output_file = None
        writer = None


        # ------------------------------------------
        # READ EVERY ROW
        # ------------------------------------------

        for row in reader:

            # --------------------------------------
            # CREATE NEW BATCH EVERY 1000 ROWS
            # --------------------------------------

            if row_count % BATCH_SIZE == 0:

                # Close previous batch
                if output_file is not None:
                    output_file.close()


                output_file_path = os.path.join(
                    output_folder,
                    f"batch_{batch_number:03d}.csv"
                )


                output_file = open(
                    output_file_path,
                    "w",
                    encoding="utf-8",
                    newline=""
                )


                writer = csv.writer(
                    output_file
                )


                # Every batch gets header
                writer.writerow(header)


                print(
                    f"Created: {output_file_path}"
                )


                batch_number += 1


            # --------------------------------------
            # WRITE ROW INTO CURRENT BATCH
            # --------------------------------------

            writer.writerow(row)

            row_count += 1


        # Close last batch
        if output_file is not None:
            output_file.close()


    total_batches = batch_number - 1


    print("\nCompleted")
    print(f"File           : {file_name}")
    print(f"Total rows     : {row_count}")
    print(f"Total batches  : {total_batches}")


# ==================================================
# PROCESS ALL CSV FILES
# ==================================================

for file_name in CSV_FILES:

    split_csv(file_name)


print("\n" + "=" * 60)
print("ALL CSV FILES SPLIT SUCCESSFULLY")
print("=" * 60)