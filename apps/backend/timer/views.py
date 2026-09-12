from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from users.models import User
from timer.models import PomodoroSettings, PomodoroSession
import json

def timer(request):

    if not request.session.get("username"):
        return redirect("users:login")

    current_user = User.objects.get(username=request.session["username"])

    settings_obj, _ = PomodoroSettings.objects.get_or_create(user=current_user)

    if request.method == "POST":
        #Handles updates to the timer settings
        if "update_settings" in request.POST:
            def _clean_int(field, current, minimum, maximum):
                raw = request.POST.get(field)
                if raw and raw.isdigit():
                    return max(minimum, min(int(raw), maximum))
                return current

            settings_obj.work_minutes = _clean_int("work_minutes", settings_obj.work_minutes, 1, 120)
            settings_obj.short_break_minutes = _clean_int("short_break_minutes", settings_obj.short_break_minutes, 1, 60)
            settings_obj.long_break_minutes = _clean_int("long_break_minutes", settings_obj.long_break_minutes, 1, 60)
            settings_obj.sessions_before_long_break = _clean_int("sessions_before_long_break", settings_obj.sessions_before_long_break, 2, 12)
            settings_obj.save()
            return redirect("timer:timer")

        if "log_session" in request.POST:
            # Called via fetch() from the timer JS when a session completes —
            # returns JSON rather than redirecting, since the page must NOT reload (that would reset the running timer's JS state).
            session_type = request.POST.get("session_type")
            duration = request.POST.get("duration_minutes")
            task_label = request.POST.get("task_label", "").strip()[:200]

            valid_types = dict(PomodoroSession.SESSION_TYPES)
            if session_type in valid_types and duration and duration.isdigit():
                PomodoroSession.objects.create(
                    user =current_user,
                    session_type=session_type,
                    duration_minutes=int(duration),
                    task_label=task_label,
                )
                return JsonResponse({"status": "ok"})
            return JsonResponse({"status": "error"}, status=400)

        #Handles deletion of a pomodoro session
        if "delete_session" in request.POST:
            session_id = request.POST.get("session_id")
            PomodoroSession.objects.filter(id=session_id, user =current_user).delete()
            return redirect("timer:timer")

    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    todays_work_sessions = PomodoroSession.objects.filter(
        user =current_user, session_type="work", completed_at__gte=today_start
    )
    sessions_today = todays_work_sessions.count()
    focus_minutes_today = sum(s.duration_minutes for s in todays_work_sessions)

    recent_sessions = PomodoroSession.objects.filter(user =current_user)[0:10] #Returns the 10 recent sessions



    settings_dict = {
    "work_minutes": settings_obj.work_minutes,
    "short_break_minutes": settings_obj.short_break_minutes,
    "long_break_minutes": settings_obj.long_break_minutes,
    "sessions_before_long_break": settings_obj.sessions_before_long_break,
}

    return render(request, "timer_page.html", {
        "settings": settings_obj,
        "settings_dict": settings_dict,  
        "sessions_today": sessions_today,
        "focus_minutes_today": focus_minutes_today,
        "recent_sessions": recent_sessions,
    })