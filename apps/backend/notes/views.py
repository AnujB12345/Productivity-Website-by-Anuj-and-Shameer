from django.shortcuts import render, redirect, get_object_or_404
from notes.models import Note
from users.models import User

def notes(request):
    if not request.session.get("username"):
        return redirect("users:login")

    current_user = User.objects.get(username=request.session["username"])

    notes = Note.objects.filter(user = current_user)
    subjects = list(Note.objects.values_list("subject", flat=True).filter(user = current_user).distinct())

    if request.method == "POST":

        #Handles adding a new revision note
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
                    existing_note = Note.objects.filter(subject=subject, user = current_user).first()
                    if existing_note:
                        subject_colour = existing_note.subject_colour
                    else:
                        subject_colour = "#000000"  # Default color is black
                else:   
                    subject_colour = "#000000"
            if title:
                Note.objects.create(title=title, description=description, subject=subject, subject_colour=subject_colour, user = current_user)
            return redirect("notes:notes")

        #Handles editing the notes
        #Handles editing the notes
    if "edit_note" in request.POST:
        note_id = request.POST.get("note_id")
        new_title = request.POST.get("new_title")
        new_description = request.POST.get("new_description") or ""
        new_subject = request.POST.get("new_subject") or ""
        new_subject_colour = request.POST.get("new_subject_colour")

        note = get_object_or_404(Note, id=note_id, user=current_user)

        old_subject = note.subject
        subject_changed = new_subject != old_subject

        note.title = new_title or note.title
        note.description = new_description

        if subject_changed:
            note.subject = new_subject

            if new_subject:
                existing_note = Note.objects.filter(
                    user=current_user, subject=new_subject
                ).exclude(id=note.id).first()

                if existing_note:
                    note.subject_colour = existing_note.subject_colour
                else:
                    # Starting a brand new subject group - use whatever colour
                    # was submitted (or fall back to current colour/black).
                    note.subject_colour = new_subject_colour or note.subject_colour
            else:
                # Cleared the subject entirely - just keep/accept the submitted colour.
                note.subject_colour = new_subject_colour or note.subject_colour

            note.save()

        else:
            # Subject unchanged - a colour change here means "recolour this
            # whole subject group", so apply it to every note sharing this subject.
            note.subject_colour = new_subject_colour or note.subject_colour
            note.save()

            if old_subject:
                Note.objects.filter(
                    user=current_user, subject=old_subject
                ).exclude(id=note.id).update(
                    subject_colour=note.subject_colour,
                )

        return redirect("notes:notes")

        #Handles deletion of notes
        if "delete_note" in request.POST:
            note_id = request.POST.get("note_id")
            note = get_object_or_404(Note, id=note_id, user = current_user)
            note.delete()
            return redirect("notes:notes")

        
    return render(request, "revision_notes_page.html", {
        "notes": notes,
        "note_count": notes.count(),
        "subjects": subjects
    })