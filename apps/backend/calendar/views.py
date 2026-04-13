from django.shortcuts import render

# Create your views here.

def calendar_view(request):
    return render(request, "home.html")


def add_event(request):
    events = CalendarEvent.objects.filter(username=request.session["username"])

    if request.method == "POST":

        if "add_event" in request.POST:
            title = request.POST.get("title")
            if title:
                Todo.objects.create(title=title, username=request.session["username"])
            return redirect("todo:todo_list")
        
        if "edit_task" in request.POST:
            task_id = request.POST.get("task_id")
            new_title = request.POST.get("new_title")
            todo = get_object_or_404(Todo, id=task_id)
            todo.title = new_title
            todo.save()
            return redirect("todo:todo_list")
        
        if "check_task" in request.POST:
            task_id = request.POST.get("task_id")
            todo = get_object_or_404(Todo, id=task_id)
            todo.checkbox = not todo.checkbox
            todo.save()
            return redirect("todo:todo_list")
        if "delete_task" in request.POST:
            task_id = request.POST.get("task_id")
            todo = get_object_or_404(Todo, id=task_id)
            todo.delete()
            return redirect("todo:todo_list")
        
        if "clear_all" in request.POST:
            Todo.objects.all().delete()
            return redirect("todo:todo_list")
        
    return render(request, "list.html", {
        "todos": todos,
        "task_count": todos.count()
    })