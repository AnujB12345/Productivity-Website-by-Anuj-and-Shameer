from django.shortcuts import render, redirect, get_object_or_404
from .models import Note

def notes(request):

    if not request.session.get("username"):
        return redirect("users:login")

    notes = Note.objects.filter(username=request.session["username"])

    if request.method == "POST":

        if "add_note" in request.POST:
            title = request.POST.get("title")
            description = request.POST.get("description")
            if description is None:
                description = ""
            if title:
                Note.objects.create(title=title, description=description, username=request.session["username"])
            return redirect("notes:notes")
        
        if "edit_note" in request.POST:
            note_id = request.POST.get("note_id")
            new_title = request.POST.get("new_title")
            new_description = request.POST.get("new_description")
            note = get_object_or_404(Note, id=note_id, username=request.session["username"])
            note.title = new_title
            note.description = new_description
            if new_description is None:
                note.description = ""
            if not new_title:
                new_title = note.title
            note.save()
            return redirect("notes:notes")
        
        if "delete_note" in request.POST:
            note_id = request.POST.get("note_id")
            note = get_object_or_404(Note, id=note_id, username=request.session["username"])
            note.delete()
            return redirect("notes:notes")
        
        if "clear_all" in request.POST:
            Note.objects.all().delete()
            return redirect("notes:notes")
        
    return render(request, "notes.html", {
        "notes": notes,
        "note_count": notes.count()
    })