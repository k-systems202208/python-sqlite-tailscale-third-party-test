from flask import Blueprint, abort, g, jsonify, redirect, render_template, request, url_for

from app.core.access import require_user

from .service import create_note, delete_note, list_notes, update_note

bp = Blueprint("notes", __name__, template_folder="templates")


def _note_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "body": row["body"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@bp.get("/notes")
@require_user
def index():
    rows = list_notes(g.current_user["id"])
    return render_template("notes/index.html", notes=rows)


@bp.post("/notes")
@require_user
def add_note():
    try:
        create_note(
            g.current_user["id"],
            request.form.get("title", ""),
            request.form.get("body", ""),
        )
    except ValueError as exc:
        abort(400, description=str(exc))
    return redirect(url_for("notes.index"))


@bp.post("/notes/<int:note_id>/update")
@require_user
def update(note_id: int):
    try:
        updated = update_note(
            g.current_user["id"],
            note_id,
            request.form.get("title", ""),
            request.form.get("body", ""),
        )
    except ValueError as exc:
        abort(400, description=str(exc))
    if not updated:
        abort(404)
    return redirect(url_for("notes.index"))


@bp.post("/notes/<int:note_id>/delete")
@require_user
def delete(note_id: int):
    if not delete_note(g.current_user["id"], note_id):
        abort(404)
    return redirect(url_for("notes.index"))


@bp.get("/api/notes")
@require_user
def api_notes():
    return jsonify([_note_to_dict(row) for row in list_notes(g.current_user["id"])])


@bp.post("/api/notes")
@require_user
def api_create_note():
    payload = request.get_json(silent=True) or {}
    try:
        row = create_note(g.current_user["id"], payload.get("title", ""), payload.get("body", ""))
    except ValueError as exc:
        abort(400, description=str(exc))
    return jsonify(_note_to_dict(row)), 201
