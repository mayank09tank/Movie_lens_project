import psycopg


conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="movie_db",
    user="postgres",
    password="FB@hari3147"
)


try:

    with conn.cursor() as cursor:


        # ------------------------------------------
        # BEFORE
        # ------------------------------------------

        cursor.execute(
            "SELECT COUNT(*) FROM movies"
        )

        movies_before = cursor.fetchone()[0]


        cursor.execute(
            "SELECT COUNT(*) FROM links"
        )

        links_before = cursor.fetchone()[0]


        cursor.execute(
            "SELECT COUNT(*) FROM ratings"
        )

        ratings_before = cursor.fetchone()[0]


        cursor.execute(
            "SELECT COUNT(*) FROM tags"
        )

        tags_before = cursor.fetchone()[0]


    print("BEFORE RUN")
    print("Movies :", movies_before)
    print("Links  :", links_before)
    print("Ratings:", ratings_before)
    print("Tags   :", tags_before)


finally:

    conn.close()