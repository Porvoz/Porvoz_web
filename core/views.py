from django.shortcuts import render


def dashboard(request):
    return render(request, "dashboard.html")


def contacts_page(request):
    return render(request, "contacts/list.html")


def reminders_page(request):
    return render(request, "reminders/list.html")


def calls_page(request):
    return render(request, "calls/list.html")
