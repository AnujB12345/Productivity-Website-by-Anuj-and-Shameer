from django.shortcuts import render, redirect, get_object_or_404
from .models import Note

def notes(request):

    if not request.session.get("username"):
        return redirect("users:login")

    notes = Note.objects.filter(username=request.session["username"])
    subjects = list(Note.objects.values_list("subject", flat=True).filter(username=request.session["username"]).distinct())

    if request.method == "POST":

        if "add_note" in request.POST:
            title = request.POST.get("title")
            description = request.POST.get("description")
            subject = request.POST.get("subject")
            subject_colour = request.POST.get("subject_colour")
            if description is None:
                description = ""
            if subject is None:
                subject = ""
            if subject_colour is None:
                if subject:
                    # If a subject is provided but no color, check if the subject already exists and use its color
                    existing_note = Note.objects.filter(subject=subject, username=request.session["username"]).first()
                    if existing_note:
                        subject_colour = existing_note.subject_colour
                    else:
                        subject_colour = "#000000"  # Default color is black
                else:   
                    subject_colour = "#000000"
            if title:
                Note.objects.create(title=title, description=description, subject=subject, subject_colour=subject_colour, username=request.session["username"])
            return redirect("notes:notes")
        
        if "edit_note" in request.POST:
            note_id = request.POST.get("note_id")
            new_title = request.POST.get("new_title")
            new_description = request.POST.get("new_description")
            new_subject = request.POST.get("new_subject")
            new_subject_colour = request.POST.get("new_subject_colour")
            note = get_object_or_404(Note, id=note_id, username=request.session["username"])
            note.title = new_title
            note.description = new_description
            note.subject = new_subject
            note.subject_colour = new_subject_colour or note.subject_colour
            for note in notes:
                if note.subject == new_subject and note.id != note_id:
                    note.subject_colour = new_subject_colour or note.subject_colour
                    note.save()
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
        
    return render(request, "revision_notes_page.html", {
        "notes": notes,
        "note_count": notes.count(),
        "subjects": subjects
    })