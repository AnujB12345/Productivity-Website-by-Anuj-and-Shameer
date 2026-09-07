from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Todo

def todo_list(request):

    if not request.session.get("username"):
        return redirect("users:login")

    todos = Todo.objects.filter(username=request.session["username"]).order_by('checkbox', '-priority')

    if request.method == "POST":

        if "add_task" in request.POST:
            title = request.POST.get("title")
            if title:
                Todo.objects.create(title=title, username=request.session["username"])
            return redirect("todo:todo_list")

        if "edit_task" in request.POST:
            task_id = request.POST.get("task_id")
            new_title = request.POST.get("new_title")
            todo = get_object_or_404(Todo, id=task_id, username=request.session["username"])
            todo.title = new_title
            todo.save()
            return redirect("todo:todo_list")

        if "check_task" in request.POST:
            task_id = request.POST.get("task_id")
            todo = get_object_or_404(Todo, id=task_id, username=request.session["username"])
            todo.checkbox = not todo.checkbox
            todo.completed_at = timezone.now() if todo.checkbox else None
            todo.save()
            return redirect("todo:todo_list")

        if "change_priority" in request.POST:
            task_id = request.POST.get("task_id")
            priority = request.POST.get("priority")
            todo = get_object_or_404(Todo, id=task_id, username=request.session["username"])
            todo.priority = int(priority)
            todo.save()
            return redirect("todo:todo_list")

        if "delete_task" in request.POST:
            task_id = request.POST.get("task_id")
            todo = get_object_or_404(Todo, id=task_id, username=request.session["username"])
            todo.delete()
            return redirect("todo:todo_list")

        if "clear_all" in request.POST:
            Todo.objects.filter(username=request.session["username"]).delete()
            return redirect("todo:todo_list")

    todos = list(todos)
    active_todos = [t for t in todos if not t.checkbox]
    done_todos = [t for t in todos if t.checkbox]

    return render(request, "to_do_list_page.html", {
        "active_todos": active_todos,
        "done_todos": done_todos,
        "task_count": len(todos),
        "checked_count": len(done_todos),
    })