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


# ==================================================
# CREATE TABLES
# ==================================================

sql = """

CREATE TABLE IF NOT EXISTS movies (

    movie_id INTEGER PRIMARY KEY,

    title TEXT NOT NULL,

    genres TEXT

);


CREATE TABLE IF NOT EXISTS links (

    movie_id INTEGER PRIMARY KEY,

    imdb_id TEXT,

    tmdb_id TEXT,

    FOREIGN KEY (movie_id)
        REFERENCES movies(movie_id)

);


CREATE TABLE IF NOT EXISTS ratings (

    user_id INTEGER NOT NULL,

    movie_id INTEGER NOT NULL,

    rating NUMERIC(2,1) NOT NULL,

    rating_timestamp BIGINT NOT NULL,

    PRIMARY KEY (user_id, movie_id),

    FOREIGN KEY (movie_id)
        REFERENCES movies(movie_id)

);


CREATE TABLE IF NOT EXISTS tags (

    user_id INTEGER NOT NULL,

    movie_id INTEGER NOT NULL,

    tag TEXT NOT NULL,

    tag_timestamp BIGINT NOT NULL,

    PRIMARY KEY (
        user_id,
        movie_id,
        tag,
        tag_timestamp
    ),

    FOREIGN KEY (movie_id)
        REFERENCES movies(movie_id)

);


CREATE INDEX IF NOT EXISTS idx_ratings_movie
ON ratings(movie_id);


CREATE INDEX IF NOT EXISTS idx_ratings_user
ON ratings(user_id);


CREATE INDEX IF NOT EXISTS idx_tags_movie
ON tags(movie_id);


CREATE INDEX IF NOT EXISTS idx_tags_user
ON tags(user_id);

"""


try:

    with conn.cursor() as cursor:

        cursor.execute(sql)


    conn.commit()

    print("All tables created successfully!")


except Exception as error:

    conn.rollback()

    print("ERROR:")
    print(error)


finally:

    conn.close()