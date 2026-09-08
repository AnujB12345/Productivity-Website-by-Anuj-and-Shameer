import pytest
import datetime
from django.urls import reverse
from calendar_app.models import CalendarEvent  # Adjust import to match your app name (e.g., calendar_app or calendar)


# ============================================================================
# MODEL TESTS
# ============================================================================

@pytest.mark.django_db
def test_calendar_event_str():
    event = CalendarEvent.objects.create(
        title="Team Sync",
        username="alice",
        date="2026-09-10",
        time="10:00:00"
    )
    assert str(event) == "Team Sync"


# ============================================================================
# VIEW TESTS
# ============================================================================

@pytest.mark.django_db
def test_calendar_unauthenticated_redirect(client):
    """Unauthenticated requests redirect to the login page."""
    url = reverse("calendar:calendar")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("users:login")


@pytest.mark.django_db
def test_calendar_get_authenticated(client):
    """Authenticated users can access the calendar and view calculated dates."""
    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("calendar:calendar")
    response = client.get(url, {"year": "2026", "month": "9"})

    assert response.status_code == 200
    assert response.context["year"] == 2026
    assert response.context["month"] == 9
    assert response.context["month_name"] == "September"
    assert response.context["next_month"] == 10
    assert response.context["prev_month"] == 8


@pytest.mark.django_db
def test_calendar_filter_by_selected_date(client):
    """Passing a date query string filters events specifically for that day."""
    session = client.session
    session["username"] = "alice"
    session.save()

    event1 = CalendarEvent.objects.create(
        title="Event 1", username="alice", date="2026-09-10", time="09:00:00"
    )
    CalendarEvent.objects.create(
        title="Event 2", username="alice", date="2026-09-11", time="10:00:00"
    )

    url = reverse("calendar:calendar")
    response = client.get(url, {"date": "2026-09-10"})

    assert response.status_code == 200
    assert len(response.context["selected_date_events"]) == 1
    assert response.context["selected_date_events"][0] == event1


@pytest.mark.django_db
def test_add_event(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("calendar:calendar")
    response = client.post(url, {
        "add_event": "",
        "title": "Doctor Appointment",
        "description": "Checkup",
        "date": "2026-09-15",
        "time": "14:30:00"
    })

    assert response.status_code == 302
    event = CalendarEvent.objects.get(username="alice", title="Doctor Appointment")
    assert str(event.date) == "2026-09-15"
    assert str(event.time) == "14:30:00"


@pytest.mark.django_db
def test_edit_event(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    event = CalendarEvent.objects.create(
        title="Initial Title",
        description="Initial Desc",
        username="alice",
        date="2026-09-15",
        time="10:00:00"
    )

    url = reverse("calendar:calendar")
    response = client.post(url, {
        "edit_event": "",
        "event_id": event.id,
        "title": "Updated Title",
        "description": "Updated Desc",
        "date": "2026-09-16",
        "time": "11:00:00"
    })

    assert response.status_code == 302
    event.refresh_from_db()
    assert event.title == "Updated Title"
    assert event.description == "Updated Desc"
    assert str(event.date) == "2026-09-16"


@pytest.mark.django_db
def test_delete_event(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    event = CalendarEvent.objects.create(
        title="Delete Me",
        username="alice",
        date="2026-09-20",
        time="12:00:00"
    )

    url = reverse("calendar:calendar")
    response = client.post(url, {
        "delete_event": "",
        "event_id": event.id
    })

    assert response.status_code == 302
    assert not CalendarEvent.objects.filter(id=event.id).exists()