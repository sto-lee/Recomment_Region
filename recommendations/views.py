from .forms import RecommendationForm
from django.shortcuts import render, redirect
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
import json
import requests
from .models import RecommendationInput, RecommendationResult

# Create your views here.
# 서울시 구/동 데이터
SEOUL_DISTRICTS = {
    "강남구": ["개포1동","개포2동","개포3동","개포4동", "논현1동","논현2동", "대치1동","대치2동","대치4동", 
                "도곡1동","도곡2동", "삼성1동","삼성2동","세곡동","일원본동","일원1동", "수서동",
                "신사동", "압구정동", "역삼1동","역삼2동", "청담동"],
    "강동구": ["강일동", "고덕1동","고덕2동", "길동", "둔촌1동","둔촌2동", "명일1동", "명일2동", "상일1동", "상일2동", 
                "성내1동", "성내2동", "성내3동", "암사1동", "암사2동", "암사3동", "천호1동", "천호2동", "천호3동"],
    "강북구": ["미아동", "번1동", "번2동", "번3동", "수유1동", "수유2동", "수유3동", "우이동", "인수동", "삼양동", "송중동",
                "송천동", "삼각산동"],
    "강서구": ["가양1동","가양2동","가양3동", "공항동", "발산1동", "등촌1동", "등촌2동", "등촌3동", "방화1동","방화2동","방화3동",
                "염창동", "화곡본동", "화곡1동","화곡2동","화곡3동","화곡4동","화곡6동","화곡8동","우장산동"],
    "관악구": ["남현동","은천동","성현동","보라매","청림동","행운동","낙성대동","중앙동","인헌동","서원동","신원동",
                "봉천동", "신림동", "난향동", "조원동", "대학동", "삼성동", "미성동", "난곡동","서림동","신사동"],
    "광진구": ["광장동", "구의1동","구의2동","구의3동", "군자동", "능동", "화양동","중곡1동","중곡2동","중곡3동","중곡4동",
                "자양1동","자양2동","자양3동","자양4동",],   
    "구로구": ["개봉1동","개봉2동","개봉3동", "고척1동","고척2동", "구로1동","구로2동","구로3동","구로4동","구로5동", "신도림동","가리봉동",
                "오류1동","오류2동","항동","수궁동"],
    "금천구": ["가산동", "독산1동","독산2동","독산3동","독산4동", "시흥1동","시흥2동","시흥3동","시흥4동","시흥5동"],
    "노원구": ["공릉1동","공릉2동","하계1동","하계2동","중계본동","중계1동","중계2,3동","중계4동", "상계1동","상계2동","상계3,4동",
                "상계5동","상계6,7동","상계8동","상계9동","상계10동", "월계1동","월계2동","월계3동"],
    "도봉구": ["도봉1동","도봉2동", "방학1동","방학2동","방학3동", "쌍문1동","쌍문2동","쌍문3동","쌍문4동", "창1동","창2동",
                "창3동","창4동","창5동"],
    "동대문구": ["제기동","답십리1동","답십리2동", "신설동", "용신동", "이문1동","이문2동", "장안1동","장안2동", "전농1동","전농2동", "청량리동"
                "회기동", "휘경1동","휘경2동"],
    "동작구": ["노량진1동","노량진2동", "대방동", "사당1동","사당2동","사당3동","사당4동", "상도1동","상도2동","상도3동","상도4동",
                "신대방1동","신대방2동", "흑석동"],
    "마포구": ["아현동","공덕동","도화동","용강동","대흥동","염리동","신수동","서강동","합정동","연남동", "망원1동","망원2동",
                "상암동", "서교동", "성산1동","성산2동", "합정동"],
    "서대문구": ["충현동","천연동","남가좌1동","남가좌2동", "북가좌1동","북가좌2동", "북아현동", "신촌동", "연희동", "홍제1동","홍제2동","홍제3동",
                "홍은1동","홍은2동"],
    "서초구": ["반포본동","반포1동","반포2동","반포3동","반포4동", "방배본동","방배1동","방배2동","방배3동","방배4동",
                "서초1동","서초2동","서초3동","서초4동", "양재1동","양재2동", "잠원동", "내곡동"],
    "성동구": ["사근동","행당1동","행당2동","응봉동","금호1가동","금호2,3가동","금호4가동", "도선동", "마장동", "송정동", "용답동",
                "성수1가1동","성수1가2동","성수2가1동","성수2가3동", "옥수동", "왕십리2동","왕십리도선동"],
    "성북구": ["안암동","길음1동","길음2동", "돈암1동","돈암2동", "동선동", "보문동", "삼선동", "석관동", "성북동", "장위1동","장위2동","장위3동",
                "정릉1동","종암동","정릉2동","정릉3동","정릉4동","월곡1동","월곡2동"],
    "송파구": ["풍납1동","풍납2동","방이1동","방이2동","가락본동","가락1동","가락2동", "거여1동","거여2동", "마천1동","마천2동", "문정1동","문정2동", 
                "석촌동","삼전동","송파1동","송파2동", "오금동","오륜동", "장지동","위례동","잠실본동","잠실2동","잠실3동","잠실4동",
                "잠실6동","잠실7동"],
    "양천구": ["목1동","목2동","목3동","목4동","목5동", "신월1동","신월2동","신월3동","신월4동","신월5동","신월6동","신월7동", 
                "신정1동","신정2동","신정3동","신정4동","신정5동","신정6동","신정7동"],
    "영등포구": ["영등포본동","영등포동","당산1동","당산2동", "대림1동","대림2동","대림3동", "도림동", "문래동", "양평1동","양평2동", "여의동",
                "신길1동","신길2동","신길3동","신길4동","신길5동","신길6동","신길7동"],
    "용산구": ["후암동","용산2가동","남영동", "보광동","청파동","원효로1동","원효로2동","효창동","용문동", "서빙고동", "이태원1동","이태원2동",
                "한강로동","이촌1동","이촌2동","한남동"],
    "은평구": ["갈현1동","갈현2동", "구산동", "녹번동","대조동","응암1동","응암2동","응암3동", "불광1동","불광2동", "수색동", 
                "신사1동","신사2동","증산동", "역촌동","진관동"],
    "종로구": ["청운효자동","삼청동","평창동","가회동", "교남동", "낙원동", "내자동", "무악동", "부암동", "사직동", "창신1동","창신2동","창신3동",
                "종로1.2.3.4가동","종로5,6가동","이화동","혜화동","숭인1동","숭인2동"],
    "중구": ["회현동","명동","필동","장충동","광희동","약수동","남대문로", "다산동", "만리동", "묵정동", "소공동", "신당동","신당5동", 
                "을지로동","청구동","동화동","황학동","중림동"],
    "중랑구": ["망우3동","망우본동", "면목본동","면목2동","면목3.8동","면목4동","면목5동","면목7동", "상봉1동","상봉2동", "중화1동","중화2동",
                "묵1동","묵2동","신내1동","신내2동"]
}

def get_dongs(request):
    district = request.GET.get("district", "")
    dongs = SEOUL_DISTRICTS.get(district, [])
    return JsonResponse({"dongs": dongs})

def recommendations_view(request):
    print("📌 recommendations_view() 실행됨!")  # ✅ 디버깅 로그 추가
    districts_list = list(SEOUL_DISTRICTS.keys())
    print("📌 recommendations_view()에서 전달되는 districts 리스트:", districts_list)  # ✅ 로그 추가

    return render(request, "recommendations/recommend_page_1.html", {
        'districts': districts_list  # ✅ districts 리스트 추가
    })

def recommend_view(request):  # recommend_page_2
    if request.method == 'POST':
        # recommend_page_1에서 전달된 데이터 처리
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        preferred_facilities = request.POST.get('preferred_facilities')
        desired_district = request.POST.get('desired_district', "").strip()
        transport = request.POST.get('transport')
        desired_dong = request.POST.get('desired_dong', "").strip()

        # 필수 입력값 검증
        if not all([age, gender, preferred_facilities, desired_district]):
            return redirect('recommendations:recommend_page_1')

        # 세션에 데이터 저장
        request.session['age'] = age
        request.session['gender'] = gender
        request.session['preferred_facilities'] = preferred_facilities
        request.session['desired_district'] = desired_district
        request.session['transport'] = transport
        request.session['desired_dong'] = desired_dong

        # recommend_page_2 렌더링
        context = {
            "age": age,
            "gender": gender,
            "preferred_facilities": preferred_facilities,
            "transport": transport,
            "desired_district": desired_district,
            "desired_dong": desired_dong,
        }
        return render(request, 'recommendations/recommend_page_2.html', context)

    return render(request, 'recommendations/recommend_page_2.html')

def recommend_result_view(request):
    # POST로 전달된 데이터와 세션 데이터 모두 가져오기
    user_data = {
        'age': int(request.session.get('age')),
        'gender': request.session.get('gender'),
        'preferred_facilities': request.session.get('preferred_facilities').split(','),
        'transport': request.session.get('transport'),
        'desired_district': request.session.get('desired_district'),
        'desired_dong': request.session.get('desired_dong'),
        'property_type': request.POST.get('property_type'),
        'crime_sensitivity': int(request.POST.get('crime_sensitivity', 0)),
        
        # 시세 정보 (전세)
        'jeonse_deposit_min': request.POST.get('jeonse_deposit_min'),
        'jeonse_deposit_max': request.POST.get('jeonse_deposit_max'),
        
        # 시세 정보 (월세)
        'monthly_deposit_min': request.POST.get('monthly_deposit_min'),
        'monthly_deposit_max': request.POST.get('monthly_deposit_max'),
        'monthly_rent_min': request.POST.get('monthly_rent_min'),
        'monthly_rent_max': request.POST.get('monthly_rent_max'),
        
        # 추천 유형
        'recommendation_type': request.POST.get('recommendation_type', 'facility'),
        
        # 사용자 지정 가중치
        'custom_facility_weight': request.POST.get('custom_facility_weight'),
        'custom_crime_weight': request.POST.get('custom_crime_weight'),
        'custom_price_weight': request.POST.get('custom_price_weight'),
        'custom_population_weight': request.POST.get('custom_population_weight'),
    }

    # RecommendationInput 객체 생성
    recommendation_input = RecommendationInput.objects.create(
        age=user_data['age'],
        gender=user_data['gender'],
        transport=user_data['transport'],
        preferred_facilities=user_data['preferred_facilities'],  # facility -> preferred_facilities
        property_type=user_data['property_type'],
        desired_location=f"{user_data['desired_district']} {user_data['desired_dong']}".strip(),
        crime_sensitivity=user_data['crime_sensitivity'],
        
        # 시세 정보 (전세)
        jeonse_deposit_min=user_data['jeonse_deposit_min'] or None,
        jeonse_deposit_max=user_data['jeonse_deposit_max'] or None,
        
        # 시세 정보 (월세)
        monthly_deposit_min=user_data['monthly_deposit_min'] or None,
        monthly_deposit_max=user_data['monthly_deposit_max'] or None,
        monthly_rent_min=user_data['monthly_rent_min'] or None,
        monthly_rent_max=user_data['monthly_rent_max'] or None,
        
        # 추천 유형
        recommendation_type=user_data['recommendation_type'],
        
        # 사용자 지정 가중치 (custom 타입일 때만)
        custom_facility_weight=float(user_data['custom_facility_weight']) if user_data['custom_facility_weight'] else None,
        custom_crime_weight=float(user_data['custom_crime_weight']) if user_data['custom_crime_weight'] else None,
        custom_price_weight=float(user_data['custom_price_weight']) if user_data['custom_price_weight'] else None,
        custom_population_weight=float(user_data['custom_population_weight']) if user_data['custom_population_weight'] else None
    )

    # 추천 결과 생성
    recommendations = RecommendationResult.create_recommendation(recommendation_input)

    # 추천 결과를 위도/경도 리스트로 변환
    recommended_locations = [
        {
            'lat': rec.cluster_lat,
            'lng': rec.cluster_lng,
            'district': rec.recommended_district,
            'score': rec.recommendation_score
        } for rec in recommendations
    ]

    return render(request, 'recommendations/result_recommend.html', {
        'recommendations': recommended_locations
    })