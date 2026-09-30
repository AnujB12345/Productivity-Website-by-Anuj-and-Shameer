import pytest
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from users.models import User
from timer.models import PomodoroSettings, PomodoroSession
from todo.models import Todo


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
def test_todo_unauthenticated_redirect(client):
    """Unauthenticated users without session['username'] redirect to login."""
    url = reverse("todo:todo_list")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("users:login")


@pytest.mark.django_db
def test_todo_get_authenticated_renders_list(client):
    """GET request loads active/done todos separated and correctly counted."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    Todo.objects.create(title="Active Task", user=alice, checked=False)
    Todo.objects.create(title="Completed Task", user=alice, checked=True)

    url = reverse("todo:todo_list")
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.context["active_todos"]) == 1
    assert len(response.context["done_todos"]) == 1
    assert response.context["task_count"] == 2
    assert response.context["checked_count"] == 1


@pytest.mark.django_db
def test_todo_add_task(client):
    """POST add_task creates a new Todo item and redirects."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("todo:todo_list")
    response = client.post(url, {
        "add_task": "1",
        "title": "Buy Groceries",
    })

    assert response.status_code == 302
    assert response.url == reverse("todo:todo_list")
    assert Todo.objects.filter(user=alice, title="Buy Groceries").exists()


@pytest.mark.django_db
def test_todo_edit_task(client):
    """POST edit_task updates the title of an existing todo."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    todo = Todo.objects.create(title="Old Title", user=alice)

    url = reverse("todo:todo_list")
    response = client.post(url, {
        "edit_task": "1",
        "task_id": str(todo.id),
        "new_title": "Updated Title",
    })

    assert response.status_code == 302
    todo.refresh_from_db()
    assert todo.title == "Updated Title"


@pytest.mark.django_db
def test_todo_check_task_toggle(client):
    """POST check_task toggles checked state and sets/clears completed_at timestamp."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    todo = Todo.objects.create(title="Check me", user=alice, checked=False)

    url = reverse("todo:todo_list")
    # Check the task
    client.post(url, {"check_task": "1", "task_id": str(todo.id)})
    todo.refresh_from_db()
    assert todo.checked is True
    assert todo.completed_at is not None

    # Uncheck the task
    client.post(url, {"check_task": "1", "task_id": str(todo.id)})
    todo.refresh_from_db()
    assert todo.checked is False
    assert todo.completed_at is None


@pytest.mark.django_db
def test_todo_change_priority(client):
    """POST change_priority updates task priority level."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    todo = Todo.objects.create(title="Task", priority="Low", user=alice)

    url = reverse("todo:todo_list")
    response = client.post(url, {
        "change_priority": "1",
        "task_id": str(todo.id),
        "priority": "High",
    })

    assert response.status_code == 302
    todo.refresh_from_db()
    assert todo.priority == "High"


@pytest.mark.django_db
def test_todo_delete_task(client):
    """POST delete_task removes a specific todo."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    todo = Todo.objects.create(title="Delete me", user=alice)

    url = reverse("todo:todo_list")
    response = client.post(url, {
        "delete_task": "1",
        "task_id": str(todo.id),
    })

    assert response.status_code == 302
    assert not Todo.objects.filter(id=todo.id).exists()


@pytest.mark.django_db
def test_todo_clear_all(client):
    """POST clear_all removes all todos belonging to the user."""
    alice = User.objects.create(username="alice", email="alice@test.com")
    session = client.session
    session["username"] = "alice"
    session.save()

    Todo.objects.create(title="Task 1", user=alice)
    Todo.objects.create(title="Task 2", user=alice)

    url = reverse("todo:todo_list")
    response = client.post(url, {"clear_all": "1"})

    assert response.status_code == 302
    assert Todo.objects.filter(user=alice).count() == 0