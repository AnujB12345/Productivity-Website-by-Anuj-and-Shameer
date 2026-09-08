import pytest
from django.urls import reverse
from django.utils import timezone
from todo.models import Todo


# ============================================================================
# MODEL TESTS
# ============================================================================

@pytest.mark.django_db
def test_todo_str_representation():
    todo = Todo.objects.create(title="Buy Milk", username="alice")
    assert str(todo) == "Buy Milk"


@pytest.mark.django_db
def test_todo_default_values():
    todo = Todo.objects.create(title="Study Pytest", username="alice")
    assert todo.checkbox is False
    assert todo.priority == 2  # Default Priority: Medium
    assert todo.completed_at is None


# ============================================================================
# VIEW TESTS
# ============================================================================

@pytest.mark.django_db
def test_todo_list_unauthenticated_redirect(client):
    """Unauthenticated users without session['username'] redirect to login."""
    url = reverse("todo:todo_list")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("users:login")


@pytest.mark.django_db
def test_todo_list_get_authenticated(client):
    """Authenticated users can view their todo list."""
    session = client.session
    session["username"] = "alice"
    session.save()

    Todo.objects.create(title="Task 1", username="alice")
    Todo.objects.create(title="Task 2", username="bob")  # Belongs to another user

    url = reverse("todo:todo_list")
    response = client.get(url)

    assert response.status_code == 200
    assert response.context["task_count"] == 1
    assert response.context["checked_count"] == 0


@pytest.mark.django_db
def test_add_task(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("todo:todo_list")
    response = client.post(url, {"add_task": "", "title": "New Task"})

    assert response.status_code == 302
    assert Todo.objects.filter(username="alice", title="New Task").exists()


@pytest.mark.django_db
def test_edit_task(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    todo = Todo.objects.create(title="Old Title", username="alice")

    url = reverse("todo:todo_list")
    response = client.post(url, {
        "edit_task": "",
        "task_id": todo.id,
        "new_title": "Updated Title"
    })

    assert response.status_code == 302
    todo.refresh_from_db()
    assert todo.title == "Updated Title"


@pytest.mark.django_db
def test_check_task_toggle(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    todo = Todo.objects.create(title="Check me", username="alice", checkbox=False)

    url = reverse("todo:todo_list")
    # Toggle to complete
    client.post(url, {"check_task": "", "task_id": todo.id})
    todo.refresh_from_db()
    assert todo.checkbox is True
    assert todo.completed_at is not None

    # Toggle back to incomplete
    client.post(url, {"check_task": "", "task_id": todo.id})
    todo.refresh_from_db()
    assert todo.checkbox is False
    assert todo.completed_at is None


@pytest.mark.django_db
def test_change_priority(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    todo = Todo.objects.create(title="Prioritize me", username="alice", priority=1)

    url = reverse("todo:todo_list")
    response = client.post(url, {
        "change_priority": "",
        "task_id": todo.id,
        "priority": "3"
    })

    assert response.status_code == 302
    todo.refresh_from_db()
    assert todo.priority == 3


@pytest.mark.django_db
def test_delete_task(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    todo = Todo.objects.create(title="Delete me", username="alice")

    url = reverse("todo:todo_list")
    response = client.post(url, {"delete_task": "", "task_id": todo.id})

    assert response.status_code == 302
    assert not Todo.objects.filter(id=todo.id).exists()


@pytest.mark.django_db
def test_clear_all_tasks(client):
    session = client.session
    session["username"] = "alice"
    session.save()

    Todo.objects.create(title="Task A", username="alice")
    Todo.objects.create(title="Task B", username="alice")
    Todo.objects.create(title="Bob's Task", username="bob")  # Should not be deleted

    url = reverse("todo:todo_list")
    response = client.post(url, {"clear_all": ""})

    assert response.status_code == 302
    assert Todo.objects.filter(username="alice").count() == 0
    assert Todo.objects.filter(username="bob").count() == 1