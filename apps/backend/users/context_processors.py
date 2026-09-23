def current_user(request):
    """Makes the logged-in User object available in every template as {{ current_user }}."""
    username = request.session.get("username")
    if not username:
        return {}

    from users.models import User  # imported here, not at module level, to avoid AppRegistryNotReady

    try:
        return {"current_user": User.objects.get(username=username)}
    except User.DoesNotExist:
        return {}