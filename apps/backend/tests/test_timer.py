import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from timer.models import PomodoroSettings, PomodoroSession


# ============================================================================
# MODEL TESTS
# ============================================================================

@pytest.mark.django_db
def test_pomodoro_settings_str_representation():
    settings = PomodoroSettings.objects.create(username="alice")
    assert str(settings) == "alice's Pomodoro settings"


@pytest.mark.django_db
def test_pomodoro_settings_default_values():
    settings = PomodoroSettings.objects.create(username="alice")
    assert settings.work_minutes == 25
    assert settings.short_break_minutes == 5
    assert settings.long_break_minutes == 15
    assert settings.sessions_before_long_break == 4


@pytest.mark.django_db
def test_pomodoro_settings_username_unique():
    PomodoroSettings.objects.create(username="alice")
    with pytest.raises(Exception):
        PomodoroSettings.objects.create(username="alice")


@pytest.mark.django_db
def test_pomodoro_session_str_representation():
    session = PomodoroSession.objects.create(
        username="alice", session_type="work", duration_minutes=25
    )
    assert str(session) == "alice - Focus (25m)"


@pytest.mark.django_db
def test_pomodoro_session_default_type_is_work():
    session = PomodoroSession.objects.create(username="alice", duration_minutes=25)
    assert session.session_type == "work"


@pytest.mark.django_db
def test_pomodoro_session_completed_at_auto_set():
    session = PomodoroSession.objects.create(username="alice", duration_minutes=25)
    assert session.completed_at is not None


@pytest.mark.django_db
def test_pomodoro_session_ordering_most_recent_first():
    """Meta.ordering = ["-completed_at"] means the default queryset
    order should already be newest-first, without an explicit
    order_by() call anywhere.
    """
    older = PomodoroSession.objects.create(username="alice", duration_minutes=25)
    PomodoroSession.objects.filter(id=older.id).update(
        completed_at=timezone.now() - timedelta(days=1)
    )
    newer = PomodoroSession.objects.create(username="alice", duration_minutes=25)

    sessions = list(PomodoroSession.objects.filter(username="alice"))
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
    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("timer:timer")
    response = client.get(url)

    assert response.status_code == 200
    assert PomodoroSettings.objects.filter(username="alice").exists()
    assert response.context["settings"].work_minutes == 25


@pytest.mark.django_db
def test_timer_get_authenticated_shows_only_own_sessions(client):
    """Recent sessions and today's stats should only reflect the
    logged-in user's data, not another user's.
    """
    session = client.session
    session["username"] = "alice"
    session.save()

    PomodoroSession.objects.create(username="alice", session_type="work", duration_minutes=25)
    PomodoroSession.objects.create(username="bob",