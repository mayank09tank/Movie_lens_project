import psycopg


conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="movie_db",
    user="postgres",
    password="FB@hari3147"
)


# ==================================================
# HISTORY TABLES
# ==================================================

SQL = """

-- ==================================================
-- MOVIES HISTORY
-- ==================================================

CREATE TABLE IF NOT EXISTS movies_history (

    history_id BIGSERIAL PRIMARY KEY,

    movie_id INTEGER NOT NULL,

    title TEXT,

    genres TEXT,

    valid_from TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    valid_to TIMESTAMP,

    is_current BOOLEAN NOT NULL
        DEFAULT TRUE,

    operation VARCHAR(20)

);


-- ==================================================
-- LINKS HISTORY
-- ==================================================

CREATE TABLE IF NOT EXISTS links_history (

    history_id BIGSERIAL PRIMARY KEY,

    movie_id INTEGER NOT NULL,

    imdb_id TEXT,

    tmdb_id TEXT,

    valid_from TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    valid_to TIMESTAMP,

    is_current BOOLEAN NOT NULL
        DEFAULT TRUE,

    operation VARCHAR(20)

);


-- ==================================================
-- RATINGS HISTORY
-- ==================================================

CREATE TABLE IF NOT EXISTS ratings_history (

    history_id BIGSERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL,

    movie_id INTEGER NOT NULL,

    rating NUMERIC(2,1),

    timestamp BIGINT,

    valid_from TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    valid_to TIMESTAMP,

    is_current BOOLEAN NOT NULL
        DEFAULT TRUE,

    operation VARCHAR(20)

);


-- ==================================================
-- TAGS HISTORY
-- ==================================================

CREATE TABLE IF NOT EXISTS tags_history (

    history_id BIGSERIAL PRIMARY KEY,

    user_id INTEGER NOT NULL,

    movie_id INTEGER NOT NULL,

    tag TEXT,

    timestamp BIGINT,

    valid_from TIMESTAMP NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    valid_to TIMESTAMP,

    is_current BOOLEAN NOT NULL
        DEFAULT TRUE,

    operation VARCHAR(20)

);

"""


try:


    with conn.cursor() as cursor:

        cursor.execute(SQL)


    conn.commit()


    print(
        "All history tables created successfully!"
    )


except Exception as e:

    conn.rollback()

    print(e)


finally:

    conn.close()