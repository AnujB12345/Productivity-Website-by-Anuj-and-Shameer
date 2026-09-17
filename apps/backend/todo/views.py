from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField
from .models import Todo
from users.models import User

def todo_list(request):

    #If user is not logged in, redirect to the login page
    if not request.session.get("username"):
        return redirect("users:login")

    current_user = User.objects.get(username=request.session["username"])

    #Used to rank the priority of the tasks for ordering
    priority_rank = Case(
        When(priority='High', then=Value(0)),
        When(priority='Medium', then=Value(1)),
        When(priority='Low', then=Value(2)),
        output_field=IntegerField(),
    )
    todos = Todo.objects.filter(user=current_user).order_by('checked', priority_rank)

    if request.method == "POST":

        #Handles add task
        if "add_task" in request.POST:
            title = request.POST.get("title")
            if title:
                Todo.objects.create(title=title, user=current_user)
            return redirect("todo:todo_list")

        #Handles edit task
        if "edit_task" in request.POST:
            task_id = request.POST.get("task_id")
            new_title = request.POST.get("new_title")
            todo = get_object_or_404(Todo, id=task_id, user=current_user)
            todo.title = new_title
            todo.save()
            return redirect("todo:todo_list")

        #Handles checking the task complete/ not complete
        if "check_task" in request.POST:
            task_id = request.POST.get("task_id")
            todo = get_object_or_404(Todo, id=task_id, user=current_user)
            todo.checked = not todo.checked
            todo.completed_at = timezone.now() if todo.checked else None
            todo.save()
            return redirect("todo:todo_list")

        #Handles changing the priority of the task
        if "change_priority" in request.POST:
            task_id = request.POST.get("task_id")
            priority = request.POST.get("priority")
            todo = get_object_or_404(Todo, id=task_id, user=current_user)
            todo.priority = str(priority)
            todo.save()
            return redirect("todo:todo_list")

        #Handles deleting the task
        if "delete_task" in request.POST:
            task_id = request.POST.get("task_id")
            todo = get_object_or_404(Todo, id=task_id, user=current_user)
            todo.delete()
            return redirect("todo:todo_list")

        #Deletes all the task matching the user
        if "clear_all" in request.POST:
            Todo.objects.filter(user=current_user).delete()
            return redirect("todo:todo_list")

    # Separate active and completed tasks for display
    todos = list(todos)
    active_todos = [t for t in todos if not t.checked]
    done_todos = [t for t in todos if t.checked]

    return render(request, "to_do_list_page.html", {
        "active_todos": active_todos,
        "done_todos": done_todos,
        "task_count": len(todos),
        "checked_count": len(done_todos),
    })