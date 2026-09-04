from conftest import csrf_for, tailscale_headers

import app.features as features
from app.db import _migration_files, get_db


def test_notes_feature_replaces_items_sample():
    assert "notes" in features.feature_names()
    assert "items" not in features.feature_names()


def test_notes_migration_is_discovered(app):
    with app.app_context():
        migrations = _migration_files()

    assert any(
        version == 3
        and name == "notes"
        and path.as_posix().endswith("app/features/notes/migrations/003_notes.sql")
        for version, name, path in migrations
    )
    assert not any(name == "sample_items" for _version, name, _path in migrations)


def test_notes_page_is_available_and_items_is_removed(client):
    alice = tailscale_headers()
    assert client.get("/notes", headers=alice).status_code == 200
    assert client.get("/items", headers=alice).status_code == 404


def test_fresh_schema_contains_notes_but_not_items(app):
    with app.app_context():
        tables = {
            row[0]
            for row in get_db()
            .execute("SELECT name FROM sqlite_master WHERE type = 'table'")
            .fetchall()
        }

    assert "notes" in tables
    assert "items" not in tables


def test_notes_are_isolated_per_user(client):
    alice = tailscale_headers("alice@example.com", "Alice")
    bob = tailscale_headers("bob@example.com", "Bob")

    token = csrf_for(client, alice)
    created = client.post(
        "/api/notes",
        json={"title": "Alice note", "body": "private memo"},
        headers={**alice, "X-CSRF-Token": token},
    )
    assert created.status_code == 201

    alice_notes = client.get("/api/notes", headers=alice).get_json()
    bob_notes = client.get("/api/notes", headers=bob).get_json()

    assert [note["title"] for note in alice_notes] == ["Alice note"]
    assert bob_notes == []


def test_note_validation_error_is_json(client):
    alice = tailscale_headers()
    token = csrf_for(client, alice)
    response = client.post(
        "/api/notes",
        json={"title": ""},
        headers={**alice, "X-CSRF-Token": token},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["status"] == 400
    assert "between 1 and 200" in payload["error"]


def test_note_mutation_requires_csrf(client):
    alice = tailscale_headers()
    response = client.post(
        "/api/notes",
        json={"title": "Should fail"},
        headers=alice,
    )
    assert response.status_code == 400


def test_update_and_delete_note(client):
    alice = tailscale_headers()
    token = csrf_for(client, alice)
    created = client.post(
        "/api/notes",
        json={"title": "Before", "body": "old"},
        headers={**alice, "X-CSRF-Token": token},
    )
    note_id = created.get_json()["id"]

    updated = client.post(
        f"/notes/{note_id}/update",
        data={"csrf_token": token, "title": "After", "body": "new"},
        headers=alice,
    )
    assert updated.status_code == 302
    note = client.get("/api/notes", headers=alice).get_json()[0]
    assert note["title"] == "After"
    assert note["body"] == "new"

    deleted = client.post(
        f"/notes/{note_id}/delete",
        data={"csrf_token": token},
        headers=alice,
    )
    assert deleted.status_code == 302
    assert client.get("/api/notes", headers=alice).get_json() == []


def test_other_user_cannot_update_or_delete_note(client):
    alice = tailscale_headers("alice@example.com", "Alice")
    bob = tailscale_headers("bob@example.com", "Bob")
    alice_token = csrf_for(client, alice)
    created = client.post(
        "/api/notes",
        json={"title": "Alice only"},
        headers={**alice, "X-CSRF-Token": alice_token},
    )
    note_id = created.get_json()["id"]

    bob_token = csrf_for(client, bob)
    updated = client.post(
        f"/notes/{note_id}/update",
        data={"csrf_token": bob_token, "title": "Stolen", "body": ""},
        headers=bob,
    )
    deleted = client.post(
        f"/notes/{note_id}/delete",
        data={"csrf_token": bob_token},
        headers=bob,
    )

    assert updated.status_code == 404
    assert deleted.status_code == 404
    assert client.get("/api/notes", headers=alice).get_json()[0]["title"] == "Alice only"
