import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_logged_in_renders_dashboard(client):
    """When username exists in session, renders dashboard_page.html."""
    session = client.session
    session["username"] = "alice"
    session.save()

    url = reverse("home")  # Adjust URL name if different in your urls.py
    response = client.get(url)

    assert response.status_code == 200
    assert "dashboard_page.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_home_logged_out_none_username_renders_homepage(client):
    """When session['username'] is None, renders home_page.html."""
    session = client.session
    session["username"] = None
    session.save()

    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    assert "home_page.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_home_missing_session_key_renders_homepage(client):
    """When 'username' key is missing, KeyError triggers except block and renders home_page.html."""
    url = reverse("home")
    response = client.get(url)

    assert response.status_code == 200
    assert "home_page.html" in [t.name for t in response.templates]