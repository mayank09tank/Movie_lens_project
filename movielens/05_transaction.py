import psycopg


conn = None

try:
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="movie_db",
        user="postgres",
        password="FB@hari3147",
        autocommit=False
    )

    with conn.cursor() as cursor:

        print("TRANSACTION STARTED")

        # ------------------------------------------
        # INSERT 1
        # ------------------------------------------

        cursor.execute(
            """
            INSERT INTO movies (movie_id, title, genres)
            VALUES (999999, 'Transaction Movie 1', 'Test')
            """
        )

        print("First insert successful")

        # ------------------------------------------
        # INSERT 2
        # ------------------------------------------
        # Same primary key
        # Intentional error
        # ------------------------------------------

        cursor.execute(
            """
            INSERT INTO movies (movie_id, title, genres)
            VALUES (999999, 'Transaction Movie 2', 'Test')
            """
        )

        print("Second insert successful")

    conn.commit()
    print("COMMIT")

except Exception as e:

    print("\nERROR OCCURRED")
    print(e)

    if conn:
        conn.rollback()
        print("ROLLBACK PERFORMED")

finally:
    if conn:
        conn.close()
