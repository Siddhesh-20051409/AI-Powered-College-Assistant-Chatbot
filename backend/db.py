import mysql.connector
from rapidfuzz import fuzz

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Sidpadwal@"
        database="ycis_chatbot"
    )


def detect_intent(query):
    q = query.lower()

    intents = {
        "fees": ["fee", "fees", "fees structure", "payment"],
        "department": ["department", "departments", "dept"],
        "course": ["course", "courses", "program", "programs"],
        "admission": ["admission", "apply", "application", "enroll"]
    }

    best_intent = None
    best_score = 0

    for intent, keywords in intents.items():
        for word in keywords:
            score = fuzz.partial_ratio(q, word)
            if score > best_score:
                best_score = score
                best_intent = intent

    if best_score >= 70:
        return best_intent

    return None


def search_database(query):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    q = query.lower()
    category = detect_intent(q)

    # First: category search
    if category:
        cursor.execute(
            "SELECT * FROM college_info WHERE category = %s",
            (category,)
        )
        rows = cursor.fetchall()
        if rows:
            cursor.close()
            conn.close()
            return rows

    # Second: fuzzy search on all database rows
    cursor.execute("SELECT * FROM college_info")
    all_rows = cursor.fetchall()

    matched_rows = []

    for row in all_rows:
        text = f"{row['title']} {row['content']}".lower()
        score = fuzz.partial_ratio(q, text)

        if score >= 65:
            matched_rows.append(row)

    cursor.close()
    conn.close()

    return matched_rows

    # =========================
    # SEARCH WEBSITE DATA
    # =========================

def search_website_data(query):

    conn = get_connection()

    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM website_data
        WHERE title LIKE %s
        OR content LIKE %s
        LIMIT 5
        """,
        (f"%{query}%", f"%{query}%")
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows