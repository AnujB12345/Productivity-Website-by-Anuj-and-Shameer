import time

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from .forms import LoginForm, RegisterForm
from users.models import User

def register(request):
    if request.method == 'GET': #If the user is asking to visit the page
        if request.session.get("username"): #Redirect to the dashboard if user is already logged in
            return redirect("dashboard:dashboard")
        form = RegisterForm() #Creates an empty form
        return render(request, 'register_page.html', {'form': form})    
   
    if request.method == 'POST':
        form = RegisterForm(request.POST) 
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password1']) #Hashes the password for security

            #If the username already exists in the database, don't save it to the database and re-prompt
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                    messages.error(request, "Username or email already exists")
                    return render(request, "register_page.html", {"form": form})

            User.objects.create(
                username=username,
                email=email,
                password=password,
            )

            request.session["username"] = username #Logs the newly registered user in
            return redirect("dashboard:dashboard") #redirects to the dashboard after account is successfully created
        
        else:
            return render(request, 'register_page.html', {'form': form})
            

def sign_in(request):
    # list(messages.get_messages(request))
    if request.method == 'GET':
        if request.session.get("username"):
            return redirect("dashboard:dashboard")
        form = LoginForm() #Creates an empty login form
        return render(request,'login_page.html', {'form': form})
    
    elif request.method == 'POST': #If the user has submitted the login form
        form = LoginForm(request.POST)
        
        if form.is_valid(): #Checks if the form's data is valid
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                user = User.objects.get(username = username)
            except User.DoesNotExist:
                messages.error(request, "Username does not exist, please try again!")  #If user enters a username that hasn't been registered onto the system
                return render(request, "login_page.html", {"form": form})

            if check_password(password, user.password): #Checks if the entered password matches the password that we get from the database matching to the entered username
                request.session["username"] = username
                return redirect("dashboard:dashboard")
            else:
                messages.error(request,"Invalid password, please try again!") #If user enters a valid username but incorrect password
        
        return render(request,'login_page.html',{'form': form})
        
    
def sign_out(request):
    request.session.flush()
    return redirect("/") #redirects to the homepage after you sign out