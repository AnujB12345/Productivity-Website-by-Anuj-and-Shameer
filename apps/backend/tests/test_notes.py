import pytest
from django.urls import reverse
from notes.models import Note


# ============================================================================
# MODEL TESTS
# ============================================================================

@pytest.mark.django_db
def test_note_str_representation():
    note = Note.objects.create(title="Biology Summary", username="alice")
    assert str(note) == "Biology Summary"


@pytest.mark.django_db
def test_note_default_values():
    note = Note.objects.create(title="Math Formulas", username="alice")
    assert note.description == ""
    assert note.subject == ""
    assert note.subject_colour == "#000000"


# ============================================================================
# VIEW TESTS
# ============================================================================

@pytest.mark.django_db
def test_notes_unauthenticated_redirect(client):
    """Unauthenticated users are redirected to the login page."""
    url = reverse("notes:notes")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("users:login")


@pytest.mark.django_db
def test_notes_get_authenticated(client):
    """Authenticated users see only their own notes and distinct subjects."""
    session = client.session
    session["username"] = "alice"
    session.save()

    Note.objects.create(title="Note 1", subject="Math", username="alice")
    Note.objects.create(title="Note 2", subject="Math", username="alice")
    Note.objects.create(title="Note 3", subject="Physics", username="bob")  # Belongs to Bob

    url = reverse("notes:notes")
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["note_count"] == 2
    assert "Math" in response.context["subjects"]
    assert "Physics" not in response.context["subjects"]


@pytest.mark.django_db
def test_add_note_with_defaults(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("notes:notes")
    response = client.post(url, {
        "add_note": "",
        "title": "History Chapter 1",
        "description": "Important dates",
        "subject": "History"
        # subject_colour omitted to test automatic color fallback
    })

    assert response.status_code == 302
    note = Note.objects.get(username="alice", title="History Chapter 1")
    assert note.description == "Important dates"
    assert note.subject == "History"
    assert note.subject_colour == "#000000"


@pytest.mark.django_db
def test_add_note_reuses_existing_subject_color(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    # Pre-existing note with custom subject color
    Note.objects.create(title="Old Note", subject="Chemistry", subject_colour="#FF0000", username="alice")

    url = reverse("notes:notes")
    client.post(url, {
        "add_note": "",
        "title": "New Note",
        "subject": "Chemistry"
    })

    new_note = Note.objects.get(title="New Note")
    assert new_note.subject_colour == "#FF0000"


@pytest.mark.django_db
def test_edit_note(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    note = Note.objects.create(
        title="Draft",
        description="Draft text",
        subject="Drafts",
        subject_colour="#000000",
        username="alice"
    )

    url = reverse("notes:notes")
    response = client.post(url, {
        "edit_note": "",
        "note_id": note.id,
        "new_title": "Final Version",
        "new_description": "Final content",
        "new_subject": "Published",
        "new_subject_colour": "#00FF00"
    })

    assert response.status_code == 302
    note.refresh_from_db()
    assert note.title == "Final Version"
    assert note.description == "Final content"
    assert note.subject == "Published"
    assert note.subject_colour == "#00FF00"


@pytest.mark.django_db
def test_delete_note(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    note = Note.objects.create(title="Delete Me", username="alice")

    url = reverse("notes:notes")
    response = client.post(url, {"delete_note": "", "note_id": note.id})

    assert response.status_code == 302
    assert not Note.objects.filter(id=note.id).exists()


@pytest.mark.django_db
def test_clear_all_notes(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    Note.objects.create(title="Note A", username="alice")
    Note.objects.create(title="Note B", username="bob")

    url = reverse("notes:notes")
    response = client.post(url, {"clear_all": ""})

    assert response.status_code == 302
    assert Note.objects.count() == 0  # clear_all deletes all Note objects in table