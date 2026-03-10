from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password, check_password
from .forms import LoginForm, RegisterForm
import sqlite3

def sign_up(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})    
   
    if request.method == 'POST':
        form = RegisterForm(request.POST) 
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = make_password(form.cleaned_data['password1'])
            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM users WHERE username=? OR email=?", (username, email))
            existing_user=cursor.fetchone()
            if existing_user:
                messages.error(request, "Username or email already exists")
                conn.close()
                return render(request, "register.html", {"form": form})
            cursor.execute(
                "INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                (username, password, email)
            )
    
            conn.commit()
            cursor.close()
            messages.success(request, "Account created successfully")
            return redirect("users:sign_in")
            #user should be stored in the database
        else:
            return render(request, 'register.html', {'form': form})

def sign_in(request):

    if request.method == 'GET':
        form = LoginForm()
        return render(request,'login.html', {'form': form})
    
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
                messages.error(request, "Username does not exist")
                conn.close()
                return render(request, "login.html", {"form": form})
            if check_password(password, stored_hash[0]):
                messages.success(request, "Logged in successfully")
                return redirect("/myapp/")

            #should be checked if user is in databasse
        
        messages.error(request,"Invalid password")
        return render(request,'login.html',{'form': form})
    
def sign_out(request):
    logout(request)
    messages.success(request,f'You have been logged out.')
    return redirect('login') 