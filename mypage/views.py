from django.shortcuts import render, redirect
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
import json
import requests

def mypage_view(request):
    return render(request, 'mypage/mypage.html')

def myprofile_view(request):
    return render(request, 'mypage/myprofile.html')

def mybookmarks_view(request):
    return render(request, 'mypage/mybookmarks.html')

def myposts_view(request):
    return render(request, 'mypage/myposts.html')
