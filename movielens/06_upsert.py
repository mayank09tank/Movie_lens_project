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


        # =========================================
        # BEFORE
        # =========================================

        cursor.execute(
            """
            SELECT
                movie_id,
                title,
                genres

            FROM movies

            WHERE movie_id = 1
            """
        )


        print("BEFORE:")

        print(
            cursor.fetchone()
        )


        # =========================================
        # UPSERT
        # =========================================

        cursor.execute(
            """
            INSERT INTO movies
            (
                movie_id,
                title,
                genres
            )

            VALUES
            (
                1,
                'Toy Story - UPDATED',
                'Adventure|Animation|Children'
            )

            ON CONFLICT (movie_id)

            DO UPDATE SET

                title = EXCLUDED.title,

                genres = EXCLUDED.genres;
            """
        )


    conn.commit()


    # =========================================
    # AFTER
    # =========================================

    with conn.cursor() as cursor:


        cursor.execute(
            """
            SELECT
                movie_id,
                title,
                genres

            FROM movies

            WHERE movie_id = 1
            """
        )


        print("\nAFTER:")

        print(
            cursor.fetchone()
        )


except Exception as e:

    conn.rollback()

    print(e)


finally:

    conn.close()