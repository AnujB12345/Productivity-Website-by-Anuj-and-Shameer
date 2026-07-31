from django.shortcuts import render, HttpResponse


# Create your views here.

def home(request):
    try:
        if request.session["username"] is None:
            return render(request, "home_page.html")
        else:
            return render(request, "dashboard_page.html")
    except:
        return render(request, "home_page.html")
        # return redirect("dashboard:dashboard")

# def about(request):
#     return HttpResponse("About Page")

