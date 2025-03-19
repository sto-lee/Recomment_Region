from .forms import RecommendationForm
from django.shortcuts import render, redirect
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib.auth.models import User
from .models import Profile
import json
import requests

def login_view(request):
    """로그인 페이지 렌더링"""
    return render(request, 'login/login.html')

def login_process(request):
    """로그인 처리 로직"""
    if request.method == "POST":
        data = json.loads(request.body)
        login_method = data.get("login_method", "")

        # ✅ 로그인 성공 처리 (가짜 로그인)
        request.session['is_logged_in'] = True
        request.session['login_method'] = login_method  # 카카오 or 구글 저장

        # ✅ "next" 값 확인 후 해당 페이지로 이동
        next_url = request.GET.get("next", request.META.get("HTTP_REFERER", "/"))
        return redirect(next_url)

    return JsonResponse({"error": "Invalid request"}, status=400)

def logout_view(request):
    """로그아웃 처리"""
    request.session.flush()
    logout(request)
    return redirect('home')

def kakao_login(request):
    """카카오 로그인 URL로 리디렉트"""
    kakao_auth_url = f"{settings.KAKAO_AUTH_URL}?client_id={settings.KAKAO_REST_API_KEY}&redirect_uri={settings.KAKAO_REDIRECT_URI}&response_type=code"
    return redirect(kakao_auth_url)

def kakao_callback(request):
    code = request.GET.get("code")
    
    # 토큰 받기
    token_request = requests.post(
        settings.KAKAO_TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        },
    )
    
    token_json = token_request.json()
    access_token = token_json.get("access_token")
    
    if not access_token:
        return redirect('home')
        
    # 사용자 정보 받기
    profile_request = requests.get(
        settings.KAKAO_USER_INFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    profile_json = profile_request.json()
    
    # 카카오 계정 정보 추출
    kakao_account = profile_json.get("kakao_account")
    profile = kakao_account.get("profile")
    
    nickname = profile.get("nickname", "")
    profile_image = profile.get("profile_image_url", "")
    kakao_id = str(profile_json.get('id'))
    
    # 먼저 User 모델에서 사용자 찾기 또는 생성
    try:
        user = User.objects.get(username=f"kakao_{kakao_id}")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=f"kakao_{kakao_id}",
            email=kakao_account.get('email', ''),
            password=None
        )
    
    # Profile 모델에서 프로필 찾기 또는 생성
    try:
        profile_obj = Profile.objects.get(user=user)
        # 프로필 정보 업데이트
        profile_obj.nickname = nickname
        profile_obj.image_link = profile_image
        profile_obj.save()
    except Profile.DoesNotExist:
        profile_obj = Profile.objects.create(
            user=user,
            nickname=nickname,
            image_link=profile_image
        )
    
    # 로그인 처리 및 세션 정보 설정
    login(request, user)
    request.session['is_logged_in'] = True
    request.session['login_method'] = 'kakao'
    request.session['nickname'] = nickname
    request.session.save()
    
    return redirect('home')

def home_view(request):
    context = {
        'user': request.user,  # 현재 로그인한 사용자 정보
    }
    return render(request, 'home/home.html', context)