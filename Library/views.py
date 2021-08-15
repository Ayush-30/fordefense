from django.shortcuts import render


def library(request):
    return render(request, 'library/library.html')
def navbar(request):
    return render(request, 'library/navbar.html')
def comp1(request):
    return render(request, 'library/contenttrial2.html')
def error(request):
    return render(request, 'library/error404.html')