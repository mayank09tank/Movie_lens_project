import csv
import os
import psycopg


# ==================================================
# DATABASE CONNECTION
# ==================================================

conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="movie_db",
    user="postgres",
    password="FB@hari3147"
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BATCH_FOLDER = os.path.join(BASE_DIR, "batches")


# ==================================================
# INSERT QUERIES
# ==================================================

INSERT_QUERIES = {

    "movies": """
        INSERT INTO movies
        (
            movie_id,
            title,
            genres
        )
        VALUES
        (%s, %s, %s)
    """,


    "links": """
        INSERT INTO links
        (
            movie_id,
            imdb_id,
            tmdb_id
        )
        VALUES
        (%s, %s, %s)
    """,


    "ratings": """
        INSERT INTO ratings
        (
            user_id,
            movie_id,
            rating,
            rating_timestamp
        )
        VALUES
        (%s, %s, %s, %s)
    """,


    "tags": """
        INSERT INTO tags
        (
            user_id,
            movie_id,
            tag,
            tag_timestamp
        )
        VALUES
        (%s, %s, %s, %s)
    """
}


# ==================================================
# FUNCTION
# ==================================================

def load_table(table_name):

    folder = os.path.join(
        BATCH_FOLDER,
        table_name
    )


    # Get all CSV batch files

    batch_files = sorted(
        [
            file
            for file in os.listdir(folder)
            if file.endswith(".csv")
        ]
    )


    print("\n" + "=" * 60)
    print(f"Loading table: {table_name}")
    print(f"Total batches: {len(batch_files)}")
    print("=" * 60)


    total_rows = 0


    # ==================================================
    # PROCESS EVERY BATCH
    # ==================================================

    for batch_file in batch_files:

        file_path = os.path.join(
            folder,
            batch_file
        )


        rows = []


        # ----------------------------------------------
        # READ BATCH
        # ----------------------------------------------

        with open(
            file_path,
            "r",
            encoding="utf-8",
            newline=""
        ) as file:

            reader = csv.DictReader(file)


            for row in reader:

                if table_name == "movies":

                    data = (
                        int(row["movieId"]),
                        row["title"],
                        row["genres"]
                    )


                elif table_name == "links":

                    data = (
                        int(row["movieId"]),
                        row["imdbId"],
                        row["tmdbId"]
                    )


                elif table_name == "ratings":

                    data = (
                        int(row["userId"]),
                        int(row["movieId"]),
                        float(row["rating"]),
                        int(row["timestamp"])
                    )


                elif table_name == "tags":

                    data = (
                        int(row["userId"]),
                        int(row["movieId"]),
                        row["tag"],
                        int(row["timestamp"])
                    )


                rows.append(data)


        # ----------------------------------------------
        # INSERT BATCH
        # ----------------------------------------------

        try:

            with conn.cursor() as cursor:

                cursor.executemany(
                    INSERT_QUERIES[table_name],
                    rows
                )


            # Commit this batch

            conn.commit()


            total_rows += len(rows)


            print(
                f"{batch_file} -> "
                f"{len(rows)} rows inserted"
            )


        except Exception as error:

            # If batch fails

            conn.rollback()

            print(
                f"{batch_file} FAILED"
            )

            print(error)

            raise


    print(
        f"\n{table_name} completed"
    )

    print(
        f"Total rows inserted: {total_rows}"
    )


# ==================================================
# LOAD ORDER
# ==================================================

try:

    # Parent table first
    load_table("movies")

    # Child table
    load_table("links")

    # Child table
    load_table("ratings")

    # Child table
    load_table("tags")


    print("\n" + "=" * 60)
    print("ALL DATA INSERTED SUCCESSFULLY")
    print("=" * 60)


finally:

    conn.close()