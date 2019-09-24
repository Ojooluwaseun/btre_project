import json
import urllib
from .decorators import check_recaptcha

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from contacts.models import Contact

@check_recaptcha
def register(request):
    if request.method == 'POST':
        #register user
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        #check if password match
        if password == password2:
            #check username
            if User.objects.filter(username=username).exists():
               messages.error(request, 'Username already exist')
               return redirect('register')
            else:
                #check email
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Email already exist')
                    return redirect('register')
                else:
                    if request.recaptcha_is_valid:
                        user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                        #login after register
                        # auth.login(request, user)
                        # return redirect('index')
                        # messages.success(request, 'You are now logged in')

                        user.save()
                        messages.success(request, 'You are registered, You can now login')
                        return redirect('login')
                    else:
                        return redirect('register')
        else:
            messages.error(request, 'Password does not match')
            return redirect('register')
    else:
        return render(request, 'accounts/register.html')

@check_recaptcha
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if request.recaptcha_is_valid:
                auth.login(request, user)
                messages.success(request, 'You are now logged in')
                return redirect('dashboard')
            else:
                return redirect('login')
            
        else:
            messages.error(request, 'Invalid Username or Password')
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')


def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, 'You are now logged out')
        return redirect('index')

def dashboard(request):
    user_contact = Contact.objects.order_by('-contact_date').filter(user_id=request.user.id)

    context = {
        'contacts' : user_contact
    }
    return render(request, 'accounts/dashboard.html', context)