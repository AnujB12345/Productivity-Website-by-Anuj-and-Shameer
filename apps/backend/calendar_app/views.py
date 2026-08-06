from django.shortcuts import render, redirect, get_object_or_404
from .models import CalendarEvent
import calendar
import datetime


def calendar_event(request):

    username = request.session.get("username")
    if not username:
        return redirect("users:login")
    #if user isn't signed in, they get redirected to the login page

    month = request.GET.get("month")
    year = request.GET.get("year")
    #reads the url and retrieves the month and year

    today = datetime.date.today() #Date object representing today's date

    year = int(year) if year else today.year
    month = int(month) if month else today.month
    month_name = calendar.month_name[month]

    cal = calendar.monthcalendar(year, month)
    #generates the month's calendar

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


    event_count = 0

    selected_date = request.GET.get("date") #retrieves the date from the url
    selected_date_obj = None

    if selected_date:
        try:
            selected_date_obj = datetime.datetime.strptime( #converts the string into an actual date object
                selected_date, "%Y-%m-%d"
            ).date()
        except:
            selected_date_obj = None #ignore if invalid date


    calendar_events = CalendarEvent.objects.filter(username=username) #filters all of the events based on the username

    if selected_date_obj:
        selected_date_events = CalendarEvent.objects.filter( #searches the database and filters all the events for a certain date that has been selected
            username=username,
            date=selected_date_obj
        )
        event_count += len(selected_date_events)
        #returns every event for the user if no date selected
    else:
        selected_date_events = CalendarEvent.objects.filter(username=username)


    if request.method == "POST": #when user submits an event, a POST request is sent

        #ADD A NEW EVENT
        if "add_event" in request.POST:
            #creates a new database row with all of the information for the new event
            CalendarEvent.objects.create( 
                title=request.POST.get("title"),
                username=username,
                description=request.POST.get("description"),
                date=request.POST.get("date"),
                time=request.POST.get("time")
            )
            event_count += 1
            return redirect(request.path)

        #EDIT AN EXISTING EVENT
        if "edit_event" in request.POST: #if user sends an edit event request
            event_id = request.POST.get("event_id") #retreives the event to edit from event id
            event = get_object_or_404(CalendarEvent, id=event_id, username=username)

            event.title = request.POST.get("title")
            event.description = request.POST.get("description")
            event.date = request.POST.get("date")
            event.time = request.POST.get("time")
            #makes all the edits
            event.save()

            return redirect(request.path)

        #DELETING AN EVENT
        if "delete_event" in request.POST:
            event_id = request.POST.get("event_id") #finds the edit to delete using the event ID
            event = get_object_or_404(CalendarEvent, id=event_id, username=username)
            event.delete() #permanently remove it from the database

            event_count -= 1

            return redirect(request.path)


    return render(request, "calendar_page.html", {
        "calendar": cal,
        "today": today,
        "year": year,
        "month": month,
        "month_name": month_name,
        # "events": events,
        "selected_date_events": selected_date_events,
        "calendar_events": calendar_events,
        "event_count": event_count,
        "selected_date": selected_date,
        "next_month": next_month,
        "next_year": next_year,
        "prev_month": prev_month,
        "prev_year": prev_year,
    })
    #the render function sends all of the variables within views.py to HTML template