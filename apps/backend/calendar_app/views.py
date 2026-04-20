from django.shortcuts import render, redirect, get_object_or_404
from .models import CalendarEvent
import calendar
import datetime


def calendar_event(request):

    username = request.session.get("username")
    if not username:
        return redirect("users:login")

    month = request.GET.get("month")
    year = request.GET.get("year")

    today = datetime.date.today()

    year = int(year) if year else today.year
    month = int(month) if month else today.month

    cal = calendar.monthcalendar(year, month)

    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1


    selected_date = request.GET.get("date")
    selected_date_obj = None

    if selected_date:
        try:
            selected_date_obj = datetime.datetime.strptime(
                selected_date, "%Y-%m-%d"
            ).date()
        except:
            selected_date_obj = None

    if selected_date_obj:
        events = CalendarEvent.objects.filter(
            username=username,
            date=selected_date_obj
        )
    else:
        events = CalendarEvent.objects.filter(username=username)


    if request.method == "POST":

        if "add_event" in request.POST:
            CalendarEvent.objects.create(
                title=request.POST.get("title"),
                username=username,
                description=request.POST.get("description"),
                date=request.POST.get("date"),
                time=request.POST.get("time")
            )
            return redirect(request.path)

        if "edit_event" in request.POST:
            event_id = request.POST.get("event_id")
            event = get_object_or_404(CalendarEvent, id=event_id, username=username)

            event.title = request.POST.get("title")
            event.description = request.POST.get("description")
            event.date = request.POST.get("date")
            event.time = request.POST.get("time")
            event.save()

            return redirect(request.path)

        if "delete_event" in request.POST:
            event_id = request.POST.get("event_id")
            event = get_object_or_404(CalendarEvent, id=event_id, username=username)
            event.delete()

            return redirect(request.path)


    return render(request, "calendar.html", {
        "calendar": cal,
        "year": year,
        "month": month,
        "events": events,
        "selected_date": selected_date,
        "next_month": next_month,
        "next_year": next_year,
        "prev_month": prev_month,
        "prev_year": prev_year,
    })