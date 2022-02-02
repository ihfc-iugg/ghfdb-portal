from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def why_register(request):
    return render(request, 'dashboard/why_register.html')

