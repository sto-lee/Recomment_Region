from django.shortcuts import render, redirect
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
import json
import requests

def writepost_view(request):
    return render(request, 'community/writepost.html')

def comment_view(request):
    return render(request, 'community/comment.html')

def community_view(request):
    posts = [
        {
            "id": 1,
            "author": "사용자1",
            "title": "첫 번째 게시글",
            "likes": 15,
            "comments": 3,
            "bookmarks": 5,
            "created_at": datetime(2025, 2, 14, 14, 30),
        },
        {
            "id": 2,
            "author": "사용자2",
            "title": "두 번째 게시글",
            "likes": 7,
            "comments": 1,
            "bookmarks": 2,
            "created_at": datetime(2025, 2, 13, 12, 45),
        },
    ]
    return render(request, "community/community.html", {"posts": posts})