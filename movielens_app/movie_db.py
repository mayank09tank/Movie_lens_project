import re

from db import get_connection


# ---------------------------------
# Extract movie name from question
# ---------------------------------

def _extract_title(
    question: str
) -> str | None:

    patterns = [

        r"\brating\s+(?:of|for)\s+(.+?)\??$",

        r"\baverage\s+rating\s+(?:of|for)\s+(.+?)\??$",

        r"\bscore\s+(?:of|for)\s+(.+?)\??$"

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            question,
            flags=re.IGNORECASE
        )


        if match:

            return match.group(
                1
            ).strip(
                " .?!"
            )


    return None


# ---------------------------------
# Get movie rating
# ---------------------------------

def get_movie_rating_context(
    title: str
) -> str:

    sql = """
    SELECT
        m.movie_id,
        m.title,
        ROUND(
            AVG(r.rating),
            2
        ) AS average_rating,
        COUNT(*) AS rating_count

    FROM movies m

    JOIN ratings r
        ON r.movie_id = m.movie_id

    WHERE m.title ILIKE %s

    GROUP BY
        m.movie_id,
        m.title

    ORDER BY rating_count DESC

    LIMIT 5;
    """


    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                sql,
                (f"%{title}%",)
            )

            rows = cur.fetchall()


    if not rows:

        return ""


    lines = [
        "MovieLens database results:"
    ]


    for (
        movie_id,
        movie_title,
        avg_rating,
        rating_count
    ) in rows:

        lines.append(

            f"- {movie_title} | "
            f"movie_id={movie_id} | "
            f"average_rating={avg_rating} | "
            f"ratings_count={rating_count}"

        )


    return "\n".join(lines)


# ---------------------------------
# Top rated movies
# ---------------------------------

def get_top_rated_context(
    limit: int = 5
) -> str:

    sql = """
    SELECT
        m.title,
        ROUND(
            AVG(r.rating),
            2
        ) AS average_rating,
        COUNT(*) AS rating_count

    FROM movies m

    JOIN ratings r
        ON r.movie_id = m.movie_id

    GROUP BY
        m.movie_id,
        m.title

    HAVING COUNT(*) >= 20

    ORDER BY
        average_rating DESC,
        rating_count DESC

    LIMIT %s;
    """


    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                sql,
                (limit,)
            )

            rows = cur.fetchall()


    if not rows:

        return ""


    lines = [
        "MovieLens top-rated results:"
    ]


    for (
        title,
        avg_rating,
        rating_count
    ) in rows:

        lines.append(

            f"- {title} | "
            f"average_rating={avg_rating} | "
            f"ratings_count={rating_count}"

        )


    return "\n".join(lines)


# ---------------------------------
# Decide what MovieLens context
# is needed
# ---------------------------------

def get_movie_context(
    question: str
) -> str:

    lower = question.lower()


    try:

        title = _extract_title(
            question
        )


        if title:

            context = get_movie_rating_context(
                title
            )


            if context:

                return context


        if any(
            phrase in lower
            for phrase in [

                "top rated",
                "highest rated",
                "best rated",
                "highest rating",
                "top movies"

            ]
        ):

            return get_top_rated_context()


    except Exception:

        # RAG should still work even if
        # MovieLens SQL context fails.

        return ""


    return ""