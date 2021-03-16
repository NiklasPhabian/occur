from django.shortcuts import render


def home(request):
    return render(request, 'sitepages/home.html')


def about(request):
    return render(request, 'sitepages/about.html')



