from app.db import get_db


def list_notes(owner_user_id: int):
    return (
        get_db()
        .execute(
            """
            SELECT id, title, body, created_at, updated_at
            FROM notes
            WHERE owner_user_id = ?
            ORDER BY updated_at DESC, id DESC
            """,
            (owner_user_id,),
        )
        .fetchall()
    )


def create_note(owner_user_id: int, title: str, body: str = ""):
    title, body = _validate_note(title, body)
    db = get_db()
    cur = db.execute(
        "INSERT INTO notes (owner_user_id, title, body) VALUES (?, ?, ?)",
        (owner_user_id, title, body),
    )
    db.commit()
    return get_note(owner_user_id, cur.lastrowid)


def get_note(owner_user_id: int, note_id: int):
    return (
        get_db()
        .execute(
            """
            SELECT id, title, body, created_at, updated_at
            FROM notes
            WHERE id = ? AND owner_user_id = ?
            """,
            (note_id, owner_user_id),
        )
        .fetchone()
    )


def update_note(owner_user_id: int, note_id: int, title: str, body: str = "") -> bool:
    title, body = _validate_note(title, body)
    db = get_db()
    cur = db.execute(
        """
        UPDATE notes
        SET title = ?, body = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND owner_user_id = ?
        """,
        (title, body, note_id, owner_user_id),
    )
    db.commit()
    return cur.rowcount == 1


def delete_note(owner_user_id: int, note_id: int) -> bool:
    db = get_db()
    cur = db.execute(
        "DELETE FROM notes WHERE id = ? AND owner_user_id = ?",
        (note_id, owner_user_id),
    )
    db.commit()
    return cur.rowcount == 1


def _validate_note(title: str, body: str) -> tuple[str, str]:
    title = title.strip()
    body = body.strip()
    if not title or len(title) > 200:
        raise ValueError("Title must be between 1 and 200 characters")
    if len(body) > 2000:
        raise ValueError("Body must be 2000 characters or fewer")
    return title, body
