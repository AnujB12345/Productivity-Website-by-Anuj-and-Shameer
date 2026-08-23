import time

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password, check_password
from .forms import LoginForm, RegisterForm
import sqlite3

def register(request):
    if request.method == 'GET': #If the user is asking to visit the page
        try:
            if request.session["username"] is not None: #Redirect to the dashboard if user is already logged in
                        return redirect("dashboard:dashboard")
        except:
            form = RegisterForm() #Creates an empty form
            return render(request, 'register_page.html', {'form': form})    
   
    if request.method == 'POST': #If the user has submitted the registration form
        form = RegisterForm(request.POST) #Fill the form with information the user just submitted
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password1']) #Hashes the password for security
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            # if email == "":
            #     messages.error(request, "Email is required")
            #     conn.close()
            #     return render(request, "register_page.html", {"form": form})
            cursor.execute("SELECT id FROM users WHERE username=? OR email=?", (username, email)) #SQL code
            existing_user=cursor.fetchone()

            if existing_user:
                messages.error(request, "Username or email already exists")
                conn.close()
                return render(request, "register_page.html", {"form": form})
                
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password, email)
            ) #If no existing user found, insert a new row into the database
    
            conn.commit()
            cursor.close()
            messages.success(request, "Account created successfully")
            list(messages.get_messages(request))
            request.session["username"] = username #Logs the newly registered user in
            return redirect("dashboard:dashboard") #redirects to the dashboard after account is successfully created
        
        else:
            return render(request, 'register_page.html', {'form': form})
            

def sign_in(request):
    list(messages.get_messages(request))
    if request.method == 'GET':
        try:
            if request.session["username"] is not None:
                return redirect("dashboard:dashboard")
        except:
            form = LoginForm() #Creates an empty login form
            return render(request,'login_page.html', {'form': form})
    
    elif request.method == 'POST': #If the user has submitted the login form
        form = LoginForm(request.POST)
        
        if form.is_valid(): #Checks if the form's data is valid
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()

            cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
            stored_hash=cursor.fetchone()
            if not stored_hash:
                messages.error(request, "Username does not exist, please try again!") #If user enters a username that hasn't been registered onto the system
                conn.close()
                return render(request, "login_page.html", {"form": form})
            if check_password(password, stored_hash[0]): #Checks if the entered password corresponds to the stored hash
                request.session["username"] = username
                return redirect("dashboard:dashboard")
            else:
                messages.error(request,"Invalid password, please try again!") #If user enters a valid username but incorrect password
        
        # messages.error(request,"Invalid password")
        return render(request,'login_page.html',{'form': form})
        
    
def sign_out(request):
    request.session.flush()
    return redirect("/") #redirects to the homepage after you sign out