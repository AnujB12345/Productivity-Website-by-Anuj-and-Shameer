from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.db.models.functions import TruncMonth
import json

from todo.models import Todo
from notes.models import Note
from calendar_app.models import CalendarEvent  # ⚠️ adjust to your actual app name/path


def dashboard(request):
    username = request.session.get("username")
    if not username:
        return redirect("users:login")

    now = timezone.now()
    today = now.date()

    # --- Rolling 7-day windows for week-over-week comparison ---
    week_0_start = now - timedelta(days=7)
    week_1_start = now - timedelta(days=14)

    tasks_this_week = Todo.objects.filter(username=username, completed_at__gte=week_0_start).count()
    tasks_last_week = Todo.objects.filter(
        username=username, completed_at__gte=week_1_start, completed_at__lt=week_0_start
    ).count()

    notes_this_week = Note.objects.filter(username=username, created_at__gte=week_0_start).count()
    notes_last_week = Note.objects.filter(
        username=username, created_at__gte=week_1_start, created_at__lt=week_0_start
    ).count()

    def pct_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round(((current - previous) / previous) * 100)

    tasks_change = pct_change(tasks_this_week, tasks_last_week)
    notes_change = pct_change(notes_this_week, notes_last_week)

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

    # --- Year-so-far chart: monthly totals ---
    year = today.year

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

    chart_data = {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "tasks": monthly_counts(Todo.objects.filter(username=username, checkbox=True), "completed_at"),
        "notes": monthly_counts(Note.objects.filter(username=username), "created_at"),
        "events": monthly_counts(CalendarEvent.objects.filter(username=username), "date"),
    }

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
        "chart_data": json.dumps(chart_data),
    })