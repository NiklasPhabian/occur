from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def sign_up(request):
    if request.method == "POST":
        username = request.POST['user']
        password = request.POST['password']
        context = {}
        try:
            User.objects.get(username=username)
            context['error'] = 'User already exists'
        except User.DoesNotExist:
            User.objects.create_user(username=username, password=password, email=None, first_name='', last_name='')
            context['success'] = True
            user = authenticate(request, username=username, password=password)
            logout(request)
            login(request, user)
        return render(request=request, template_name='accounts/signup.html', context=context)
    else:
        return render(request=request, template_name='accounts/signup.html')


def log_in(request):
    context = {}
    if request.method == "POST":
        username = request.POST['user']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            logout(request)
            login(request, user)
            if 'next' in request.POST:
                return redirect(request.POST['next'])
            else:
                context = {'username': username}
                return render(request, template_name='accounts/loggedin.html', context=context)
        else:
            context['error'] = 'No user-password match found'
            return render(request, template_name='accounts/login.html', context=context)

    else:
        return render(request=request, template_name='accounts/login.html')


def log_out(request):
    logout(request)
    return render(request=request, template_name='accounts/logout.html')
