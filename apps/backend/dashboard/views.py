from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
import json

from todo.models import Todo
from notes.models import Note
from calendar_app.models import CalendarEvent  # ⚠️ adjust to your actual app path
from dashboard.models import Goal
from timer.models import PomodoroSession

import requests
from django.http import JsonResponse
from django.core.cache import cache
def dashboard(request):
    username = request.session.get("username")
    if not username:
        return redirect("users:login")

    # Handle goal updates
    if request.method == "POST" and ("update_goal" in request.POST or "update_pomodoro_goal" in request.POST):
        goal_obj, _ = Goal.objects.get_or_create(username=username)

        if "update_goal" in request.POST:
            new_goal = request.POST.get("notes_goal")
            if new_goal and new_goal.isdigit() and int(new_goal) > 0:
                goal_obj.notes_goal = int(new_goal)
        else:
            new_pomo_goal = request.POST.get("pomodoro_goal")
            if new_pomo_goal and new_pomo_goal.isdigit() and int(new_pomo_goal) > 0:
                goal_obj.pomodoro_goal = int(new_pomo_goal)

        goal_obj.save()
        return redirect("dashboard:dashboard")

    # --- Time calculations ---
    now = timezone.now()
    today = now.date()
    month_start = today.replace(day=1)

    # --- Rolling 7-day windows for week-over-week comparison ---
    week_0_start = now - timedelta(days=7)
    week_1_start = now - timedelta(days=14)

    # --- Week-over-week stats ---
    tasks_this_week = Todo.objects.filter(username=username, completed_at__gte=week_0_start).count()
    tasks_last_week = Todo.objects.filter(
        username=username, completed_at__gte=week_1_start, completed_at__lt=week_0_start
    ).count()

    notes_this_week = Note.objects.filter(username=username, created_at__gte=week_0_start).count()
    notes_last_week = Note.objects.filter(
        username=username, created_at__gte=week_1_start, created_at__lt=week_0_start
    ).count()

    # Only "work" sessions count as focus sessions — short/long breaks don't.
    pomodoro_sessions_this_week = PomodoroSession.objects.filter(
        username=username, session_type="work", completed_at__gte=week_0_start
    ).count()
    pomodoro_sessions_last_week = PomodoroSession.objects.filter(
        username=username, session_type="work", completed_at__gte=week_1_start, completed_at__lt=week_0_start
    ).count()

    # --- Percentage change calculations ---
    def pct_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100)

    # --- Percentage changes stored ---
    tasks_change = pct_change(tasks_this_week, tasks_last_week)
    notes_change = pct_change(notes_this_week, notes_last_week)
    pomodoro_change = pct_change(pomodoro_sessions_this_week, pomodoro_sessions_last_week)

    # --- Calendar: done in last 30 days / upcoming in next 30 days ---
    month_ago = today - timedelta(days=30)
    month_ahead = today + timedelta(days=30)

    events_done_last_month = CalendarEvent.objects.filter(
        username=username, date__gte=month_ago, date__lt=today
    ).count()
    events_upcoming = CalendarEvent.objects.filter(
        username=username, date__gte=today, date__lte=month_ahead
    ).count()

    # --- Extra stats ---
    total_tasks = Todo.objects.filter(username=username).count()
    total_completed_tasks = Todo.objects.filter(username=username, checkbox=True).count()
    completion_rate = round((total_completed_tasks / total_tasks) * 100) if total_tasks else 0
    total_notes = Note.objects.filter(username=username).count()

    focus_minutes_this_week = PomodoroSession.objects.filter(
        username=username, session_type="work", completed_at__gte=week_0_start
    ).aggregate(total=Sum("duration_minutes"))["total"] or 0

    # --- Task reminder widget: top 3 highest-priority incomplete tasks ---
    incomplete_tasks = Todo.objects.filter(username=username, checkbox=False)
    tasks_remaining = incomplete_tasks.count()
    top_tasks = incomplete_tasks.order_by('-priority', 'id')[:3]

    # --- Progress tracker ---
    tasks_completed_this_month = Todo.objects.filter(
        username=username, checkbox=True, completed_at__gte=month_start
    ).count()
    tasks_progress_pct = round((tasks_completed_this_month / total_tasks) * 100) if total_tasks else 0

    # --- Notes, events and pomodoro progress tracker ---
    goal_obj, _ = Goal.objects.get_or_create(username=username)
    notes_created_this_month = Note.objects.filter(username=username, created_at__gte=month_start).count()
    notes_progress_pct = min(round((notes_created_this_month / goal_obj.notes_goal) * 100), 100) if goal_obj.notes_goal else 0

    events_this_month_total = CalendarEvent.objects.filter(
        username=username, date__year=today.year, date__month=today.month
    ).count()
    events_this_month_done = CalendarEvent.objects.filter(
        username=username, date__year=today.year, date__month=today.month, date__lt=today
    ).count()
    events_progress_pct = round((events_this_month_done / events_this_month_total) * 100) if events_this_month_total else 0

    pomodoro_sessions_this_month = PomodoroSession.objects.filter(
        username=username, session_type="work", completed_at__gte=month_start
    ).count()
    pomodoro_progress_pct = min(round((pomodoro_sessions_this_month / goal_obj.pomodoro_goal) * 100), 100) if goal_obj.pomodoro_goal else 0

    # --- Year-so-far chart: monthly totals ---
    year = today.year

    # --- Helper function to get monthly counts for tasks, notes, events and pomodoro sessions for the year for the chart ---
    def monthly_counts(queryset, date_field):
        counts = {m: 0 for m in range(1, 13)}
        annotated = (
            queryset.filter(**{f"{date_field}__year": year})
            .annotate(month=TruncMonth(date_field))
            .values("month")
            .annotate(total=Count("id"))
        )
        for row in annotated:
            counts[row["month"].month] = row["total"]
        return [counts[m] for m in range(1, 13)]

    # --- Prepare chart data for tasks, notes, events and pomodoro sessions ---
    chart_data = {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "tasks": monthly_counts(Todo.objects.filter(username=username, checkbox=True), "completed_at"),
        "notes": monthly_counts(Note.objects.filter(username=username), "created_at"),
        "events": monthly_counts(CalendarEvent.objects.filter(username=username), "date"),
        "pomodoro": monthly_counts(
            PomodoroSession.objects.filter(username=username, session_type="work"), "completed_at"
        ),
    }

    # --- Render the dashboard template with all the calculated stats and data ---
    return render(request, "dashboard_page.html", {
        "tasks_this_week": tasks_this_week,
        "tasks_last_week": tasks_last_week,
        "tasks_change": tasks_change,
        "notes_this_week": notes_this_week,
        "notes_last_week": notes_last_week,
        "notes_change": notes_change,
        "events_done_last_month": events_done_last_month,
        "events_upcoming": events_upcoming,
        "total_tasks": total_tasks,
        "completion_rate": completion_rate,
        "total_notes": total_notes,
        "chart_data": chart_data,

        "pomodoro_sessions_this_week": pomodoro_sessions_this_week,
        "pomodoro_sessions_last_week": pomodoro_sessions_last_week,
        "pomodoro_change": pomodoro_change,
        "focus_minutes_this_week": focus_minutes_this_week,

        "tasks_remaining": tasks_remaining,
        "top_tasks": top_tasks,

        "tasks_progress_pct": tasks_progress_pct,
        "tasks_completed_this_month": tasks_completed_this_month,
        "notes_progress_pct": notes_progress_pct,
        "notes_created_this_month": notes_created_this_month,
        "notes_goal": goal_obj.notes_goal,
        "pomodoro_goal": goal_obj.pomodoro_goal,
        "pomodoro_progress_pct": pomodoro_progress_pct,
        "pomodoro_sessions_this_month": pomodoro_sessions_this_month,
        "events_progress_pct": events_progress_pct,
        "events_this_month_done": events_this_month_done,
        "events_this_month_total": events_this_month_total,
    })


def quote(request):

    cached_quote = cache.get("daily_quote")

    if cached_quote:
        return JsonResponse(cached_quote)

    response = requests.get("https://zenquotes.io/api/random")

    data = response.json()

    quote_data = {
        "quote": data[0]["q"],
        "author": data[0]["a"]
    }

    cache.set("daily_quote", quote_data, 86400)

    return JsonResponse(quote_data)