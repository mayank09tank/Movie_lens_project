import json
import os

import psycopg
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def get_connection():

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg.connect(database_url)

    password = os.getenv("DB_PASSWORD")
    if not password:
        raise RuntimeError("DB_PASSWORD is not set. Add it to movielens_app/.env or your environment.")

    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "movie_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=password,
    )


def init_db():

    sql = """
    CREATE TABLE IF NOT EXISTS rag_prompt_history
    (
        history_id BIGSERIAL PRIMARY KEY,

        user_prompt TEXT NOT NULL,

        response TEXT NOT NULL,

        retrieved_sources TEXT,

        sql_context TEXT,

        created_at TIMESTAMP
            DEFAULT CURRENT_TIMESTAMP
    );
    """


    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute(sql)

        conn.commit()


def save_history(
    user_prompt: str,
    response: str,
    sources: list[str],
    sql_context: str = ""
):

    sql = """
    INSERT INTO rag_prompt_history
    (
        user_prompt,
        response,
        retrieved_sources,
        sql_context
    )
    VALUES (%s, %s, %s, %s);
    """


    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                sql,
                (
                    user_prompt,
                    response,
                    json.dumps(sources),
                    sql_context
                )
            )


def get_history(
    limit: int = 20
):

    sql = """
    SELECT
        history_id,
        user_prompt,
        response,
        retrieved_sources,
        created_at
    FROM rag_prompt_history
    ORDER BY created_at DESC
    LIMIT %s;
    """


    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                sql,
                (limit,)
            )

            return cur.fetchall()