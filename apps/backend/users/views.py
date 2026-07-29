import time

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password, check_password
from .forms import LoginForm, RegisterForm
import sqlite3

def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register_page.html', {'form': form})    
   
    if request.method == 'POST':
        form = RegisterForm(request.POST) 
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password1'])
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()
            if email == "":
                messages.error(request, "Email is required")
                conn.close()
                return render(request, "register_page.html", {"form": form})
            cursor.execute("SELECT id FROM users WHERE username=? OR email=?", (username, email))
            existing_user=cursor.fetchone()
            if existing_user:
                messages.error(request, "Username or email already exists")
                conn.close()
                return render(request, "register_page.html", {"form": form})
                
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password, email)
            )
    
            conn.commit()
            cursor.close()
            messages.success(request, "Account created successfully")
            list(messages.get_messages(request))
            request.session["username"] = username
            return redirect("dashboard:dashboard") #redirects to the dashboard after account is successfully created
        
        else:
            return render(request, 'register_page.html', {'form': form})
            

def sign_in(request):
    list(messages.get_messages(request))
    if request.method == 'GET':
        form = LoginForm()
        return render(request,'login_page.html', {'form': form})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()

            cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
            stored_hash=cursor.fetchone()
            if not stored_hash:
                messages.error(request, "Username does not exist, please try again!")
                conn.close()
                return render(request, "login_page.html", {"form": form})
            if check_password(password, stored_hash[0]):
                request.session["username"] = username
                # return render(request, 'home_page.html')
                return render(request, 'dashboard_page.html')

            #should be checked if user is in databasse
        
        messages.error(request,"Invalid password")
        return render(request,'login_page.html',{'form': form})
        
    
def sign_out(request):
    request.session.flush()
    return redirect("/") #redirects to the homepage after you sign out