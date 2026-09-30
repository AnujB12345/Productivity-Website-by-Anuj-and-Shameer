import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from users.models import User
from timer.models import PomodoroSettings, PomodoroSession


# ============================================================================
# MODEL TESTS
# ============================================================================

@pytest.mark.django_db
def test_pomodoro_settings_str_representation():
    alice = User.objects.create(username="alice", email="alice@test.com")
    settings = PomodoroSettings.objects.create(user=alice)
    assert str(settings) == "alice's Pomodoro settings"


@pytest.mark.django_db
def test_pomodoro_settings_default_values():
    alice = User.objects.create(username="alice", email="alice@test.com")
    settings = PomodoroSettings.objects.create(user=alice)
    assert settings.work_minutes == 25
    assert settings.short_break_minutes == 5
    assert settings.long_break_minutes == 15
    assert settings.sessions_before_long_break == 3


@pytest.mark.django_db
def test_pomodoro_settings_username_unique():
    alice = User.objects.create(username="alice", email="alice@test.com")
    PomodoroSettings.objects.create(user=alice)
    with pytest.raises(Exception):
        PomodoroSettings.objects.create(user=alice)


@pytest.mark.django_db
def test_pomodoro_session_str_representation():
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = PomodoroSession.objects.create(
        user=alice, session_type="work", duration_minutes=25
    )
    assert str(session) == "alice - Focus (25m)"


@pytest.mark.django_db
def test_pomodoro_session_default_type_is_work():
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = PomodoroSession.objects.create(user=alice, duration_minutes=25)
    assert session.session_type == "work"


@pytest.mark.django_db
def test_pomodoro_session_completed_at_auto_set():
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = PomodoroSession.objects.create(user=alice, duration_minutes=25)
    assert session.completed_at is not None


@pytest.mark.django_db
def test_pomodoro_session_ordering_most_recent_first():
    """Meta.ordering = ["-completed_at"] means the default queryset
    order should already be newest-first, without an explicit
    order_by() call anywhere.
    """
    alice = User.objects.create(username="alice", email="alice@test.com")
    older = PomodoroSession.objects.create(user=alice, duration_minutes=25)
    PomodoroSession.objects.filter(id=older.id).update(
        completed_at=timezone.now() - timedelta(days=1)
    )
    newer = PomodoroSession.objects.create(user=alice, duration_minutes=25)

    sessions = list(PomodoroSession.objects.filter(user=alice))
    assert sessions == [newer, older]


# ============================================================================
# VIEW TESTS
# ============================================================================

@pytest.mark.django_db
def test_timer_unauthenticated_redirect(client):
    """Unauthenticated users without session['username'] redirect to login."""
    url = reverse("timer:timer")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("users:login")


@pytest.mark.django_db
def test_timer_get_authenticated_creates_default_settings(client):
    """Visiting the page for the first time should auto-create a
    PomodoroSettings row via get_or_create, with default values.
    """
    alice = User.objects.create(username="alice", email="alice@test.com")

    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("timer:timer")
    response = client.get(url)

    assert response.status_code == 200
    assert PomodoroSettings.objects.filter(user=alice).exists()
    assert response.context["settings"].work_minutes == 25


@pytest.mark.django_db
def test_timer_get_authenticated_shows_only_own_sessions(client):
    """Recent sessions and today's stats should only reflect the
    logged-in user's data, not another user's.
    """
    alice = User.objects.create(username="alice", email="alice@test.com")
    bob = User.objects.create(username="bob", email="bob@test.com")

    session = client.session
    session["username"] = "alice"
    session.save()

    PomodoroSession.objects.create(user=alice, session_type="work", duration_minutes=25)
    PomodoroSession.objects.create(user=bob, session_type="work", duration_minutes=25)

    url = reverse("timer:timer")
    response = client.get(url)

    assert response.status_code == 200
    # Context should only count Alice's session
    assert len(response.context["recent_sessions"]) == 1


@pytest.mark.django_db
def test_timer_update_settings_valid_data(client):
    """POST update_settings updates the user's PomodoroSettings and redirects."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("timer:timer")
    response = client.post(url, {
        "update_settings": "1",
        "work_minutes": "30",
        "short_break_minutes": "10",
        "long_break_minutes": "20",
        "sessions_before_long_break": "5",
    })

    assert response.status_code == 302
    assert response.url == reverse("timer:timer")

    settings_obj = PomodoroSettings.objects.get(user=alice)
    assert settings_obj.work_minutes == 30
    assert settings_obj.short_break_minutes == 10
    assert settings_obj.long_break_minutes == 20
    assert settings_obj.sessions_before_long_break == 5


@pytest.mark.django_db
def test_timer_update_settings_invalid_or_clamped_values(client):
    """Values outside min/max bounds are clamped, and invalid data falls back to defaults."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("timer:timer")
    response = client.post(url, {
        "update_settings": "1",
        "work_minutes": "999",  # Should clamp to max 120
        "short_break_minutes": "invalid",  # Should fall back to default (5)
        "long_break_minutes": "0",  # Should clamp to min 1
        "sessions_before_long_break": "15",  # Should clamp to max 12
    })

    assert response.status_code == 302
    settings_obj = PomodoroSettings.objects.get(user=alice)
    assert settings_obj.work_minutes == 120
    assert settings_obj.short_break_minutes == 5
    assert settings_obj.long_break_minutes == 1
    assert settings_obj.sessions_before_long_break == 12


@pytest.mark.django_db
def test_timer_log_session_success(client):
    """POST log_session creates a new PomodoroSession and returns status ok JSON."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("timer:timer")
    response = client.post(url, {
        "log_session": "1",
        "session_type": "work",
        "duration_minutes": "25",
        "task_label": "Math Revision",
    })

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    created_session = PomodoroSession.objects.get(user=alice)
    assert created_session.session_type == "work"
    assert created_session.duration_minutes == 25
    assert created_session.task_label == "Math Revision"


@pytest.mark.django_db
def test_timer_log_session_invalid_data(client):
    """POST log_session with invalid type or duration returns 400 error status."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("timer:timer")
    response = client.post(url, {
        "log_session": "1",
        "session_type": "invalid_type",
        "duration_minutes": "abc",
    })

    assert response.status_code == 400
    assert response.json() == {"status": "error"}
    assert PomodoroSession.objects.filter(user=alice).count() == 0


@pytest.mark.django_db
def test_timer_delete_session(client):
    """POST delete_session deletes the specified PomodoroSession and redirects."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    p_session = PomodoroSession.objects.create(
        user=alice, session_type="work", duration_minutes=25
    )

    url = reverse("timer:timer")
    response = client.post(url, {
        "delete_session": "1",
        "session_id": str(p_session.id),
    })

    assert response.status_code == 302
    assert response.url == reverse("timer:timer")
    assert not PomodoroSession.objects.filter(id=p_session.id).exists()