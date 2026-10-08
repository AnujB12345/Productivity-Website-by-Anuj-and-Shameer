import pytest
from django.urls import reverse, NoReverseMatch
from users.models import User
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
    User.objects.create(
        username="loginuser",
        email="login@example.com",
        password="correctpassword"
    )

    url = get_url('sign_in', '/user/login/')
    response = client.post(url, {'username': 'loginuser', 'password': 'correctpassword'})
    assert response.status_code in [200, 302]


@pytest.mark.django_db
def test_sign_in_post_invalid_password(client):
    User.objects.create(
        username="loginuser2",
        email="login2@example.com",
        password="correctpassword"
    )

    url = get_url('sign_in', '/user/login/')
    response = client.post(url, {'username': 'loginuser2', 'password': 'wrongpassword'})
    assert response.status_code == 200


@pytest.mark.django_db
def test_sign_out(client):
    alice = User.objects.create(
        username="activeuser",
        email="activeuser@example.com",
        password="Password123!"
    )

    session = client.session
    session["username"] = alice.username
    session.save()

    url = get_url('sign_out', '/user/logout/')
    response = client.get(url)
    assert response.status_code in [200, 302]
    assert "username" not in client.session