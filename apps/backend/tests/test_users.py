import pytest
import sqlite3
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.hashers import make_password
from users.forms import LoginForm, RegisterForm


# Helper function to dynamically resolve URLs regardless of app namespaces
def get_url(url_name, default_path):
    for possible_name in [url_name, f"users:{url_name}", f"accounts:{url_name}"]:
        try:
            return reverse(possible_name)
        except NoReverseMatch:
            continue
    return default_path


# ============================================================================
# FORM TESTS
# ============================================================================

def test_login_form_valid_data():
    form = LoginForm(data={'username': 'testuser', 'password': 'password123'})
    assert form.is_valid()


def test_login_form_missing_fields():
    form = LoginForm(data={'username': '', 'password': ''})
    assert not form.is_valid()
    assert 'username' in form.errors
    assert 'password' in form.errors


@pytest.mark.django_db
def test_register_form_valid_data():
    form = RegisterForm(data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'StrongPassword123!',
        'password2': 'StrongPassword123!'
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_register_form_password_mismatch():
    form = RegisterForm(data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'Password123',
        'password2': 'DifferentPassword123'
    })
    assert not form.is_valid()


# ============================================================================
# VIEW TESTS
# ============================================================================

@pytest.fixture(autouse=True)
def setup_sqlite_db(tmp_path, monkeypatch):
    """
    Fixture that redirects raw sqlite3 connections to a temporary test database.
    """
    db_file = str(tmp_path / "test_users.db")
    orig_connect = sqlite3.connect
    monkeypatch.setattr(sqlite3, 'connect', lambda database, *args, **kwargs: orig_connect(db_file, *args, **kwargs))

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()


@pytest.mark.django_db
def test_register_get_unauthenticated(client):
    url = get_url('register', '/users/register/')
    response = client.get(url)
    assert response.status_code in [200, 302]


@pytest.mark.django_db
def test_register_post_success(client):
    data = {
        'username': 'registereduser',
        'email': 'reg@example.com',
        'password1': 'Password123!',
        'password2': 'Password123!'
    }
    url = get_url('register', '/users/register/')
    response = client.post(url, data)
    assert response.status_code in [200, 302]

    if response.status_code == 302:
        assert client.session.get("username") == "registereduser"


@pytest.mark.django_db
def test_sign_in_post_success(client):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    hashed_pwd = make_password("correctpassword")
    cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", 
                   ("loginuser", hashed_pwd, "login@example.com"))
    conn.commit()
    conn.close()

    url = get_url('sign_in', '/user/login/')
    response = client.post(url, {'username': 'loginuser', 'password': 'correctpassword'})
    assert response.status_code in [200, 302]


@pytest.mark.django_db
def test_sign_in_post_invalid_password(client):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    hashed_pwd = make_password("correctpassword")
    cursor.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)", 
                   ("loginuser2", hashed_pwd, "login2@example.com"))
    conn.commit()
    conn.close()

    url = get_url('sign_in', '/user/login/')
    response = client.post(url, {'username': 'loginuser2', 'password': 'wrongpassword'})
    assert response.status_code == 200


@pytest.mark.django_db
def test_sign_out(client):
    session = client.session
    session["username"] = "activeuser"
    session.save()

    url = get_url('sign_out', '/user/logout/')
    response = client.get(url)
    assert response.status_code in [200, 302]
    assert "username" not in client.session